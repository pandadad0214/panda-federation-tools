"""Minimal async client for Apify's run-sync-get-dataset-items endpoint."""

from __future__ import annotations

import asyncio
import re
from typing import Any

import httpx2 as httpx

from panda_federation_tools import __version__

# Only retry when we know no Actor run was started, so a retry can never double-charge:
# 429 (request rejected by the rate limiter) and connection failures (request never sent).
RETRY_STATUSES = {429}
MAX_ATTEMPTS = 2
_TOKEN_RE = re.compile(r"apify_api_[A-Za-z0-9]+")


class ApifyError(Exception):
    """An error safe to show to the user or agent (contains no secrets)."""


def redact(text: str, token: str = "") -> str:
    if token:
        text = text.replace(token, "[REDACTED]")
    return _TOKEN_RE.sub("[REDACTED]", text)


def _error_message(resp: httpx.Response) -> str:
    try:
        err = resp.json().get("error") or {}
        return str(err.get("message") or err.get("type") or "")
    except (ValueError, AttributeError):
        return ""


class ApifyClient:
    def __init__(
        self,
        token: str,
        *,
        api_base: str = "https://api.apify.com",
        transport: httpx.AsyncBaseTransport | None = None,
        retry_delay: float = 1.0,
    ) -> None:
        self._token = token
        self._api_base = api_base.rstrip("/")
        self._transport = transport
        self._retry_delay = retry_delay

    def __repr__(self) -> str:  # never show the token
        return f"ApifyClient(api_base={self._api_base!r})"

    async def run_actor(
        self, actor: str, run_input: dict[str, Any], *, timeout_secs: int, max_items: int, max_charge_usd: float
    ) -> list[dict[str, Any]]:
        if not self._token:
            raise ApifyError(
                "APIFY_TOKEN is not set. Add your Apify API token (https://console.apify.com/settings/integrations) "
                "to this MCP server's environment and restart it."
            )
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_-]*", actor):
            raise ApifyError(f"Invalid Actor id: {actor!r}")
        url = f"{self._api_base}/v2/acts/{actor.replace('/', '~')}/run-sync-get-dataset-items"
        params: dict[str, str | int | float] = {
            "timeout": timeout_secs,
            "maxItems": max_items,
            "limit": max_items,  # dataset items returned to the caller
            "maxTotalChargeUsd": max_charge_usd,
            "format": "json",
            "clean": 1,
        }
        headers = {
            "Authorization": f"Bearer {self._token}",
            "User-Agent": f"panda-federation-tools/{__version__}",
        }
        timeout = httpx.Timeout(timeout_secs + 30, connect=15)
        async with httpx.AsyncClient(transport=self._transport, timeout=timeout) as http:
            for attempt in range(1, MAX_ATTEMPTS + 1):
                try:
                    resp = await http.post(url, params=params, json=run_input, headers=headers)
                except httpx.TimeoutException as exc:
                    if isinstance(exc, httpx.ConnectTimeout) and attempt < MAX_ATTEMPTS:
                        await asyncio.sleep(self._retry_delay)
                        continue
                    raise ApifyError(
                        f"Timed out after {timeout_secs}s waiting for {actor}. "
                        "Try a smaller input or a larger run_timeout_secs (max 300)."
                    ) from exc
                except httpx.ConnectError as exc:
                    if attempt < MAX_ATTEMPTS:
                        await asyncio.sleep(self._retry_delay)
                        continue
                    raise ApifyError(f"Could not connect to Apify: {redact(type(exc).__name__, self._token)}") from exc
                except httpx.HTTPError as exc:
                    # The request may have reached Apify and started a run; do not retry (no double charge).
                    raise ApifyError(
                        f"Network error calling Apify ({redact(type(exc).__name__, self._token)}). "
                        "Check your Apify Console before retrying: the run may have started."
                    ) from exc
                if resp.status_code in RETRY_STATUSES and attempt < MAX_ATTEMPTS:
                    await asyncio.sleep(self._retry_delay * attempt)
                    continue
                return self._handle(resp, actor, timeout_secs)
        raise ApifyError("Apify request failed.")  # pragma: no cover

    def _handle(self, resp: httpx.Response, actor: str, timeout_secs: int) -> list[dict[str, Any]]:
        status = resp.status_code
        detail = redact(_error_message(resp), self._token)
        if 200 <= status < 300:
            try:
                data = resp.json()
            except ValueError as exc:
                raise ApifyError("Apify returned a response that is not JSON.") from exc
            if not isinstance(data, list):
                raise ApifyError("Apify returned an unexpected response shape.")
            return [d if isinstance(d, dict) else {"value": d} for d in data]
        if status == 400:
            raise ApifyError(f"{actor} rejected the input: {detail or 'invalid input'}")
        if status in (401, 403):
            raise ApifyError("Apify rejected the token (check APIFY_TOKEN and its permissions).")
        if status == 402:
            raise ApifyError("Your Apify account is out of credit or over its usage limit.")
        if status == 404:
            raise ApifyError(f"Actor {actor} was not found on Apify.")
        if status == 408:
            raise ApifyError(
                f"{actor} did not finish within {timeout_secs}s and was stopped. Narrow the input or raise "
                "run_timeout_secs (max 300). Results found before the stop are in the run's dataset "
                "in your Apify Console."
            )
        if status == 429:
            raise ApifyError("Apify rate limit reached. Wait a moment and try again.")
        raise ApifyError(f"Apify error {status}: {detail or 'unexpected error'}")
