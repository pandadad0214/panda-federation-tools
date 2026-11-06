"""MCP server (stdio) exposing the public Panda Federation Apify Actors as tools."""

from __future__ import annotations

import json
import logging
import os
import sys
from collections.abc import Awaitable, Callable
from typing import Any

import anyio
from jsonschema import Draft202012Validator
from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

from panda_federation_tools import __version__
from panda_federation_tools.apify import ApifyClient, ApifyError, redact
from panda_federation_tools.catalog import RUN_OPTIONS, ToolSpec, get_tool
from panda_federation_tools.config import Settings
from panda_federation_tools.domains import DOMAIN_META, DOMAINS, filter_catalog

log = logging.getLogger("panda_federation_tools")
MAX_TEXT_CHARS = 60_000
HEARTBEAT_SECS = 5
STORE_URL = "https://apify.com/pandadad0214"

INDEX_INSTRUCTIONS = """Panda Federation Tools is the index / compatibility surface for Panda Federation MCP tools.
Recommended: install one focused server instead of this mega-server (better Glama Tool Count / coherence):
  panda-research-tools (6) — citations, literature, PubMed, experts, PDF tables
  panda-public-funding-tools (8) — grants, contracts, SBIR/STTR, SEC, clinical trials, Federal Register, recalls, VIN
  panda-leads-tools (9) — NPI, podcasts, local businesses, hiring, enrichment, teams, trends, trucking, IRS nonprofits
  panda-web-security-tools (4) — email domain security, AI/SEO audit, website change monitor, hidden AI scanner
This process still exposes all tools when PFT_DOMAIN is unset (backward compatible). Set PFT_DOMAIN to
research | public-funding | leads | web-security to load only that domain, or use the matching console script.
Each tool runs one Apify Actor on the user's own Apify account (APIFY_TOKEN) and returns its dataset items.
Every call costs a little per result (empty runs are not charged per result) and is capped by run_max_charge_usd.
run_max_items also caps how many results most tools produce and charge for. Keep inputs small first, then widen."""

DOMAIN_INSTRUCTIONS: dict[str, str] = {
    "research": """Panda Research Tools: scholarly integrity and papers (Apify Actors by pandadad0214).
Tools: reference_checker (fake/mismatched/retracted citations), citation_formatter (APA/MLA/etc.),
literature_search (OpenAlex papers), pubmed_evidence_table (PubMed screening tables),
researcher_expert_finder (academic KOLs), pdf_table_extractor (PDF tables to Excel/CSV).
Sibling servers: panda-public-funding-tools (grants/contracts/trials), panda-leads-tools (B2B leads),
panda-web-security-tools (email/site/agent safety). Use literature_search for all disciplines;
pubmed_evidence_table only for biomedical PubMed queries. Each tool runs on the user's APIFY_TOKEN.
Empty runs are not charged per result; spending is capped by run_max_charge_usd.""",
    "public-funding": """Panda Public Funding Tools: US federal money, filings and safety monitors
(Apify Actors by pandadad0214).
Tools: grants_finder (Grants.gov + NIH/NSF awards), federal_contract_finder (USAspending awards/recompetes),
sbir_sttr_topic_radar (open SBIR/STTR topics), sec_financials_excel (EDGAR XBRL comps),
clinical_trial_leads (ClinicalTrials.gov sponsors/sites/contacts),
federal_register_monitor (rules and comment deadlines),
product_recall_monitor (FDA + CPSC recalls), vin_decoder_recalls (NHTSA VIN decode + recalls).
Sibling servers: panda-research-tools (papers/citations), panda-leads-tools (B2B leads),
panda-web-security-tools (email/site/agent safety). Use grants_finder for assistance awards,
federal_contract_finder for procurement contracts, sbir_sttr_topic_radar for open topics to bid,
federal_register_monitor for rulemaking, product_recall_monitor for FDA/CPSC,
vin_decoder_recalls for vehicles.
Each tool runs on the user's APIFY_TOKEN. Empty runs are not charged per result; capped by run_max_charge_usd.""",
    "leads": """Panda Leads Tools: public leads and enrichment (Apify Actors by pandadad0214).
Tools: npi_provider_lists (US healthcare NPI), podcast_leads_finder (shows/hosts with RSS emails),
local_business_leads (OpenStreetMap businesses), company_hiring_signals (public ATS boards),
company_website_enricher (firmographics from the company site), company_team_finder (people from team pages),
topic_trends_tracker (Wikipedia pageview trends), trucking_company_leads (FMCSA carriers/brokers),
nonprofit_leads_irs (IRS Exempt Organizations charities and foundations).
Sibling servers: panda-research-tools (papers), panda-public-funding-tools (federal $),
panda-web-security-tools (email/site/agent safety). Prefer company_team_finder for people,
company_website_enricher for one firmographic row, nonprofit_leads_irs for tax-exempt orgs.
Each tool runs on the user's APIFY_TOKEN. Empty runs are not charged per result; capped by run_max_charge_usd.""",
    "web-security": """Panda Web Security Tools: site, email and agent safety (Apify Actors by pandadad0214).
Tools: email_domain_security_checker (SPF/DKIM/DMARC/MTA-STS/BIMI), ai_search_seo_audit (SEO + GEO readiness),
website_change_monitor (page diffs, price and keyword alerts), hidden_ai_instructions_scanner
(free prompt-injection / hidden-AI-text detector).
Sibling servers: panda-research-tools, panda-public-funding-tools, panda-leads-tools.
Use hidden_ai_instructions_scanner before an agent reads an untrusted page. Each tool runs on the
user's APIFY_TOKEN (scanner is free). Empty runs are not charged per result; capped by run_max_charge_usd.""",
}

