"""Domain partitions for focused MCP servers (TDQS / Glama Tool Count band)."""

from __future__ import annotations

from typing import Literal

from panda_federation_tools.catalog import ToolSpec, load_catalog

Domain = Literal["research", "public-funding", "leads", "web-security"]

DOMAINS: dict[str, frozenset[str]] = {
    "research": frozenset(
        {
            "reference_checker",
            "citation_formatter",
            "literature_search",
            "pubmed_evidence_table",
            "researcher_expert_finder",
            "pdf_table_extractor",
        }
    ),
    "public-funding": frozenset(
        {
            "grants_finder",
            "federal_contract_finder",
            "sbir_sttr_topic_radar",
            "sec_financials_excel",
            "clinical_trial_leads",
        }
    ),
    "leads": frozenset(
        {
            "npi_provider_lists",
            "podcast_leads_finder",
            "local_business_leads",
            "company_hiring_signals",
            "company_website_enricher",
            "company_team_finder",
            "topic_trends_tracker",
            "trucking_company_leads",
        }
    ),
    "web-security": frozenset(
        {
            "email_domain_security_checker",
            "ai_search_seo_audit",
            "website_change_monitor",
            "hidden_ai_instructions_scanner",
        }
    ),
}

DOMAIN_META: dict[str, dict[str, str]] = {
    "research": {
        "package": "panda-research-tools",
        "title": "Panda Research Tools",
        "scope": "Scholarly integrity and papers: citation checks, literature/PubMed search, experts, PDF tables.",
    },
    "public-funding": {
        "package": "panda-public-funding-tools",
        "title": "Panda Public Funding Tools",
        "scope": "US federal money and filings: grants, contracts, SBIR/STTR topics, SEC financials, clinical trials.",
    },
    "leads": {
        "package": "panda-leads-tools",
        "title": "Panda Leads Tools",
        "scope": (
            "Public leads and enrichment: NPI, podcasts, local businesses, "
            "hiring, websites, teams, trends, trucking."
        ),
    },
    "web-security": {
        "package": "panda-web-security-tools",
        "title": "Panda Web Security Tools",
        "scope": (
            "Site, email and agent safety: SPF/DKIM/DMARC, AI/SEO audit, "
            "page-change monitor, hidden AI instructions."
        ),
    },
}

# Every catalog tool must belong to exactly one domain.
_ALL = frozenset().union(*DOMAINS.values())


def validate_domain_map(tools: tuple[ToolSpec, ...] | None = None) -> None:
    catalog = tools if tools is not None else load_catalog()
    names = {t.name for t in catalog}
    missing = names - _ALL
    extra = _ALL - names
    overlap: list[str] = []
    for a, tools_a in DOMAINS.items():
        for b, tools_b in DOMAINS.items():
            if a >= b:
                continue
            shared = tools_a & tools_b
            if shared:
                overlap.append(f"{a}/{b}: {sorted(shared)}")
    if missing or extra or overlap:
        raise RuntimeError(f"domain map drift: missing={sorted(missing)} extra={sorted(extra)} overlap={overlap}")


def filter_catalog(domain: str | None = None, tools: tuple[ToolSpec, ...] | None = None) -> tuple[ToolSpec, ...]:
    """Return catalog tools for one domain, or all tools when domain is None/empty."""
    catalog = tools if tools is not None else load_catalog()
    if not domain:
        return catalog
    if domain not in DOMAINS:
        raise ValueError(f"Unknown PFT_DOMAIN={domain!r}; expected one of {sorted(DOMAINS)}")
    wanted = DOMAINS[domain]
    return tuple(t for t in catalog if t.name in wanted)


def domain_of(tool_name: str) -> str | None:
    for domain, names in DOMAINS.items():
        if tool_name in names:
            return domain
    return None
