import json

import pytest
from mcp import Client

from panda_federation_tools.apify import ApifyError
from panda_federation_tools.catalog import load_catalog
from panda_federation_tools.config import Settings
from panda_federation_tools.server import create_server

TOKEN = "apify_api_SERVERTEST999"


class FakeClient:
    def __init__(self, items=None, error=None):
        self.items = items or []
        self.error = error
        self.calls = []

    async def run_actor(self, actor, run_input, **kw):
        self.calls.append((actor, run_input, kw))
        if self.error:
            raise self.error
        return self.items


def server_with(fake, token=TOKEN):
    return create_server(Settings(token=token), factory=lambda s: fake)


async def test_lists_every_catalog_tool():
    async with Client(server_with(FakeClient())) as c:
        result = await c.list_tools()
    names = {t.name for t in result.tools}
    assert names == {t.name for t in load_catalog()}
    tool = next(t for t in result.tools if t.name == "reference_checker")
    assert tool.annotations.read_only_hint is True
    assert "run_max_charge_usd" in tool.input_schema["properties"]
    assert "apify.com/pandadad0214/reference-checker" in tool.description


async def test_call_passes_input_and_run_options():
    fake = FakeClient(items=[{"summary": "OK: found", "status": "OK"}])
    async with Client(server_with(fake)) as c:
        result = await c.call_tool("reference_checker", {"dois": ["10.1038/nature14539"], "run_max_items": 3})
    assert not result.is_error
    payload = json.loads(result.content[0].text)
    assert payload["count"] == 1 and payload["items"][0]["status"] == "OK"
    actor, run_input, kw = fake.calls[0]
    assert actor == "pandadad0214/reference-checker"
    assert run_input == {"dois": ["10.1038/nature14539"]}
    assert kw["max_items"] == 3 and kw["max_charge_usd"] == 0.5


async def test_invalid_input_is_rejected_before_any_run():
    fake = FakeClient()
    async with Client(server_with(fake)) as c:
        bad_type = await c.call_tool("reference_checker", {"dois": "not-a-list"})
        unknown = await c.call_tool("reference_checker", {"nope": 1})
        too_big = await c.call_tool("reference_checker", {"run_max_charge_usd": 1000})
    for r in (bad_type, unknown, too_big):
        assert r.is_error and "Invalid input" in r.content[0].text
    assert fake.calls == []


async def test_required_inputs_are_enforced():
    fake = FakeClient()
    async with Client(server_with(fake)) as c:
        r = await c.call_tool("grants_finder", {})
    assert r.is_error and "keywords" in r.content[0].text


async def test_empty_result_notes_no_charge():
    async with Client(server_with(FakeClient(items=[]))) as c:
        r = await c.call_tool("topic_trends_tracker", {})
    assert not r.is_error and "not charged per result" in r.content[0].text


@pytest.mark.parametrize("error", [ApifyError(f"boom {TOKEN}"), RuntimeError(f"secret {TOKEN}")])
async def test_errors_never_leak_token(error):
    async with Client(server_with(FakeClient(error=error))) as c:
        r = await c.call_tool("topic_trends_tracker", {})
    assert r.is_error and TOKEN not in r.content[0].text


async def test_unknown_tool():
    async with Client(server_with(FakeClient())) as c:
        r = await c.call_tool("rm_rf", {})
    assert r.is_error


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("APIFY_TOKEN", TOKEN)
    monkeypatch.setenv("PANDA_MAX_CHARGE_USD", "9999")
    monkeypatch.setenv("PANDA_TIMEOUT_SECS", "1")
    s = Settings.from_env()
    assert s.token == TOKEN and s.max_charge_usd == 25.0 and s.timeout_secs == 10
    assert TOKEN not in repr(s)
