"""Deterministic lead selection.

A lead is a reason to look closer, never a conclusion. Each rule is written down here,
applies identically to every entity, and cites the ledger records that triggered it.
"""
from __future__ import annotations

import collections
import datetime as dt

STRUCTURE_FORMS = {"SC 13D", "SC 13D/A", "SCHEDULE 13D", "S-4", "425", "DEFM14A", "S-1", "S-1/A", "424B4"}
STRUCTURE_ITEMS = {"1.01", "1.02", "2.01", "2.06", "4.02", "5.01"}
STRONG_SIGNALS = {"complaint-or-charge (allegation)", "settlement-or-order", "ruling", "market-investigation"}

RULES = {
    "R1": "A regulator or oversight body published something naming a watched entity",
    "R2": "A federal court case naming a watched entity as a party was first observed",
    "R3": "A watched entity filed an ownership, control, offering or material-agreement disclosure",
    "R4": "A watched entity was named in another company's SEC filing (dependency or investment disclosure)",
    "R5": "A federal contract of $1M or more to a watched entity was first observed",
    "R6": "A watched entity registered a new lobbying relationship or reported $500k+ in a quarter",
    "R7": "The same entity surfaced in four or more divisions within 30 days (convergence; low priority, large firms trip it often)",
}


def score_record(r: dict) -> list[tuple[str, int]]:
    hits = []
    cls, meta = r["source_class"], r.get("meta", {})
    if not r["entities"]:
        return hits
    if cls in ("regulator-statement", "regulator-notice", "oversight-report"):
        hits.append(("R1", 3 + (2 if r.get("title_signal") in STRONG_SIGNALS else 0)))
    if cls == "court-record":
        hits.append(("R2", 2))
    if r["source"] == "sec-edgar-filings":
        if meta.get("form") in STRUCTURE_FORMS or STRUCTURE_ITEMS & set(meta.get("items") or []):
            hits.append(("R3", 3))
    if r["source"] == "sec-edgar-fulltext":
        hits.append(("R4", 2))
    if cls == "government-award" and (meta.get("amount_usd") or 0) >= 1_000_000:
        hits.append(("R5", 2 + (1 if meta["amount_usd"] >= 10_000_000 else 0)))
    if cls == "lobbying-disclosure":
        amt = float(meta.get("amount_usd") or 0)
        if meta.get("filing_type") == "RR":
            hits.append(("R6", 2))
        elif amt >= 500_000:
            hits.append(("R6", 1))
    return hits


def build_leads(records: list[dict], now: dt.datetime, window_days: int = 30, names: dict | None = None) -> list[dict]:
    names = names or {}
    since = now - dt.timedelta(days=window_days)
    recent = [r for r in records if dt.datetime.fromisoformat(r["first_seen"]["utc"]) >= since]
    leads = []
    for r in recent:
        for rule, score in score_record(r):
            leads.append({"rule": rule, "score": score, "entities": r["entities"], "records": [r["id"]],
                          "title": r["title"], "url": r["url"], "date": min(r.get("published") or "9999", r["first_seen"]["utc"][:10]),
                          "signal": r.get("title_signal"), "source_class": r["source_class"]})
    divs = collections.defaultdict(set)
    ids = collections.defaultdict(list)
    for r in recent:
        for e in r["entities"]:
            divs[e] |= set(r["divisions"])
            ids[e].append(r["id"])
    for e, ds in divs.items():
        if len(ds) >= 4:
            leads.append({"rule": "R7", "score": 1, "entities": [e], "records": ids[e][-50:],
                          "title": f"{names.get(e, e)} appears across {len(ds)} divisions: {', '.join(sorted(ds))} ({len(ids[e])} records)",
                          "url": "", "date": now.date().isoformat(), "signal": None, "source_class": "ledger"})
    leads.sort(key=lambda x: (x["score"], x["date"]), reverse=True)
    return leads
