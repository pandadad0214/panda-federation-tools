# Panda Federation Tools

Reliable research and public-data tools that run on [Apify](https://apify.com/pandadad0214). Every tool uses official, free sources (Crossref, OpenAlex, PubMed, Unpaywall, Grants.gov, NIH, NSF, USAspending), charges only per result, and gives you Excel/CSV/JSON plus a clear **OK / CHECK / FIX** status where it applies. Built with AI assistance.

| Tool | What it does | Price (free plan) |
|---|---|---|
| [Reference Checker](https://apify.com/pandadad0214/reference-checker) | Finds fake, AI-hallucinated and retracted citations in a reference list | $0.01 / reference |
| [Citation Generator API](https://apify.com/pandadad0214/citation-formatter) | DOI, PMID, arXiv, ISBN or messy text → APA, MLA, Chicago, Harvard, IEEE, Vancouver, BibTeX | $0.003 / citation |
| [Google Scholar Scraper Alternative](https://apify.com/pandadad0214/literature-search) | Real papers from 250M+ OpenAlex works, with citations, free PDFs, BibTeX | $0.003 / paper |
| [PubMed Scraper](https://apify.com/pandadad0214/pubmed-evidence-table) | PubMed → evidence table (study design, sample size, retractions) in Excel | $0.004 / article |
| [Grants.gov Scraper](https://apify.com/pandadad0214/grants-finder) | Federal grants plus NIH & NSF awards in one table | $0.003 / grant |
| [Academic Research MCP Server](https://apify.com/pandadad0214/panda-research-mcp) | All of the above as tools for Claude, Cursor and other AI agents | $0.01–$0.02 / call |
| [PDF to Excel & CSV Converter](https://apify.com/pandadad0214/pdf-table-extractor) | Every table in a PDF → Excel & CSV, with OCR for scanned pages | $0.001 / page |
| [NPI Registry Scraper](https://apify.com/pandadad0214/npi-provider-lists) | De-duplicated US doctor & healthcare provider lists from the official NPI Registry | $0.0015 / provider |
| [Google Scholar Author Alternative](https://apify.com/pandadad0214/researcher-expert-finder) | Ranked academic experts & KOLs for a research topic, with ORCID and h-index | $0.0025 / expert |
| [USAspending Scraper: Federal Contracts](https://apify.com/pandadad0214/federal-contract-finder) | Federal contract awards, incumbents and recompete leads (contracts ending soon) by NAICS, PSC, agency or set-aside | $0.002 / contract |

Apify's free plan includes $5/month of credit. Bronze, Silver and Gold Apify plans get 10–30% off.

## For AI agents and LLMs
- [`llms.txt`](llms.txt): short index of every tool and when to use it ([llms.txt convention](https://llmstxt.org)).
- [`llms-full.txt`](llms-full.txt): each tool's inputs, outputs and prices in one file.
- Every result has a one-line `summary` field, and every run saves a `SUMMARY` record with a `takeaway` and the suggested next tool.
- Agents can run any tool through Apify's MCP server at `https://mcp.apify.com`, or connect the Academic Research MCP Server directly.

## Typical workflows
- **Writing a paper:** Literature Search → Citation Generator → Reference Checker before you submit.
- **Systematic review:** PubMed Scraper (evidence table + PRISMA counts) → Reference Checker.
- **Funding:** Grants.gov Scraper → Literature Search on the topic.
- **Federal contracting:** USAspending Scraper (recompete radar + top incumbents) → Grants.gov Scraper for related funding.
- **AI agents:** connect the MCP server so your agent checks its own citations.

## Quick start (API)
```bash
curl -X POST "https://api.apify.com/v2/acts/pandadad0214~reference-checker/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" -H "Content-Type: application/json" \
  -d '{"bibliography": "LeCun, Y., Bengio, Y., & Hinton, G. (2015). Deep learning. Nature, 521, 436-444."}'
```

## Hire a human (Fiverr)
Prefer a person to run the tools and hand you finished files? Panda Federation also sells these as Fiverr gigs (seller `pandafederation`). Professional use only, not for coursework.

| Gig | Use when | Price |
|---|---|---|
| [Reference verification](https://www.fiverr.com/pandafederation/verify-your-references-find-fake-citations-and-retracted-papers) | You want a person to check a whole reference list for fake, mismatched or retracted citations and get a color-coded PDF/Excel report. | from $15, 2-3 days |
| [Reference list formatting](https://www.fiverr.com/pandafederation/format-or-convert-your-reference-list-to-apa-mla-chicago-or-harvard) | You want a finished reference list formatted or converted to APA, MLA, Chicago, Harvard, IEEE or Vancouver, delivered as Word and PDF. | from $20, 2-3 days |
| [Web data to CSV/Excel](https://www.fiverr.com/pandafederation/scrape-website-data-into-a-clean-csv-or-excel-spreadsheet) | You want public business data from a website collected and cleaned into CSV or Excel (no logins, paywalls or personal contact data). | from $30, 3-5 days |
| [Scholarly source lists](https://www.fiverr.com/pandafederation/find-and-screen-scholarly-sources-for-your-topic-with-excel-bibtex-and-ris) | You want a screened list of scholarly sources on a topic, with retraction flags and Excel, BibTeX and RIS files (PubMed study table available as an add-on). | from $25, 2-5 days |

## Issues and requests
Open an issue here or on any tool's Apify Issues tab. We answer within a day.
