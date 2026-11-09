"""Domain partition and focused-server catalog filters."""

import pytest
from mcp import Client

from panda_federation_tools.catalog import load_catalog
from panda_federation_tools.config import Settings
from panda_federation_tools.domains import (
    DOMAIN_META,
    DOMAINS,
    REGISTRY_DESCRIPTION_MAX,
    filter_catalog,
    validate_domain_map,
    validate_registry_descriptions,
)
from panda_federation_tools.server import INDEX_INSTRUCTIONS, create_server, instructions_for, server_identity

TOKEN = "apify_api_DOMAINTEST999"

EXPECTED_COUNTS = {
    "research": 7,
    "public-funding": 8,
    "leads": 15,
    "web-security": 6,
}


def test_domain_map_covers_every_catalog_tool_exactly_once():
    validate_domain_map()
    catalog_names = {t.name for t in load_catalog()}
    mapped = set().union(*DOMAINS.values())
    assert mapped == catalog_names
    assert sum(EXPECTED_COUNTS.values()) == len(catalog_names) == 36


def test_registry_descriptions_within_mcp_limit():
    validate_registry_descriptions()
    for domain, meta in DOMAIN_META.items():
        desc = meta["registry_description"]
        assert 1 <= len(desc) <= REGISTRY_DESCRIPTION_MAX, (domain, len(desc), desc)


@pytest.mark.parametrize("domain,count", list(EXPECTED_COUNTS.items()))
def test_filter_catalog_domain_counts(domain, count):
    tools = filter_catalog(domain)
    assert len(tools) == count
    assert {t.name for t in tools} == DOMAINS[domain]


def test_filter_catalog_none_returns_all():
    assert filter_catalog(None) == load_catalog()
    assert filter_catalog("") == load_catalog()


def test_filter_catalog_unknown_domain_raises():
    with pytest.raises(ValueError, match="Unknown PFT_DOMAIN"):
        filter_catalog("astronomy")


@pytest.mark.parametrize("domain", list(DOMAINS))
def test_domain_meta_and_instructions(domain):
    meta = DOMAIN_META[domain]
    assert meta["package"].startswith("panda-")
    assert meta["scope"]
    text = instructions_for(domain)
    assert meta["package"] in text or domain.replace("-", " ") in text.lower() or "Tools:" in text
    name, title = server_identity(domain)
    assert name == meta["package"]
    assert title == meta["title"]


def test_index_instructions_recommend_focused_servers():
    assert "panda-research-tools" in INDEX_INSTRUCTIONS
    assert "PFT_DOMAIN" in INDEX_INSTRUCTIONS
    name, _title = server_identity(None)
    assert name == "panda-federation-tools"


class FakeClient:
    async def run_actor(self, actor, run_input, **kw):
        return []


async def test_create_server_respects_domain_filter():
    async with Client(create_server(Settings(token=TOKEN), factory=lambda s: FakeClient(), domain="research")) as c:
        result = await c.list_tools()
    names = {t.name for t in result.tools}
    assert names == DOMAINS["research"]
    assert "grants_finder" not in names


async def test_create_server_domain_rejects_out_of_domain_tool():
    async with Client(create_server(Settings(token=TOKEN), factory=lambda s: FakeClient(), domain="web-security")) as c:
        r = await c.call_tool("reference_checker", {"dois": ["10.1038/nature14539"]})
    assert r.is_error and "Unknown tool" in r.content[0].text


def test_pft_domain_env(monkeypatch):
    monkeypatch.setenv("PFT_DOMAIN", "leads")
    server = create_server(Settings(token=TOKEN), factory=lambda s: FakeClient())
    assert server.name == "panda-leads-tools"
    monkeypatch.delenv("PFT_DOMAIN", raising=False)
    server2 = create_server(Settings(token=TOKEN), factory=lambda s: FakeClient())
    assert server2.name == "panda-federation-tools"
