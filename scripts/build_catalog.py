#!/usr/bin/env python3
"""Regenerate src/panda_federation_tools/catalog.json from the public Apify Store.

Reads each Actor's public metadata and the input schema of its default build from
the Apify API. No token is needed (all Actors are public). Run it after you publish
or change an Actor, then commit the updated catalog.json:

    python scripts/build_catalog.py
"""

from __future__ import annotations

import html
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

OWNER = "pandadad0214"
# Order here is the order tools are listed by the MCP server.
SLUGS = [
    "reference-checker",
    "citation-formatter",
    "literature-search",
    "pubmed-evidence-table",
    "grants-finder",
    "researcher-expert-finder",
    "pdf-table-extractor",
    "npi-provider-lists",
    "federal-contract-finder",
    "email-domain-security-checker",
    "ai-search-seo-audit",
    "podcast-leads-finder",
    "local-business-leads",
    "company-hiring-signals",
    "company-website-enricher",
    "topic-trends-tracker",
    "company-team-finder",
    "trucking-company-leads",
    "website-change-monitor",
    # Built and tested; skipped automatically until each one is public on the Store.
    "sbir-sttr-topic-radar",
    "sec-financials-excel",
    "hidden-ai-instructions-scanner",
    "clinical-trial-leads",
    "nonprofit-leads-irs",
    "federal-register-monitor",
    "product-recall-monitor",
    "vin-decoder-recalls",
    "building-permit-leads",
    "florida-new-business-leads",
    "bulk-domain-whois-expiry",
    "wayback-snapshot-finder",
    "texas-new-business-leads",
    "h1b-lca-sponsor-leads",
    "new-york-new-business-leads",
    "eu-ted-tenders",
    "broken-link-checker",
]
# Inputs an agent should not pass through a chat transcript, or that only work in the Console.
SKIP_EDITORS = {"fileupload"}
KEEP_KEYS = ("type", "enum", "default", "minimum", "maximum")
OUT = Path(__file__).resolve().parents[1] / "src" / "panda_federation_tools" / "catalog.json"
# MCP tool descriptions (TDQS standard). These replace the Apify Store blurb in tools/list;
# the Store blurb is kept as storeDescription. Every public tool must have an entry here.
DESCRIPTIONS = Path(__file__).resolve().parent / "tool_descriptions.json"
API = "https://api.apify.com/v2/acts/"


def get(url: str) -> dict:
    if not url.startswith(API):
        raise ValueError(url)
    req = urllib.request.Request(  # noqa: S310 (https only, checked above)
        url, headers={"User-Agent": "panda-federation-tools-catalog"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310 (https only, checked above)
        return json.load(r)["data"]


def text(s: str | None) -> str:
    s = re.sub(r"<[^>]+>", "", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def convert_prop(p: dict) -> dict:
    out = {k: p[k] for k in KEEP_KEYS if k in p}
    desc = text(p.get("description"))
    title = text(p.get("title"))
    if p.get("enum") and p.get("enumTitles"):
        choices = "; ".join(f"{v} = {t}" for v, t in zip(p["enum"], p["enumTitles"], strict=False))
        desc = f"{desc} Choices: {choices}."
    out["description"] = f"{title}. {desc}".strip() if title else desc
    if p.get("type") == "array":
        items = dict(p.get("items") or {})
        if p.get("editor") in (None, "stringList") and not items:
            items = {"type": "string"}
        if p.get("editor") == "select" and "enum" in (items or {}):
            items = {"type": "string", "enum": items["enum"]}
        if items:
            out["items"] = {k: v for k, v in items.items() if k in ("type", "enum")}
    ex = p.get("example", p.get("prefill"))
    if ex is not None and p.get("type") != "boolean":
        out["examples"] = [ex]
    return out


def tool_name(slug: str) -> str:
    return slug.replace("-", "_")


def price_lines(act: dict) -> list[dict]:
    infos = act.get("pricingInfos") or []
    if not infos:
        return []
    events = (infos[-1].get("pricingPerEvent") or {}).get("actorChargeEvents") or {}
    out = []
    for name, ev in events.items():
        if name == "apify-actor-start":
            continue
        tier = (ev.get("eventTieredPricingUsd") or {}).get("FREE") or {}
        usd = tier.get("tieredEventPriceUsd", ev.get("eventPriceUsd"))
        out.append({"event": name, "title": ev.get("eventTitle", name), "usd": usd})
    return out


def build() -> list[dict]:
    overrides = {k: v for k, v in json.loads(DESCRIPTIONS.read_text(encoding="utf-8")).items() if not k.startswith("_")}
    tools = []
    for slug in SLUGS:
        try:
            act = get(f"{API}{OWNER}~{slug}")
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise
            print(f"skip {slug}: not public yet", file=sys.stderr)
            continue
        build = get(f"{API}{OWNER}~{slug}/builds/default")
        schema = (build.get("actorDefinition") or {}).get("input") or json.loads(build.get("inputSchema") or "{}")
        props = {}
        for key, p in (schema.get("properties") or {}).items():
            if p.get("isSecret") or p.get("editor") in SKIP_EDITORS:
                continue
            props[key] = convert_prop(p)
        required = [r for r in schema.get("required") or [] if r in props]
        tools.append(
            {
                "name": tool_name(slug),
                "actor": f"{OWNER}/{slug}",
                "title": act.get("title") or slug,
                "description": overrides.get(tool_name(slug)) or text(act.get("description")),
                "storeDescription": text(act.get("description")),
                "url": f"https://apify.com/{OWNER}/{slug}",
                "pricing": price_lines(act),
                "inputSchema": {
                    "type": "object",
                    "properties": props,
                    "required": required,
                    "additionalProperties": False,
                },
            }
        )
        if tool_name(slug) not in overrides:
            print(f"warn {slug}: no TDQS description in {DESCRIPTIONS.name}; using the Store blurb", file=sys.stderr)
        print(f"ok {slug}: {len(props)} inputs", file=sys.stderr)
    return tools


if __name__ == "__main__":
    data = {"owner": OWNER, "tools": build()}
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT}", file=sys.stderr)
