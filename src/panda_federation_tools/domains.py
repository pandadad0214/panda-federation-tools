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
            "wayback_snapshot_finder",
            "topic_trends_tracker",
        }
    ),
    "public-funding": frozenset(
        {
            "grants_finder",
            "federal_contract_finder",
            "sbir_sttr_topic_radar",
            "sec_financials_excel",
            "clinical_trial_leads",
            "federal_register_monitor",
            "product_recall_monitor",
            "vin_decoder_recalls",
            "sam_gov_opportunities",
            "eu_ted_tenders",
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
            "trucking_company_leads",
            "nonprofit_leads_irs",
            "building_permit_leads",
            "florida_new_business_leads",
            "texas_new_business_leads",
            "new_york_new_business_leads",
            "h1b_lca_sponsor_leads",
            "colorado_new_business_leads",
            "france_company_leads",
        }
    ),
    "web-security": frozenset(
        {
            "email_domain_security_checker",
            "ai_search_seo_audit",
            "website_change_monitor",
            "hidden_ai_instructions_scanner",
            "bulk_domain_whois_expiry",
            "broken_link_checker",
            "rss_feed_monitor",
        }
    ),
}

# Official MCP Registry server.json description max (body.description).
REGISTRY_DESCRIPTION_MAX = 100

DOMAIN_META: dict[str, dict[str, str]] = {
    "research": {
        "package": "panda-research-tools",
        "title": "Panda Research Tools",
        "scope": (
            "Scholarly integrity and papers: citation checks, literature/PubMed search, experts, PDF tables, "
            "Wayback Machine snapshots, topic trends."
        ),
        # Copied into each domain repo's server.json; must stay <= REGISTRY_DESCRIPTION_MAX.
        "registry_description": (
            "Scholarly integrity — citations, literature/PubMed, experts, PDF tables, Wayback, trends (8 tools)."
        ),
    },
    "public-funding": {
        "package": "panda-public-funding-tools",
        "title": "Panda Public Funding Tools",
        "scope": (
            "Public money, filings and safety monitors: grants, contracts, SAM.gov bids, SBIR/STTR, SEC, "
            "clinical trials, Federal Register, recalls, VIN decode, EU tenders."
        ),
        "registry_description": (
            "Public money & safety: grants, contracts, SAM.gov bids, SBIR, SEC, FedReg, recalls, EU tenders (10)."
        ),
    },
    "leads": {
        "package": "panda-leads-tools",
        "title": "Panda Leads Tools",
        "scope": (
            "Public leads and enrichment: NPI, podcasts, local businesses, hiring, websites, teams, "
            "trucking, IRS nonprofits, building permits, new Florida, Texas, New York and Colorado businesses, "
            "H-1B sponsors, French companies."
        ),
        "registry_description": (
            "Public leads from official data: NPI, local, hiring, trucking, IRS, permits, new firms, France (15)."
        ),
    },
    "web-security": {
        "package": "panda-web-security-tools",
        "title": "Panda Web Security Tools",
        "scope": (
            "Site, email and agent safety: SPF/DKIM/DMARC, AI/SEO audit, page-change monitor, hidden AI instructions, "
            "domain WHOIS/expiry, broken links, RSS feed monitor."
        ),
        "registry_description": (
            "Site/email/agent safety and monitors: SPF/DKIM, SEO, change + RSS monitors, hidden-AI, WHOIS (7)."
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


def validate_registry_descriptions() -> None:
    """Fail if any domain registry_description exceeds the MCP Registry 100-char limit."""
    bad: list[str] = []
    for domain, meta in DOMAIN_META.items():
        desc = meta.get("registry_description", "")
        if not desc:
            bad.append(f"{domain}: missing registry_description")
            continue
        if len(desc) > REGISTRY_DESCRIPTION_MAX:
            bad.append(f"{domain}: len={len(desc)}>{REGISTRY_DESCRIPTION_MAX}: {desc!r}")
    if bad:
        raise RuntimeError("registry_description over MCP limit: " + "; ".join(bad))


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
