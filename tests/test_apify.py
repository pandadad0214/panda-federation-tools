import json

import httpx2 as httpx
import pytest

from panda_federation_tools.apify import ApifyClient, ApifyError, redact

TOKEN = "apify_api_TESTTOKEN123"


def client(handler):
    return ApifyClient(TOKEN, transport=httpx.MockTransport(handler), retry_delay=0)


async def run(c, **kw):
    return await c.run_actor(
        "pandadad0214/reference-checker",
        {"dois": ["10.1/x"]},
        timeout_secs=kw.get("timeout", 60),
        max_items=5,
        max_charge_usd=0.25,
    )


async def test_success_sends_token_in_header_only():
    seen = {}

    def handler(request):
        seen["url"] = str(request.url)
        seen["auth"] = request.headers["authorization"]
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json=[{"status": "OK"}, 3])

    items = await run(client(handler))
    assert items == [{"status": "OK"}, {"value": 3}]
    assert seen["auth"] == f"Bearer {TOKEN}"
    assert TOKEN not in seen["url"]
    assert "/v2/acts/pandadad0214~reference-checker/run-sync-get-dataset-items" in seen["url"]
    assert "maxItems=5" in seen["url"] and "maxTotalChargeUsd=0.25" in seen["url"]
    assert seen["body"] == {"dois": ["10.1/x"]}


async def test_missing_token():
    c = ApifyClient("", transport=httpx.MockTransport(lambda r: httpx.Response(200, json=[])))
    with pytest.raises(ApifyError, match="APIFY_TOKEN is not set"):
        await run(c)


@pytest.mark.parametrize(
    ("status", "pattern"),
    [
        (400, "rejected the input: bad field"),
        (401, "rejected the token"),
        (402, "out of credit"),
        (404, "not found"),
        (408, "did not finish within 60s"),
        (429, "rate limit"),
        (500, "Apify error 500"),
    ],
)
async def test_error_mapping(status, pattern):
    def handler(request):
        return httpx.Response(status, json={"error": {"message": f"bad field {TOKEN}"}})

    with pytest.raises(ApifyError, match=pattern) as info:
        await run(client(handler))
    assert TOKEN not in str(info.value)


async def test_retries_once_on_429():
    calls = []

    def handler(request):
        calls.append(1)
        return httpx.Response(429) if len(calls) == 1 else httpx.Response(200, json=[])

    assert await run(client(handler)) == []
    assert len(calls) == 2


@pytest.mark.parametrize("status", [500, 502, 503, 504])
async def test_never_retries_5xx_so_runs_are_not_double_charged(status):
    calls = []

    def handler(request):
        calls.append(1)
        return httpx.Response(status)

    with pytest.raises(ApifyError):
        await run(client(handler))
    assert len(calls) == 1


async def test_retries_connection_failures_once():
    calls = []

    def handler(request):
        calls.append(1)
        if len(calls) == 1:
            raise httpx.ConnectError("refused", request=request)
        return httpx.Response(200, json=[{"a": 1}])

    assert await run(client(handler)) == [{"a": 1}]
    assert len(calls) == 2


async def test_does_not_retry_after_request_was_sent():
    calls = []

    def handler(request):
        calls.append(1)
        raise httpx.ReadError(f"reset {TOKEN}", request=request)

    with pytest.raises(ApifyError, match="may have started") as info:
        await run(client(handler))
    assert len(calls) == 1
    assert TOKEN not in str(info.value)


async def test_gives_up_after_two_connection_failures():
    def handler(request):
        raise httpx.ConnectError("refused", request=request)

    with pytest.raises(ApifyError, match="Could not connect"):
        await run(client(handler))


async def test_invalid_json_body():
    with pytest.raises(ApifyError, match="not JSON"):
        await run(client(lambda r: httpx.Response(200, content=b"<html>")))


async def test_timeout_is_reported():
    def handler(request):
        raise httpx.ReadTimeout("slow", request=request)

    with pytest.raises(ApifyError, match="Timed out"):
        await run(client(handler))


async def test_non_list_response():
    with pytest.raises(ApifyError, match="unexpected response"):
        await run(client(lambda r: httpx.Response(200, json={"a": 1})))


def test_redact_and_repr():
    assert "TESTTOKEN" not in redact(f"x {TOKEN} y apify_api_other", TOKEN)
    assert TOKEN not in repr(ApifyClient(TOKEN))


async def test_rejects_bad_actor_id():
    with pytest.raises(ApifyError, match="Invalid Actor id"):
        await ApifyClient(TOKEN).run_actor("../etc", {}, timeout_secs=10, max_items=1, max_charge_usd=0.1)