ClientFactory = Callable[[Settings], ApifyClient]


def _default_factory(settings: Settings) -> ApifyClient:
    return ApifyClient(settings.token, api_base=settings.api_base)


def resolve_domain(explicit: str | None = None) -> str | None:
    """Return a validated domain from argument or PFT_DOMAIN env, or None for the full index."""
    raw = explicit if explicit is not None else os.environ.get("PFT_DOMAIN", "").strip()
    if not raw:
        return None
    if raw not in DOMAINS:
        raise SystemExit(f"Unknown PFT_DOMAIN={raw!r}; expected one of {sorted(DOMAINS)} or empty")
    return raw


def instructions_for(domain: str | None) -> str:
    if domain is None:
        return INDEX_INSTRUCTIONS
    return DOMAIN_INSTRUCTIONS[domain]


def server_identity(domain: str | None) -> tuple[str, str]:
    """Return (mcp_name, title) for the running surface."""
    if domain is None:
        return "panda-federation-tools", "Panda Federation Tools"
    meta = DOMAIN_META[domain]
    return meta["package"], meta["title"]


def _tool(spec: ToolSpec) -> types.Tool:
    return types.Tool(
        name=spec.name,
        title=spec.title,
        description=spec.tool_description,
        input_schema=spec.input_schema,
        annotations=types.ToolAnnotations(
            title=spec.title,
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=True,
        ),
    )


def _error(msg: str) -> types.CallToolResult:
    return types.CallToolResult(content=[types.TextContent(type="text", text=msg)], is_error=True)


