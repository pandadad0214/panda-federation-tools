"""MCP server (stdio) exposing the public Panda Federation Apify Actors as tools."""

from __future__ import annotations

import json
import logging
import sys
from collections.abc import Callable
from typing import Any

import anyio
from jsonschema import Draft202012Validator
from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

from panda_federation_tools import __version__
from panda_federation_tools.apify import ApifyClient, ApifyError, redact
from panda_federation_tools.catalog import RUN_OPTIONS, ToolSpec, get_tool, load_catalog
from panda_federation_tools.config import Settings

log = logging.getLogger("panda_federation_tools")
MAX_TEXT_CHARS = 60_000
STORE_URL = "https://apify.com/pandadad0214"

INSTRUCTIONS = """Panda Federation Tools: research and public-data tools (Apify Actors by pandadad0214).
Each tool runs one Apify Actor on the user's own Apify account (APIFY_TOKEN) and returns its dataset items.
Citations: reference_checker flags fake, mismatched or retracted references; find real papers with
literature_search or pubmed_evidence_table; format them with citation_formatter.
Leads and company data: company_hiring_signals, company_website_enricher, company_team_finder,
local_business_leads, trucking_company_leads, podcast_leads_finder.
Audits: email_domain_security_checker, ai_search_seo_audit.
Public data: grants_finder, federal_contract_finder, npi_provider_lists, topic_trends_tracker,
pdf_table_extractor, researcher_expert_finder.
Results carry a one-line `summary`; rows may be marked OK / CHECK / FIX.
Every call costs a little per result (empty runs are not charged per result) and is capped by
run_max_charge_usd. Keep inputs small first, then widen."""

ClientFactory = Callable[[Settings], ApifyClient]


def _default_factory(settings: Settings) -> ApifyClient:
    return ApifyClient(settings.token, api_base=settings.api_base)


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


async def call_tool(
    spec: ToolSpec, arguments: dict[str, Any], settings: Settings, factory: ClientFactory = _default_factory
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
    client = factory(settings)
    try:
        items = await client.run_actor(
            spec.actor, arguments, timeout_secs=timeout_secs, max_items=max_items, max_charge_usd=max_charge
        )
    except ApifyError as exc:
        return _error(redact(str(exc), settings.token))
    except Exception as exc:  # never leak internals or secrets
        log.error("unexpected error in %s: %s", spec.name, redact(type(exc).__name__, settings.token))
        return _error(f"Unexpected error running {spec.name}. Please try again.")
    payload: dict[str, Any] = {"actor": spec.actor, "count": len(items), "items": items}
    if not items:
        payload["note"] = "No results. Runs that find nothing are not charged per result."
    text = json.dumps(payload, ensure_ascii=False, default=str)
    if len(text) > MAX_TEXT_CHARS:
        text = text[:MAX_TEXT_CHARS] + "... [truncated; lower run_max_items or read structuredContent]"
    return types.CallToolResult(content=[types.TextContent(type="text", text=text)], structured_content=payload)


def create_server(settings: Settings | None = None, factory: ClientFactory = _default_factory) -> Server[Any]:
    cfg = settings or Settings.from_env()
    tools = [_tool(s) for s in load_catalog()]

    async def on_list_tools(ctx: Any, params: types.PaginatedRequestParams | None) -> types.ListToolsResult:
        return types.ListToolsResult(tools=tools)

    async def on_call_tool(ctx: Any, params: types.CallToolRequestParams) -> types.CallToolResult:
        spec = get_tool(params.name)
        if spec is None:
            return _error(f"Unknown tool: {params.name}")
        return await call_tool(spec, dict(params.arguments or {}), cfg, factory)

    def schema_for(name: str) -> dict[str, Any] | None:
        spec = get_tool(name)
        return spec.input_schema if spec else None

    return Server(
        "panda-federation-tools",
        version=__version__,
        title="Panda Federation Tools",
        instructions=INSTRUCTIONS,
        website_url=STORE_URL,
        on_list_tools=on_list_tools,
        on_call_tool=on_call_tool,
        get_tool_input_schema=schema_for,
    )


async def _run() -> None:
    server = create_server()
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


def main() -> None:
    logging.basicConfig(level=logging.WARNING, stream=sys.stderr, format="%(levelname)s %(name)s: %(message)s")
    if "--version" in sys.argv[1:]:
        print(__version__)
        return
    anyio.run(_run)
