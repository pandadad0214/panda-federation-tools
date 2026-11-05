# Panda Federation Tools

**One MCP server that gives Claude, Cursor, VS Code Copilot and other AI assistants 23 research and public-data tools: citation checks, literature search, grants, contracts, SBIR/STTR topics, SEC financials, clinical trials, leads, website monitoring, domain audits and a free hidden-AI-instructions scanner.**

[![PyPI](https://img.shields.io/pypi/v/panda-federation-tools)](https://pypi.org/project/panda-federation-tools/)
[![Latest Release](https://img.shields.io/github/v/release/pandadad0214/panda-federation-tools?label=latest%20release)](https://github.com/pandadad0214/panda-federation-tools/releases/latest)
[![M8ven Score](https://m8ven.ai/badge/mcp/pandadad0214-panda-federation-tools-ta5xv3?v=eebc91f7834ff2dc3922a4031d7790f2)](https://m8ven.ai/mcp/pandadad0214-panda-federation-tools-ta5xv3?s=readme)
[![CI](https://github.com/pandadad0214/panda-federation-tools/actions/workflows/ci.yml/badge.svg)](https://github.com/pandadad0214/panda-federation-tools/actions/workflows/ci.yml)
[![CodeQL](https://github.com/pandadad0214/panda-federation-tools/actions/workflows/codeql.yml/badge.svg)](https://github.com/pandadad0214/panda-federation-tools/actions/workflows/codeql.yml)
[![MCP Registry](https://img.shields.io/badge/MCP_Registry-io.github.pandadad0214%2Fpanda--research--mcp-blue)](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.pandadad0214)
[![Apify Store](https://img.shields.io/badge/Apify_Store-pandadad0214-00a3ff)](https://apify.com/pandadad0214)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**[⬇ Download the latest Release](https://github.com/pandadad0214/panda-federation-tools/releases/latest)** · [Changelog](CHANGELOG.md)

## Install / Use

**You need:** a free [Apify API token](https://console.apify.com/settings/integrations) (the free plan includes $5/month) and [uv](https://docs.astral.sh/uv/getting-started/installation/) (one command: `curl -LsSf https://astral.sh/uv/install.sh | sh`, or on Windows `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`).

**One command** (from [PyPI](https://pypi.org/project/panda-federation-tools/)):

```bash
uvx panda-federation-tools
```

No clone needed. Replace `apify_api_YOUR_TOKEN` below with your token, and never commit a file that contains it.

**No install at all?** Use the hosted research server (4 research tools) at `https://pandadad0214--panda-research-mcp.apify.actor/mcp` with header `Authorization: Bearer <your Apify token>`. See [Hosted options](#hosted-options-no-install).

### Cursor
[![Add to Cursor](https://cursor.com/deeplink/mcp-install-dark.svg)](cursor://anysphere.cursor-deeplink/mcp/install?name=panda-federation-tools&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJwYW5kYS1mZWRlcmF0aW9uLXRvb2xzIl0sImVudiI6eyJBUElGWV9UT0tFTiI6ImFwaWZ5X2FwaV9ZT1VSX1RPS0VOIn19)

Click the button, then paste your token into `APIFY_TOKEN`. Or add this to `~/.cursor/mcp.json` (all projects) or `.cursor/mcp.json` (one project):

```json
{
  "mcpServers": {
    "panda-federation-tools": {
      "command": "uvx",
      "args": ["panda-federation-tools"],
      "env": { "APIFY_TOKEN": "apify_api_YOUR_TOKEN" }
    }
  }
}
```

### Claude Desktop
**Easiest:** download the `panda-federation-tools-<version>.mcpb` file from the [latest Release](https://github.com/pandadad0214/panda-federation-tools/releases/latest) and double-click it. Claude asks for your Apify token and keeps it in your system keychain.

Or: Settings → Developer → Edit Config, then add the same `mcpServers` block as Cursor to `claude_desktop_config.json` and restart Claude.

### Claude Code

```bash
claude mcp add panda-federation-tools --env APIFY_TOKEN=apify_api_YOUR_TOKEN -- \
  uvx panda-federation-tools
```

### VS Code (GitHub Copilot agent mode)
Add to `.vscode/mcp.json`. VS Code asks for the token and stores it securely:

```json
{
  "inputs": [
    { "type": "promptString", "id": "apify-token", "description": "Apify API token", "password": true }
  ],
  "servers": {
    "panda-federation-tools": {
      "type": "stdio",
      "command": "uvx",
      "args": ["panda-federation-tools"],
      "env": { "APIFY_TOKEN": "${input:apify-token}" }
    }
  }
}
```

### Windsurf, Cline, Zed, Goose and others
Command `uvx`, args `panda-federation-tools`, env `APIFY_TOKEN`. For Cline also set `"timeout": 60`. Agent-readable steps: [`llms-install.md`](llms-install.md).

### Other ways to install
- **Pinned to a git tag:** `uvx --from git+https://github.com/pandadad0214/panda-federation-tools@v1.3.0 panda-federation-tools`
- **From the Release download:** `uvx --from https://github.com/pandadad0214/panda-federation-tools/releases/download/v1.3.0/panda_federation_tools-1.3.0-py3-none-any.whl panda-federation-tools`
- **Helper script:** download `install.sh` (macOS/Linux) or `install.ps1` (Windows) from the latest Release. It installs uv if needed, checks the server starts and prints your config. One package works on every OS.
- **pip:** `pip install panda-federation-tools` (or a git tag: `pip install "git+https://github.com/pandadad0214/panda-federation-tools@v1.3.0"`), then run `panda-federation-tools`.
- **Docker:** `docker build -t panda-federation-tools https://github.com/pandadad0214/panda-federation-tools.git#v1.3.0` then `docker run -i --rm -e APIFY_TOKEN panda-federation-tools`.

## What's included

- **Official, free data sources only:** Crossref, OpenAlex, PubMed, Unpaywall, Grants.gov, NIH, NSF, USAspending, NPI Registry, FMCSA, public DNS, Apple Podcasts, OpenStreetMap, Wikimedia, public job-board feeds and companies' own websites. No logins, no paywalls, no LinkedIn scraping.
- **Pay per result, capped:** a few tenths of a cent per result; runs that find nothing are not charged per result; every MCP call has a hard USD spending cap.
- **Agent-friendly output:** JSON with a one-line `summary` or `agentSummary` per row and **OK / CHECK / FIX** status where it applies.
- **Your token stays yours:** the server runs on your machine and sends your `APIFY_TOKEN` only to `api.apify.com`, in a header. It is never logged or returned.

### Tools

Each MCP tool runs one public Apify Actor and returns its results. Input fields, limits and defaults come from the Actor's own input schema and are validated before anything runs, so a bad input never costs money.

| MCP tool | Apify Actor | What it does | Price (Apify free plan) |
|---|---|---|---|
| `reference_checker` | [reference-checker](https://apify.com/pandadad0214/reference-checker) | Finds fake, AI-hallucinated, mismatched and retracted citations | $0.01 / reference |
| `citation_formatter` | [citation-formatter](https://apify.com/pandadad0214/citation-formatter) | DOI, PMID, arXiv, ISBN or messy text → APA, MLA, Chicago, Harvard, IEEE, Vancouver, BibTeX, RIS | $0.003 / citation |
| `literature_search` | [literature-search](https://apify.com/pandadad0214/literature-search) | Real papers from 250M+ OpenAlex works, with citations, free PDFs and BibTeX | $0.003 / paper |
| `pubmed_evidence_table` | [pubmed-evidence-table](https://apify.com/pandadad0214/pubmed-evidence-table) | PubMed → evidence table (study design, sample size, retractions, PRISMA counts) | $0.004 / article |
| `grants_finder` | [grants-finder](https://apify.com/pandadad0214/grants-finder) | Grants.gov opportunities plus NIH and NSF awards in one table | $0.003 / grant |
| `researcher_expert_finder` | [researcher-expert-finder](https://apify.com/pandadad0214/researcher-expert-finder) | Ranked academic experts and KOLs for a topic, with ORCID and h-index | $0.0025 / expert |
| `pdf_table_extractor` | [pdf-table-extractor](https://apify.com/pandadad0214/pdf-table-extractor) | Every table in a PDF → rows, Excel and CSV, with OCR for scanned pages | $0.001 / page; $0.003 / table; $0.02 / OCR page |
| `npi_provider_lists` | [npi-provider-lists](https://apify.com/pandadad0214/npi-provider-lists) | De-duplicated US healthcare provider lists from the official NPI Registry | $0.0015 / provider |
| `federal_contract_finder` | [federal-contract-finder](https://apify.com/pandadad0214/federal-contract-finder) | USAspending contract awards, incumbents and recompete leads | $0.002 / contract |
| `email_domain_security_checker` | [email-domain-security-checker](https://apify.com/pandadad0214/email-domain-security-checker) | SPF, DKIM, DMARC, MTA-STS and BIMI audit with an A–F grade and fix list | $0.002 / domain |
| `ai_search_seo_audit` | [ai-search-seo-audit](https://apify.com/pandadad0214/ai-search-seo-audit) | SEO and AI-search (GEO) readiness per page, AI crawler access, llms.txt draft | $0.004 / page |
| `podcast_leads_finder` | [podcast-leads-finder](https://apify.com/pandadad0214/podcast-leads-finder) | Active podcasts by topic with host, published contact email and guest flag | $0.004 / podcast |
| `local_business_leads` | [local-business-leads](https://apify.com/pandadad0214/local-business-leads) | Local businesses by category and city from OpenStreetMap (Google Maps alternative) | $0.001 / business |
| `company_hiring_signals` | [company-hiring-signals](https://apify.com/pandadad0214/company-hiring-signals) | Open and new jobs, leadership roles and a hiring score from public ATS boards | $0.003 / company |
| `company_website_enricher` | [company-website-enricher](https://apify.com/pandadad0214/company-website-enricher) | Domains → name, description, published contacts, socials, tech stack, mail provider | $0.003 / domain |
| `topic_trends_tracker` | [topic-trends-tracker](https://apify.com/pandadad0214/topic-trends-tracker) | Wikipedia pageview trends with 30-day and YoY change (Google Trends alternative) | $0.002 / topic |
| `company_team_finder` | [company-team-finder](https://apify.com/pandadad0214/company-team-finder) | Leaders and decision makers from companies' own team pages (no LinkedIn scraping) | $0.002 / person |
| `trucking_company_leads` | [trucking-company-leads](https://apify.com/pandadad0214/trucking-company-leads) | New and existing US carriers and brokers from official FMCSA data | $0.002 / carrier |
| `website_change_monitor` | [website-change-monitor](https://apify.com/pandadad0214/website-change-monitor) | Page diffs, price changes and keyword alerts on any public page | $0.0015 / page |
| `sbir_sttr_topic_radar` | [sbir-sttr-topic-radar](https://apify.com/pandadad0214/sbir-sttr-topic-radar) | Open SBIR/STTR topics from every agency with deadlines and DoD Q&A | $0.003 / topic |
| `sec_financials_excel` | [sec-financials-excel](https://apify.com/pandadad0214/sec-financials-excel) | SEC EDGAR XBRL financials → comps and model-ready Excel | $0.002 / company-year |
| `hidden_ai_instructions_scanner` | [hidden-ai-instructions-scanner](https://apify.com/pandadad0214/hidden-ai-instructions-scanner) | Finds text hidden from people but aimed at AI agents (prompt injection) | Free |
| `clinical_trial_leads` | [clinical-trial-leads](https://apify.com/pandadad0214/clinical-trial-leads) | ClinicalTrials.gov trials with sponsors, phases, contacts and every site | $0.002 / trial |

Every tool also accepts three optional run controls: `run_max_items` (results to return, default 50), `run_max_charge_usd` (spending cap for the call, default $0.50) and `run_timeout_secs` (default 120, max 300). While a run is in progress the server sends MCP progress notifications every few seconds, so clients that support them do not time out. Most tools answer in 5–15 seconds for a few inputs; `local_business_leads` and big crawls can take a minute or more, so give them `run_timeout_secs: 300`.

Also on Apify: the hosted [Academic Research MCP Server](https://apify.com/pandadad0214/panda-research-mcp) ($0.01–$0.02 per call).

### Publishing soon

Built and tested, and going public on the Apify Store a few a day (Apify limits new publications). Each one joins this server as an MCP tool in the release after it goes public. Store links work once it is public.

| Apify Actor | What it does | Price |
|---|---|---|
| [nonprofit-leads-irs](https://apify.com/pandadad0214/nonprofit-leads-irs) | IRS charity and foundation lists by state, cause and size | $0.001 / nonprofit |
| [federal-register-monitor](https://apify.com/pandadad0214/federal-register-monitor) | New federal rules and notices with open comment deadlines | $0.001 / document |
| [product-recall-monitor](https://apify.com/pandadad0214/product-recall-monitor) | FDA food, drug and device plus CPSC recalls in one feed | $0.0015 / recall |
| [vin-decoder-recalls](https://apify.com/pandadad0214/vin-decoder-recalls) | Bulk NHTSA VIN decode with recall campaigns and complaint counts | $0.001 / VIN |
| [building-permit-leads](https://apify.com/pandadad0214/building-permit-leads) | New building permits from 8 US cities with trade category, job value and contractor | $0.0015 / permit |
| [florida-new-business-leads](https://apify.com/pandadad0214/florida-new-business-leads) | New Florida LLCs and corporations daily (Sunbiz) with officers and addresses | $0.0015 / business |
| [bulk-domain-whois-expiry](https://apify.com/pandadad0214/bulk-domain-whois-expiry) | Bulk RDAP/WHOIS: registrar, expiry and days left, availability, DNS host | $0.001 / domain |

[Hidden AI Instructions Watch](https://github.com/pandadad0214/hidden-ai-instructions-watch) is our public, evidence-only log of what the free scanner finds.

### Example prompts
- "Check these 12 references for fake or retracted papers and tell me which to fix."
- "Find 20 recent peer-reviewed papers on GLP-1 and heart failure with free PDFs, then format them in APA."
- "Which of these 30 SaaS companies are hiring sales leaders right now? Then find their VP-level contacts."
- "Audit the email security of acme.com and its three competitors, and list the fixes."
- "List dentists in Phoenix, AZ with a website and phone number."

### Typical workflows
- **Writing a paper:** `literature_search` → `citation_formatter` → `reference_checker` before you submit.
- **Systematic review:** `pubmed_evidence_table` (evidence table + PRISMA counts) → `reference_checker`.
- **Funding:** `grants_finder` → `literature_search` on the topic.
- **Federal contracting:** `federal_contract_finder` (recompete radar + top incumbents) → `grants_finder`.
- **Account prioritization:** `company_hiring_signals` → `company_website_enricher` → `email_domain_security_checker`.
- **Outbound to decision makers:** `company_hiring_signals` → `company_team_finder` (names, titles, email pattern).
- **Local prospecting:** `local_business_leads` → `ai_search_seo_audit` on their websites.
- **Trucking and logistics sales:** `trucking_company_leads` → `company_website_enricher`.
- **Market research:** `topic_trends_tracker` → `literature_search` or `podcast_leads_finder` on rising topics.

## Pricing

- You pay Apify per result, at the prices above, from your own Apify account. Apify Bronze, Silver and Gold plans get 10–30% off.
- **Empty runs cost nothing per result.** Apify adds a tiny platform start fee (about $0.00005 per run).
- `run_max_items` (default 50) also sets the Actor's own result limit on 19 of the 23 tools, so you only pay for the results you asked for. On `grants_finder`, `pdf_table_extractor`, `company_team_finder` and `sec_financials_excel` (whose limits count sources, pages, companies or years), set those fields directly; the charge cap still applies.
- Every MCP call is capped by `run_max_charge_usd` (default $0.50, set your own default with `PANDA_MAX_CHARGE_USD`). Apify stops the run when the cap is reached.
- The MCP server itself is free and open source (MIT).

## Configuration

| Variable | Required | Default | Meaning |
|---|---|---|---|
| `APIFY_TOKEN` | yes | none | Your Apify API token. Tools list without it; calls need it. |
| `PANDA_MAX_CHARGE_USD` | no | `0.50` | Default spending cap per call (0.01–25). |
| `PANDA_MAX_ITEMS` | no | `50` | Default max results per call (1–1000). |
| `PANDA_TIMEOUT_SECS` | no | `120` | Default seconds to wait per call (10–300). |

## Security and permissions

- **Runs locally over stdio.** It opens no ports and calls only `https://api.apify.com`.
- **Token handling:** read from the environment, sent only as an `Authorization: Bearer` header (never in a URL), redacted from every error message, and never logged or returned to the model.
- **Least privilege:** the token needs permission to run Actors. Apify supports [scoped API tokens](https://docs.apify.com/platform/integrations/api#api-tokens); a token limited to running these Actors is enough.
- **Read-only tools:** every tool only reads public data; none writes to your systems. Tools are marked `readOnlyHint: true`.
- **Validated inputs:** every call is checked against the Actor's JSON Schema (types, ranges, enums, no unknown fields) before it runs. Secret Actor inputs (such as optional third-party API keys) are deliberately not exposed to the model.
- **Bounded cost and time:** per-call spending cap, item cap and timeout. The server retries once only when Apify never started a run (rate limit or failed connection), so a retry can never charge you twice.
- **Context-safe output:** large results are trimmed to whole items (still valid JSON) for the model, with every item kept in `structuredContent`.
- **Supply chain:** pinned dependencies with a committed `uv.lock`, `pip-audit` and CodeQL in CI, Dependabot updates, and GitHub Actions pinned to commit SHAs.
- Found a vulnerability? See [SECURITY.md](SECURITY.md).

## Hosted options (no install)

- **Academic Research MCP Server (Streamable HTTP):** `https://pandadad0214--panda-research-mcp.apify.actor/mcp` with header `Authorization: Bearer <your Apify token>`. Four research tools (`check_references`, `format_citations`, `search_literature`, `pubmed_evidence_table`). This is the server listed in the official MCP Registry as `io.github.pandadad0214/panda-research-mcp` ([server.json](server.json)).
- **Apify's MCP server:** `https://mcp.apify.com` can call any of these Actors as `pandadad0214/<slug>`.
- **Plain HTTP API:**

```bash
curl -X POST "https://api.apify.com/v2/acts/pandadad0214~reference-checker/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" -H "Content-Type: application/json" \
  -d '{"dois": ["10.1038/nature14539"]}'
```

## Agent skills (Agensi)

Ready-made skills that wrap these tools for AI agents are listed on the [Panda Federation Agensi profile](https://www.agensi.io/creators/panda_federation). Each skill runs the Apify tools above, so the usual pay-per-result prices apply on top of the skill price.

- [Medical Writing Pack: evidence tables, ref checks and KOLs](https://agensi.io/skills/medical-writing-pack-evidence-tables-ref-checks-kols) ($12)
- [RFP Compliance Matrix + Incumbent Intel](https://agensi.io/skills/rfp-compliance-matrix-incumbent-intel-federal-proposals) (free)
- [GEO & SEO Site Audit](https://agensi.io/skills/geo-seo-site-audit-real-crawl-0-100-score-0-004-page) ($4.99)
- [Email Deliverability Audit: SPF/DKIM/DMARC in bulk](https://agensi.io/skills/email-deliverability-audit-live-spf-dkim-dmarc-in-bulk) (free)
- [Citation Check: fake, miscited and retracted references](https://agensi.io/skills/citation-check-fake-miscited-retracted-references) (free)

## Hire a human (Fiverr)
Prefer a person to run the tools and hand you finished files? Panda Federation also sells these as Fiverr gigs (seller `pandafederation`). Professional use only, not for coursework.

| Gig | Use when | Price |
|---|---|---|
| [Reference verification](https://www.fiverr.com/pandafederation/verify-your-references-find-fake-citations-and-retracted-papers) | You want a person to check a whole reference list for fake, mismatched or retracted citations and get a color-coded PDF/Excel report. | from $15, 2-3 days |
| [Reference list formatting](https://www.fiverr.com/pandafederation/format-or-convert-your-reference-list-to-apa-mla-chicago-or-harvard) | You want a finished reference list formatted or converted to APA, MLA, Chicago, Harvard, IEEE or Vancouver, delivered as Word and PDF. | from $20, 2-3 days |
| [Web data to CSV/Excel](https://www.fiverr.com/pandafederation/scrape-website-data-into-a-clean-csv-or-excel-spreadsheet) | You want public business data from a website collected and cleaned into CSV or Excel (no logins, paywalls or personal contact data). | from $30, 3-5 days |
| [Scholarly source lists](https://www.fiverr.com/pandafederation/find-and-screen-scholarly-sources-for-your-topic-with-excel-bibtex-and-ris) | You want a screened list of scholarly sources on a topic, with retraction flags and Excel, BibTeX and RIS files (PubMed study table available as an add-on). | from $25, 2-5 days |

## For developers

### For AI agents and LLMs
- [`llms.txt`](llms.txt): short index of every tool and when to use it ([llms.txt convention](https://llmstxt.org)).
- [`llms-full.txt`](llms-full.txt): each tool's inputs, outputs and prices in one file.
- [`llms-install.md`](llms-install.md): step-by-step setup for AI coding agents such as Cline.
- Every result has a one-line summary field (`summary` on the citation, literature, PubMed, PDF, NPI and expert tools; `agentSummary` on the others), and every run saves a `SUMMARY` record with a `takeaway` and the suggested next tool.
- Start small (one or two inputs), read the summary line, then widen.

### Build, test and contribute

```bash
git clone https://github.com/pandadad0214/panda-federation-tools && cd panda-federation-tools
uv sync                 # installs pinned dependencies from uv.lock
uv run pytest           # offline tests, no token or network needed
uv run ruff check . && uv run mypy
python scripts/build_catalog.py   # refresh tool schemas and prices from the Apify Store
```

Layout: `src/panda_federation_tools/` (server, Apify client, bundled `catalog.json`), `tests/`, `scripts/build_catalog.py`, `Dockerfile`. See [CONTRIBUTING.md](CONTRIBUTING.md) and [CHANGELOG.md](CHANGELOG.md).

## Issues and requests
Open an [issue](https://github.com/pandadad0214/panda-federation-tools/issues) here or on any tool's Apify Issues tab. We answer within a day.

Built by Panda Federation with AI assistance. MIT licensed.