def validate_arguments(spec: ToolSpec, arguments: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(spec.input_schema)
    errors = []
    for err in sorted(validator.iter_errors(arguments), key=lambda e: list(e.path)):
        where = ".".join(str(p) for p in err.path) or "input"
        errors.append(f"{where}: {err.message}")
    return errors


def _fit_text(payload: dict[str, Any]) -> str:
    """JSON text for the model, kept under MAX_TEXT_CHARS by dropping whole items (always valid JSON)."""
    text = json.dumps(payload, ensure_ascii=False, default=str)
    if len(text) <= MAX_TEXT_CHARS:
        return text
    items = list(payload["items"])
    shown = dict(payload)
    lo, hi = 0, len(items)
    while lo < hi:  # largest prefix of items that fits
        mid = (lo + hi + 1) // 2
        shown["items"] = items[:mid]
        if len(json.dumps(shown, ensure_ascii=False, default=str)) + 200 <= MAX_TEXT_CHARS:
            lo = mid
        else:
            hi = mid - 1
    shown["items"] = items[:lo]
    shown["truncated"] = (
        f"Showing {lo} of {len(items)} items to fit the context window. All items are in structuredContent; "
        "lower run_max_items for shorter output."
    )
    return json.dumps(shown, ensure_ascii=False, default=str)


ProgressFn = Callable[[float, float | None, str | None], Awaitable[None]]


async def _heartbeat(progress: ProgressFn, spec: ToolSpec, timeout_secs: int) -> None:
    """Report progress every few seconds so MCP clients do not time out on long Actor runs."""
    elapsed = 0
    while True:
        await anyio.sleep(HEARTBEAT_SECS)
        elapsed += HEARTBEAT_SECS
        try:
            await progress(float(elapsed), float(timeout_secs), f"{spec.title}: running on Apify ({elapsed}s)")
        except Exception:  # progress is best effort; never fail the call because of it
            log.debug("progress notification failed", exc_info=True)
            return


async def call_tool(
    spec: ToolSpec,
    arguments: dict[str, Any],
    settings: Settings,
    factory: ClientFactory = _default_factory,
    progress: ProgressFn | None = None,
) -> types.CallToolResult:
    arguments = dict(arguments or {})
    problems = validate_arguments(spec, arguments)
    if problems:
        return _error("Invalid input for " + spec.name + ":\n- " + "\n- ".join(problems[:20]))
    max_items = int(arguments.pop("run_max_items", settings.max_items))
    max_charge = float(arguments.pop("run_max_charge_usd", settings.max_charge_usd))
    timeout_secs = int(arguments.pop("run_timeout_secs", settings.timeout_secs))
    for key in RUN_OPTIONS:
        arguments.pop(key, None)
    arguments = spec.apply_result_cap(arguments, max_items)
    client = factory(settings)
    try:
        async with anyio.create_task_group() as tg:
            if progress is not None:
                tg.start_soon(_heartbeat, progress, spec, timeout_secs)
            items = await client.run_actor(
                spec.actor, arguments, timeout_secs=timeout_secs, max_items=max_items, max_charge_usd=max_charge
            )
            tg.cancel_scope.cancel()
    except ApifyError as exc:
        return _error(redact(str(exc), settings.token))
    except Exception as exc:  # never leak internals or secrets
        log.error("unexpected error in %s: %s", spec.name, redact(type(exc).__name__, settings.token))
        return _error(f"Unexpected error running {spec.name}. Please try again.")
    payload: dict[str, Any] = {"actor": spec.actor, "count": len(items), "items": items}
    if not items:
        payload["note"] = "No results. Runs that find nothing are not charged per result."
    text = _fit_text(payload)
    return types.CallToolResult(content=[types.TextContent(type="text", text=text)], structured_content=payload)


def create_server(
    settings: Settings | None = None,
    factory: ClientFactory = _default_factory,
    domain: str | None = None,
) -> Server[Any]:
    cfg = settings or Settings.from_env()
    active = resolve_domain(domain)
    catalog = filter_catalog(active)
    tools = [_tool(s) for s in catalog]
    allowed = {s.name for s in catalog}
    name, title = server_identity(active)

    async def on_list_tools(ctx: Any, params: types.PaginatedRequestParams | None) -> types.ListToolsResult:
        return types.ListToolsResult(tools=tools)

    async def on_call_tool(ctx: Any, params: types.CallToolRequestParams) -> types.CallToolResult:
        if params.name not in allowed:
            return _error(f"Unknown tool: {params.name}")
        spec = get_tool(params.name)
        if spec is None:
            return _error(f"Unknown tool: {params.name}")
        session = getattr(ctx, "session", None)
        progress = getattr(session, "report_progress", None)
        return await call_tool(spec, dict(params.arguments or {}), cfg, factory, progress)

    def schema_for(name: str) -> dict[str, Any] | None:
        if name not in allowed:
            return None
        spec = get_tool(name)
        return spec.input_schema if spec else None

    return Server(
        name,
        version=__version__,
        title=title,
        instructions=instructions_for(active),
        website_url=STORE_URL,
        on_list_tools=on_list_tools,
        on_call_tool=on_call_tool,
        get_tool_input_schema=schema_for,
    )


async def _run(domain: str | None = None) -> None:
    server = create_server(domain=domain)
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


def main_for(domain: str | None = None) -> None:
    logging.basicConfig(level=logging.WARNING, stream=sys.stderr, format="%(levelname)s %(name)s: %(message)s")
    if "--version" in sys.argv[1:]:
        print(__version__)
        return
    # Domain console scripts set PFT_DOMAIN; CLI flag also accepted for debugging.
    if domain is not None:
        os.environ["PFT_DOMAIN"] = domain
    anyio.run(_run, domain)


def main() -> None:
    """Umbrella / index entry (all tools unless PFT_DOMAIN is set)."""
    main_for(None)


def main_research() -> None:
    main_for("research")


def main_public_funding() -> None:
    main_for("public-funding")


def main_leads() -> None:
    main_for("leads")


def main_web_security() -> None:
    main_for("web-security")
