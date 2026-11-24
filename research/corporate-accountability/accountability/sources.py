"""Source adapters. Each takes a Context and returns a list of records.

Every adapter applies the same lookback window to every entity it covers, so no company
gets a longer or shorter memory than another.
"""
from __future__ import annotations

import datetime as dt
import email.utils
import os
import re
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

from .core import (CONTACT, FetchError, Matcher, clean_url, fetch, fetch_json, make_record,
                   post_json, strip_html)

ATOM = "{http://www.w3.org/2005/Atom}"


@dataclass
class Context:
    now: dt.datetime
    matcher: Matcher
    entities: list[dict]
    sources: dict
    state: dict = field(default_factory=dict)

    def since(self, days: int) -> dt.datetime:
        return self.now - dt.timedelta(days=days)

    def entity(self, eid: str) -> dict:
        return next(e for e in self.entities if e["id"] == eid)


def _parse_date(text: str | None) -> dt.datetime | None:
    if not text:
        return None
    text = text.strip()
    try:
        d = email.utils.parsedate_to_datetime(text)
    except (TypeError, ValueError):
        try:
            d = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            try:
                d = dt.datetime.strptime(text[:10], "%Y-%m-%d")
            except ValueError:
                return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return d


def _iso_date(d: dt.datetime | None) -> str | None:
    return d.date().isoformat() if d else None


def _require_sec_contact():
    if not CONTACT:
        raise FetchError("SEC_CONTACT is not set; SEC refuses requests without a contact address")


# ------------------------------------------------------------------ SEC EDGAR
def _ticker_map() -> dict:
    data = fetch_json("https://www.sec.gov/files/company_tickers.json")
    return {v["ticker"]: str(v["cik_str"]) for v in data.values()}


