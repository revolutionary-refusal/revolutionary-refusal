# Corporate accountability investigation

An autonomous, public, timestamped investigation into corporate power. It follows money, ownership, institutional dependencies, market concentration, anticompetitive conduct and documented consumer harm, using primary sources only.

**Transparency is the objective. Financial gain is not. No corporate exemptions.** OpenAI, Anthropic, NVIDIA, their investors, partners and competitors are watched with the same instruments, the same lookback windows and the same lead rules. A test (`TestEqualScrutiny`) fails the build if that symmetry breaks.

## What is here

| Path | What it is | Who writes it |
|---|---|---|
| [`FINDINGS.md`](FINDINGS.md) | Reviewed findings, each labelled PROVEN, ALLEGATION, HYPOTHESIS or OPEN QUESTION, with primary-source links | Curated review only |
| [`LEADS.md`](LEADS.md) | Mechanical leads from seven written rules (R1–R7); reasons to look closer, not conclusions | Generated every run |
| [`divisions/`](divisions/) | One page per division: scope, standing questions, watched entities, records from the last 30 days | Generated every run |
| `ledger/YYYY-MM.jsonl` | Append-only evidence ledger: one JSON line per document, first-seen time in UTC and Asia/Jerusalem | Generated, never rewritten |
| `runs/YYYY-MM.jsonl` | One line per run: which sources succeeded, failed, how many new records | Generated |
| [`STATUS.md`](STATUS.md) | Health of every source, consecutive failures | Generated |
| `config/` | Divisions, watched entities, source queries. Change these to change the investigation | Versioned with the ledger |
| `accountability/`, `run.py`, `tests/` | The collector: Python standard library only | Code |

## The six divisions

| | Division | Follows |
|---|---|---|
| D1 | [Corporate power and antitrust](divisions/01-corporate-power-antitrust/) | Mergers, minority stakes, exclusionary conduct, how reviews end |
| D2 | [AI infrastructure accountability](divisions/02-ai-infrastructure/) | Model developers, chips, compute, circular financing, public money |
| D3 | [Financial conglomerates](divisions/03-financial-conglomerates/) | Banks, asset managers, private credit, payment networks, complaint data |
| D4 | [Cloud and data gatekeepers](divisions/04-cloud-data-gatekeepers/) | Hyperscalers, search, app stores, data brokers, credit bureaus |
| D5 | [Essential services concentration](divisions/05-essential-services/) | Power and grid (incl. data-centre load), telecom, health insurers, PBMs |
| D6 | [Regulatory capture and consumer protection](divisions/06-regulatory-capture-consumer-protection/) | Lobbying, rulemaking and its reversal, enforcement closures, redress |

## Sources (all free, no API keys, no proprietary services)

| Adapter | Primary source | Document class |
|---|---|---|
| `sec-edgar-filings` | SEC EDGAR filings by ~60 watched public companies (10-K/Q, 8-K with item labels, S-1, 424B4, 13D, 13Gs *about* the company, merger filings) | regulatory filing |
| `sec-edgar-fulltext` | EDGAR full-text search: watched names in *other* companies' filings, and Form D for OpenAI/Anthropic vehicles | regulatory filing |
| `federal-register` | Federal Register API: FTC, DOJ Antitrust, BIS, Fed/OCC/FDIC/SEC, FERC, FCC, CFPB | regulator notice |
| `doj-press` | DOJ press-release API: Antitrust Division always; Civil/Consumer Protection when on-topic | regulator statement |
| `uk-cma` | GOV.UK search API, Competition and Markets Authority | regulator statement |
| `rss-feeds` | FTC (all + competition), Federal Reserve enforcement, GAO reports, European Commission, OpenAI news, NVIDIA news | mixed, labelled per feed |
| `company-sitemaps` | Anthropic news (via sitemap; Anthropic publishes no RSS) | company statement |
| `courtlistener-recap` | Federal dockets naming watched entities as parties (CourtListener public feed) | court record |
| `lda-lobbying` | Lobbying Disclosure Act filings (LDA.gov API) | lobbying disclosure |
| `usaspending-awards` | Federal contracts (USAspending.gov API) | government award |
| `cfpb-complaints` | CFPB Consumer Complaint Database, monthly volume by company | complaint database (allegations) |

