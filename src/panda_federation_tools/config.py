"""Settings read from environment variables. The Apify token is never logged or returned."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field

log = logging.getLogger("panda_federation_tools")

DEFAULT_TIMEOUT_SECS = 120
MAX_TIMEOUT_SECS = 300  # Apify run-sync endpoints wait at most 300 s.
DEFAULT_MAX_ITEMS = 50
MAX_ITEMS = 1000
DEFAULT_MAX_CHARGE_USD = 0.50
MAX_CHARGE_USD = 25.0


def _num(name: str, default: float, lo: float, hi: float) -> float:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        value = float(raw)
    except ValueError:
        value = float("nan")
    if value != value or value in (float("inf"), float("-inf")):  # not a finite number
        log.warning("%s must be a number between %g and %g; using the default %g", name, lo, hi, default)
        return default
    return min(max(value, lo), hi)


@dataclass(frozen=True)
class Settings:
    token: str = field(default="", repr=False)
    api_base: str = "https://api.apify.com"
    timeout_secs: int = DEFAULT_TIMEOUT_SECS
    max_items: int = DEFAULT_MAX_ITEMS
    max_charge_usd: float = DEFAULT_MAX_CHARGE_USD

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            token=os.environ.get("APIFY_TOKEN", "").strip(),
            timeout_secs=int(_num("PANDA_TIMEOUT_SECS", DEFAULT_TIMEOUT_SECS, 10, MAX_TIMEOUT_SECS)),
            max_items=int(_num("PANDA_MAX_ITEMS", DEFAULT_MAX_ITEMS, 1, MAX_ITEMS)),
            max_charge_usd=_num("PANDA_MAX_CHARGE_USD", DEFAULT_MAX_CHARGE_USD, 0.01, MAX_CHARGE_USD),
        )