def sec_submissions(ctx: Context) -> list[dict]:
    """New filings of interest made BY each watched public entity."""
    _require_sec_contact()
    forms = set(ctx.sources["sec_forms_of_interest"])
    labels = ctx.sources["sec_8k_item_labels"]
    cutoff = ctx.since(ctx.sources["sec_lookback_days"]).date().isoformat()
    tickers = None
    out = []
    for ent in ctx.entities:
        if ent["kind"] != "public" or not ent.get("ticker"):
            continue
        cik = ent.get("cik")
        if not cik:
            tickers = tickers or _ticker_map()
            cik = tickers.get(ent["ticker"])
            if not cik:
                continue
        data = fetch_json(f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json")
        rec = data["filings"]["recent"]
        for i, form in enumerate(rec["form"]):
            filed = rec["filingDate"][i]
            if filed < cutoff:
                break  # newest first
            if form not in forms:
                continue
            # Asset managers file thousands of passive 13G stakes; those are tracked separately (see README).
            acc = rec["accessionNumber"][i]
            # Passive 13G stakes the entity holds in OTHER companies are skipped (thousands of them);
            # 13Gs filed by others ABOUT the entity are kept: they show who owns it.
            if "13G" in form and int(acc.split("-")[0]) == int(cik):
                continue
            doc = rec["primaryDocument"][i]
            items = [x for x in (rec.get("items", [""] * len(rec["form"]))[i] or "").split(",") if x]
            item_text = "; ".join(f"Item {x}: {labels.get(x, '')}".rstrip(": ") for x in items)
            url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-', '')}/{doc}"
            title = f"{data['name']} filed {form}" + (f" ({item_text})" if item_text else "")
            out.append(make_record(
                source="sec-edgar-filings", publisher="U.S. Securities and Exchange Commission (EDGAR)",
                source_class="regulatory-filing", title=title, url=url, published=filed,
                key=acc, matcher=ctx.matcher, entities=[ent["id"]], divisions=ent["divisions"],
                meta={"form": form, "accession": acc, "cik": str(int(cik)), "items": items,
                      "report_date": rec["reportDate"][i] or None,
                      "index_url": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-', '')}/{acc}-index.htm"}))
    return out


def sec_fulltext(ctx: Context) -> list[dict]:
    """Watched names appearing in OTHER companies' filings (investors, partners, suppliers)."""
    _require_sec_contact()
    start = ctx.since(ctx.sources["sec_lookback_days"]).date().isoformat()
    end = ctx.now.date().isoformat()
    cik_to_ent = {str(int(e["cik"])): e["id"] for e in ctx.entities if e.get("cik")}
    out = []
    for q in ctx.sources["sec_fulltext"]:
        params = urllib.parse.urlencode({"q": q["q"], "forms": q["forms"], "dateRange": "custom",
                                         "startdt": start, "enddt": end})
        data = fetch_json(f"https://efts.sec.gov/LATEST/search-index?{params}")
        named = set(ctx.matcher.entities_in(q["q"]))
        by_filing = {}
        for hit in data.get("hits", {}).get("hits", []):
            s = hit["_source"]
            adsh = s["adsh"]
            filer_ents = {cik_to_ent.get(str(int(c))) for c in s.get("ciks", [])} - {None}
            if named and named <= filer_ents:
                continue  # a company naming itself is covered by sec_submissions
            by_filing.setdefault(adsh, (s, filer_ents, hit["_id"].split(":", 1)[-1]))
        for adsh, (s, filer_ents, fname) in by_filing.items():
            cik = str(int(s["ciks"][0]))
            filer = re.sub(r"\s+\(CIK.*$", "", s["display_names"][0]).strip()
            url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh.replace('-', '')}/{adsh}-index.htm"
            out.append(make_record(
                source="sec-edgar-fulltext", publisher="U.S. Securities and Exchange Commission (EDGAR full-text search)",
                source_class="regulatory-filing",
                title=f"{filer} {s['form']} filed {s['file_date']} contains {q['q']}",
                url=url, published=s["file_date"], key=f"{adsh}|{q['q']}|{q['forms']}", matcher=ctx.matcher,
                entities=sorted(named | filer_ents), divisions=[q["division"]],
                meta={"form": s["form"], "accession": adsh, "query": q["q"], "first_matching_document": fname,
                      "document_url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh.replace('-', '')}/{fname}"}))
    return out


# ------------------------------------------------------------------ Federal Register
def federal_register(ctx: Context) -> list[dict]:
    start = ctx.since(ctx.sources.get("federal_register_lookback_days", 14)).date().isoformat()
    pattern = ctx.sources.get("federal_register_exclude_title_regex")
    exclude = re.compile(pattern) if pattern else None
    out = []
    for q in ctx.sources["federal_register"]:
        params = [("per_page", "100"), ("order", "newest"), ("conditions[publication_date][gte]", start)]
        if q["term"]:
            params.append(("conditions[term]", q["term"]))
        params += [("conditions[agencies][]", a) for a in q["agencies"]]
        params += [("fields[]", f) for f in ("title", "html_url", "publication_date", "type", "agencies",
                                             "abstract", "document_number", "action")]
        data = fetch_json("https://www.federalregister.gov/api/v1/documents.json?" + urllib.parse.urlencode(params))
        for d in data.get("results") or []:
            if exclude and exclude.search(d["title"] or ""):
                continue
            agencies = ", ".join(a.get("name") or a.get("raw_name", "") for a in d.get("agencies") or [])
            out.append(make_record(
                source="federal-register", publisher=f"Federal Register ({agencies})",
                source_class="regulator-notice", title=f"{d['type']}: {d['title']}", url=d["html_url"],
                published=d["publication_date"], key=d["document_number"], matcher=ctx.matcher,
                summary=d.get("abstract") or d.get("action") or "", divisions=[q["division"]],
                meta={"document_number": d["document_number"], "agencies": agencies, "type": d["type"]}))
    return out


# ------------------------------------------------------------------ DOJ
def doj(ctx: Context) -> list[dict]:
    conf = ctx.sources["doj"]
    wanted = set(conf["components"])
    cutoff = ctx.since(21)
    out, seen = [], set()
    for page in range(conf["pages"]):
        data = fetch_json(f"https://www.justice.gov/api/v1/press_releases.json?pagesize=50&page={page}&sort=date&direction=DESC")
        for r in data.get("results", []):
            if r["uuid"] in seen:
                continue
            seen.add(r["uuid"])
            comps = [c["name"] for c in r.get("component") or []]
            text = f"{r['title']} {strip_html(r.get('teaser', ''))}"
            ents = ctx.matcher.entities_in(text)
            antitrust = "Antitrust Division" in comps
            topical = wanted & set(comps) and set(ctx.matcher.divisions_in(text)) & {"D3", "D4", "D6"}
            if not (antitrust or topical or ents):
                continue
            published = dt.datetime.fromtimestamp(int(r["date"]), dt.timezone.utc) if r.get("date") else None
            if published and published < cutoff:
                continue
            divs = ["D1"] if "Antitrust Division" in comps else []
            if wanted & set(comps) - {"Antitrust Division"}:
                divs.append("D6")
            out.append(make_record(
                source="doj-press", publisher="U.S. Department of Justice", source_class="regulator-statement",
                title=r["title"], url=r["url"], published=_iso_date(published), key=r["uuid"],
                summary=r.get("teaser", ""), matcher=ctx.matcher, divisions=divs,
                meta={"components": comps, "number": r.get("number")}))
    return out


# ------------------------------------------------------------------ RSS / Atom / sitemaps
def _feed_items(xml_bytes: bytes):
    root = ET.fromstring(xml_bytes)
    for item in root.iter("item"):
        yield (item.findtext("title") or "", item.findtext("link") or "",
               item.findtext("pubDate") or item.findtext("{http://purl.org/dc/elements/1.1/}date"),
               item.findtext("description") or "")
    for entry in root.iter(f"{ATOM}entry"):
        link = entry.find(f"{ATOM}link")
        yield (entry.findtext(f"{ATOM}title") or "", link.get("href") if link is not None else "",
               entry.findtext(f"{ATOM}published") or entry.findtext(f"{ATOM}updated"),
               entry.findtext(f"{ATOM}summary") or "")


def rss(ctx: Context) -> list[dict]:
    cutoff = ctx.since(21)
    out, errors = [], []
    for feed in ctx.sources["rss"]:
        try:
            body = fetch(feed["url"])
        except FetchError as exc:
            errors.append(f"{feed['id']}: {exc}")
            continue
        for title, link, date, desc in _feed_items(body):
            when = _parse_date(date)
            if when and when < cutoff:
                continue
            if any(x in (link or "") for x in feed.get("path_exclude", [])):
                continue
            text = f"{title} {strip_html(desc)}"
            if feed["filter"] == "division-or-entity" and not (ctx.matcher.divisions_in(text) or ctx.matcher.entities_in(text)):
                continue
            out.append(make_record(
                source=feed["id"], publisher=feed["publisher"], source_class=feed["source_class"],
                title=title, url=link, published=_iso_date(when), matcher=ctx.matcher, summary=desc,
                divisions=feed["divisions"], entities=[feed["entity"]] if feed.get("entity") else []))
    if errors and not out:
        raise FetchError("; ".join(errors))
    ctx.state.setdefault("partial_errors", {})["rss"] = errors
    return out


def sitemaps(ctx: Context) -> list[dict]:
    out = []
    known_all = ctx.state.setdefault("sitemap_known_urls", {})
    for sm in ctx.sources["sitemaps"]:
        root = ET.fromstring(fetch(sm["url"]))
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        baseline = sm["id"] not in known_all
        known = set(known_all.get(sm["id"], []))
        for u in root.iter(f"{ns}url"):
            loc = clean_url(u.findtext(f"{ns}loc") or "")
            if sm["path_contains"] not in loc or loc in known:
                continue
            known.add(loc)
            if baseline:
                continue  # first sighting of the whole sitemap: remember, do not report as new
            lastmod = u.findtext(f"{ns}lastmod")
            slug = loc.rstrip("/").rsplit("/", 1)[-1]
            out.append(make_record(
                source=sm["id"], publisher=sm["publisher"], source_class=sm["source_class"],
                title=f"{sm['publisher']} published a new page: {slug.replace('-', ' ')} (title derived from URL)",
                url=loc, published=None, matcher=ctx.matcher, divisions=sm["divisions"], entities=[sm["entity"]],
                summary=f"New URL first listed in the sitemap; sitemap lastmod {lastmod} is a modification time, not a publication date.",
                meta={"lastmod": lastmod}))
        known_all[sm["id"]] = sorted(known)
    return out


def courtlistener(ctx: Context) -> list[dict]:
    conf = ctx.sources["courtlistener"]
    out, seen = [], set()
    for eid, term in conf["case_name_terms"].items():
        q = urllib.parse.quote(f"caseName:({term})")
        body = fetch(f"https://www.courtlistener.com/feed/search/?q={q}&type=r&order_by=dateFiled%20desc", pause=2.0)
        if not body.strip():
            continue
        for title, link, date, summary in _feed_items(body):
            m = re.search(r"/docket/(\d+)/(?:\d+/)?([^/#]+)/", link or "")
            if not m or m.group(1) in seen:
                continue
            seen.add(m.group(1))
            docket_url = f"https://www.courtlistener.com/docket/{m.group(1)}/{m.group(2)}/"
            out.append(make_record(
                source="courtlistener-recap", publisher="CourtListener / RECAP (Free Law Project), U.S. federal court dockets",
                source_class="court-record", title=f"Federal case: {title}", url=docket_url,
                published=_iso_date(_parse_date(date)), key=m.group(1), matcher=ctx.matcher,
                entities=[eid], divisions=[],
                meta={"docket_id": m.group(1), "latest_entry_seen": clean_url(link)}))
    return out


# ------------------------------------------------------------------ UK CMA
def cma(ctx: Context) -> list[dict]:
    cutoff = ctx.since(21)
    params = urllib.parse.urlencode([("filter_organisations", "competition-and-markets-authority"),
                                     ("order", "-public_timestamp"), ("count", ctx.sources["cma"]["count"]),
                                     ("fields", "title"), ("fields", "link"), ("fields", "public_timestamp"),
                                     ("fields", "format"), ("fields", "description")])
    data = fetch_json(f"https://www.gov.uk/api/search.json?{params}")
    out = []
    for r in data.get("results", []):
        when = _parse_date(r.get("public_timestamp"))
        if when and when < cutoff:
            continue
        out.append(make_record(
            source="uk-cma", publisher="UK Competition and Markets Authority (GOV.UK)",
            source_class="regulator-statement", title=r["title"], url="https://www.gov.uk" + r["link"],
            published=_iso_date(when), matcher=ctx.matcher, summary=r.get("description") or "",
            divisions=["D1"], meta={"format": r.get("format")}))
    return out


# ------------------------------------------------------------------ Lobbying (LDA)
def lda(ctx: Context) -> list[dict]:
    after = ctx.since(ctx.sources["lda"]["lookback_days"]).date().isoformat()
    out = []
    for ent in ctx.entities:
        for client in ent.get("lda_clients") or []:
            url = "https://lda.gov/api/v1/filings/?" + urllib.parse.urlencode(
                {"client_name": client, "filing_dt_posted_after": after})
            while url:
                data = fetch_json(url, pause=4.0)
                for f in data.get("results", []):
                    cname = f["client"]["name"]
                    if any(x.lower() in cname.lower() for x in ent.get("lda_exclude") or []):
                        continue
                    if ent["id"] not in ctx.matcher.entities_in(cname):
                        continue  # substring hit on an unrelated client
                    amount = f.get("income") or f.get("expenses")
                    issues = sorted({a.get("general_issue_code_display") for a in f.get("lobbying_activities") or []} - {None})
                    title = (f"Lobbying: {cname} — {f['filing_type_display']} {f['filing_year']}, "
                             f"registrant {f['registrant']['name']}" + (f", reported ${float(amount):,.0f}" if amount else ""))
                    out.append(make_record(
                        source="lda-lobbying", publisher="U.S. Lobbying Disclosure Act filings (LDA.gov)",
                        source_class="lobbying-disclosure", title=title, url=f["filing_document_url"],
                        published=(f.get("dt_posted") or "")[:10] or None, key=f["filing_uuid"],
                        matcher=ctx.matcher, entities=[ent["id"]], divisions=["D6"],
                        summary="Issues: " + "; ".join(issues),
                        meta={"filing_uuid": f["filing_uuid"], "client": cname, "registrant": f["registrant"]["name"],
                              "filing_type": f["filing_type"], "amount_usd": amount, "issues": issues,
                              "api_url": f["url"]}))
                url = data.get("next")
    return out


# ------------------------------------------------------------------ Federal awards
def usaspending(ctx: Context) -> list[dict]:
    conf = ctx.sources["usaspending"]
    start = ctx.since(conf["lookback_days"]).date().isoformat()
    out = []
    for ent in ctx.entities:
        for name in ent.get("usaspending_recipients") or []:
            payload = {"filters": {"recipient_search_text": [name], "award_type_codes": ["A", "B", "C", "D"],
                                   "time_period": [{"start_date": start, "end_date": ctx.now.date().isoformat()}]},
                       "fields": ["Award ID", "Recipient Name", "Award Amount", "Awarding Agency",
                                  "Awarding Sub Agency", "Start Date", "Last Modified Date", "Description", "generated_internal_id"],
                       "limit": 50, "sort": "Award Amount", "order": "desc"}
            data = post_json("https://api.usaspending.gov/api/v2/search/spending_by_award/", payload)
            for a in data.get("results", []):
                if ent["id"] not in ctx.matcher.entities_in(a["Recipient Name"] or ""):
                    continue
                amt = a.get("Award Amount") or 0
                if amt < conf["min_amount"]:
                    continue
                out.append(make_record(
                    source="usaspending-awards", publisher="USAspending.gov (U.S. Treasury)",
                    source_class="government-award",
                    title=f"Federal contract: {a['Awarding Agency']} to {a['Recipient Name']}, ${amt:,.0f} (award {a['Award ID']})",
                    url=f"https://www.usaspending.gov/award/{a['generated_internal_id']}",
                    published=a.get("Start Date"), key=a["generated_internal_id"], matcher=ctx.matcher,
                    summary=a.get("Description") or "", entities=[ent["id"]], divisions=["D2"] if "D2" in ent["divisions"] else [],
                    meta={"amount_usd": amt, "agency": a["Awarding Agency"], "sub_agency": a.get("Awarding Sub Agency"),
                          "award_id": a["Award ID"], "start_date": a.get("Start Date"),
                          "last_modified": a.get("Last Modified Date"),
                          "note": f"Award had activity within the {conf['lookback_days']}-day window; the amount is the obligated total, not money paid."}))
    return out


# ------------------------------------------------------------------ CFPB complaints
def cfpb(ctx: Context) -> list[dict]:
    """Once per month: complaint volume by company for the previous calendar month."""
    first_this = ctx.now.date().replace(day=1)
    last_prev = first_this - dt.timedelta(days=1)
    month = last_prev.strftime("%Y-%m")
    if ctx.state.get("cfpb_month_recorded") == month:
        return []
    lo, hi = last_prev.replace(day=1).isoformat(), last_prev.isoformat()
    data = fetch_json("https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?"
                      + urllib.parse.urlencode({"size": 0, "date_received_min": lo, "date_received_max": hi}))

    def buckets(node):
        if isinstance(node, dict):
            if "buckets" in node:
                return node["buckets"]
            for v in node.values():
                b = buckets(v)
                if b is not None:
                    return b
        return None

    top = (buckets(data["aggregations"]["company"]) or [])[: ctx.sources["cfpb"]["top_n"]]
    total = data["hits"]["total"]["value"]
    rows = [{"company": b["key"], "complaints": b["doc_count"]} for b in top]
    ents = sorted({e for r in rows for e in ctx.matcher.entities_in(r["company"])})
    ctx.state["cfpb_month_recorded"] = month
    url = ("https://www.consumerfinance.gov/data-research/consumer-complaints/search/?"
           + urllib.parse.urlencode({"date_received_min": lo, "date_received_max": hi, "tab": "Trends"}))
    lead = ", ".join(f"{r['company']} {r['complaints']:,}" for r in rows[:5])
    return [make_record(
        source="cfpb-complaints", publisher="U.S. Consumer Financial Protection Bureau, Consumer Complaint Database",
        source_class="complaint-database", title=f"CFPB complaints received {month}: {total:,} total; most-named companies: {lead}",
        url=url, published=hi, key=month, matcher=ctx.matcher, entities=ents, divisions=["D3", "D4", "D6"],
        meta={"month": month, "total": total, "top_companies": rows,
              "caveat": "Counts as retrieved; complaints published later raise them. Unverified allegations; volume scales with customer base."})]


ADAPTERS = {
    "sec-edgar-filings": sec_submissions,
    "sec-edgar-fulltext": sec_fulltext,
    "federal-register": federal_register,
    "doj-press": doj,
    "uk-cma": cma,
    "rss-feeds": rss,
    "company-sitemaps": sitemaps,
    "courtlistener-recap": courtlistener,
    "lda-lobbying": lda,
    "usaspending-awards": usaspending,
    "cfpb-complaints": cfpb,
}