Every ledger record carries `what_this_shows`, a fixed sentence describing what its class of document can and cannot establish. For example, a regulator's announced complaint is an allegation until adjudicated, and an obligated federal award is not money paid. `title_signal` is a headline heuristic for triage, never a finding.

## Schedule

GitHub Actions runs the collector at **08:17, 10:17, 14:17, 17:17, 20:17 and 23:17 Asia/Jerusalem** using GitHub's native schedule `timezone:` field. Daylight saving is handled by GitHub, so nothing depends on any device clock. Every record is stamped in UTC and Asia/Jerusalem. The workflow also runs when collector code or config changes, and can be run by hand (Actions → Corporate Accountability → Run workflow). Offline tests run before every collection; a failing test stops the run before anything is committed.

GitHub may delay scheduled runs or skip them under load; the ledger's first-seen times show when each run actually happened.

## Reproduce it

```sh
cd research/corporate-accountability
python3 -m unittest discover -s tests              # offline, no network
SEC_CONTACT=you@example.org python3 run.py         # live; SEC requires your contact address
SEC_CONTACT=you@example.org python3 run.py --only doj-press,uk-cma --no-write
```

Requires Python 3.9+ and nothing else. `SEC_CONTACT` is required by SEC's fair-access policy, which rejects anonymous and GitHub noreply addresses. In this repository the workflow uses the owner's public commit address unless a repository variable named `SEC_CONTACT` is set.

## Evidentiary rules

1. **Primary sources only** in the ledger: filings, dockets, regulator releases and notices, government data. Company statements are kept and labelled as claims.
2. **Clean URLs**: https, tracking parameters and fragments removed, canonical documents (EDGAR archive paths, not viewers).
3. **Nothing is fabricated or inferred into the ledger.** Titles come from the source; where a source has no title (Anthropic sitemap), the title says it was derived from the URL.
4. **PROVEN vs ALLEGATION vs HYPOTHESIS** is decided only in `FINDINGS.md`, by review against the document itself, never by the collector.
5. **Same rules for everyone.** Lookback windows, lead rules and source coverage do not vary by company.
6. **Append, don't rewrite.** Ledger lines are never edited. Corrections to findings are appended with a date.
7. **Absence is not evidence.** A source that returns nothing for a company in a window shows only that.

## Known gaps (method backlog)

- Passive 13G stakes that asset managers hold in other companies are skipped (thousands per quarter). Common-ownership analysis needs 13F holdings data; not yet built.
- The European Commission feed returns only its 10 latest press releases per fetch; six runs a day narrows the gap but does not close it.
- The DOJ adapter reads the 200 newest releases per run. That covers several days of DOJ output, but backfill before 2026-11-24 is thin.
- CourtListener coverage is limited to dockets someone has added to RECAP, and to case names. Cases where a watched firm is a non-party are missed.
- No state-level sources yet (state AGs, public utility commissions), although D5 matters most there.

## Origin

ChatGPT committed the first collector and workflow on 2026-11-24 (commit `bc4803e`). Claude inspected and tested them, then replaced both. Five of the nine original sources failed (FTC 404; DOJ, CFPB, SEC and GAO 403). The HTML pages were hashed whole, so a change could not say what changed. Anthropic was not monitored. A delayed scheduled run was silently skipped by an exact-hour gate. The replacement keeps the original intent (scheduled, public, Israel-time windows) and the original's FTC, Federal Reserve, OpenAI, NVIDIA, SEC, DOJ, CFPB and GAO coverage, through endpoints that work.
