import json
import sys

import anyio
import pytest
from mcp import Client

from panda_federation_tools import server as server_module
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
    assert run_input == {"dois": ["10.1038/nature14539"], "maxReferences": 3}
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


def test_bad_env_numbers_fall_back_to_defaults(monkeypatch):
    for value in ("abc", "nan", "inf"):
        monkeypatch.setenv("PANDA_MAX_CHARGE_USD", value)
        monkeypatch.setenv("PANDA_MAX_ITEMS", value)
        s = Settings.from_env()
        assert s.max_charge_usd == 0.5 and s.max_items == 50


async def test_large_results_are_truncated_to_valid_json():
    items = [{"summary": "x" * 1000, "n": i} for i in range(200)]
    async with Client(server_with(FakeClient(items=items))) as c:
        r = await c.call_tool("topic_trends_tracker", {})
    assert not r.is_error
    text = r.content[0].text
    assert len(text) <= server_module.MAX_TEXT_CHARS
    payload = json.loads(text)  # still valid JSON
    assert payload["count"] == 200 and 0 < len(payload["items"]) < 200
    assert "structuredContent" in payload["truncated"]
    assert len(r.structured_content["items"]) == 200


class SlowClient(FakeClient):
    async def run_actor(self, actor, run_input, **kw):
        await anyio.sleep(0.2)
        return [{"ok": True}]


async def test_long_runs_send_progress_notifications(monkeypatch):
    monkeypatch.setattr(server_module, "HEARTBEAT_SECS", 0.05)
    seen = []

    async def on_progress(progress, total, message):
        seen.append((progress, total, message))

    async with Client(server_with(SlowClient())) as c:
        r = await c.call_tool("topic_trends_tracker", {"run_timeout_secs": 60}, progress_callback=on_progress)
    assert not r.is_error
    assert seen and seen[0][1] == 60 and "running on Apify" in seen[0][2]


async def test_run_options_are_stripped_and_defaults_apply():
    fake = FakeClient()
    settings = Settings(token=TOKEN, timeout_secs=45, max_items=7, max_charge_usd=0.2)
    async with Client(create_server(settings, factory=lambda s: fake)) as c:
        await c.call_tool("topic_trends_tracker", {"topics": ["Python"], "run_max_charge_usd": 0.05})
    _, run_input, kw = fake.calls[0]
    assert run_input == {"topics": ["Python"], "maxTopics": 7}
    assert kw == {"timeout_secs": 45, "max_items": 7, "max_charge_usd": 0.05}


def test_main_prints_version(monkeypatch, capsys):
    from panda_federation_tools import __version__
    from panda_federation_tools.server import main

    monkeypatch.setattr(sys, "argv", ["panda-federation-tools", "--version"])
    main()
    assert capsys.readouterr().out.strip() == __version__


async def test_result_cap_respects_explicit_actor_field_and_schema_limits():
    fake = FakeClient()
    async with Client(server_with(fake)) as c:
        await c.call_tool("literature_search", {"query": "x", "maxResults": 20, "run_max_items": 5})
        await c.call_tool("researcher_expert_finder", {"topic": "x", "run_max_items": 1000})
        await c.call_tool("company_team_finder", {"companies": ["a.com"], "run_max_items": 5})
    assert fake.calls[0][1]["maxResults"] == 20  # caller's own cap wins
    assert fake.calls[1][1]["maxResults"] == 200  # clamped to the Actor's maximum
    assert "maxCompanies" not in fake.calls[2][1]  # cap counts companies, not people: left alone


def test_every_result_cap_field_exists_in_its_actor_schema():
    from panda_federation_tools.catalog import RESULT_CAP_FIELDS

    for tool in load_catalog():
        if tool.name in RESULT_CAP_FIELDS:
            assert tool.result_cap_field == RESULT_CAP_FIELDS[tool.name], tool.name
