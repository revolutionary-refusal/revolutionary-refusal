"""Shared plumbing: HTTP, clean URLs, time, entity/division matching, records, ledger.

Standard library only, so the method can be reproduced with nothing but Python 3.9+.
"""
from __future__ import annotations

import datetime as dt
import gzip
import hashlib
import json
import os
import pathlib
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config"
LEDGER = ROOT / "ledger"
RUNS = ROOT / "runs"
STATE = ROOT / "state"
JERUSALEM = ZoneInfo("Asia/Jerusalem")
MAX_BYTES = 8_000_000

# SEC's fair-access policy requires a real contact address in the User-Agent; it rejects
# anonymous and GitHub noreply addresses. Anyone reproducing this sets their own SEC_CONTACT.
CONTACT = os.environ.get("SEC_CONTACT", "").strip()
USER_AGENT = f"revolutionary-refusal-accountability/2.0 {CONTACT or '(no contact set)'}"

TRACKING_PARAMS = re.compile(r"^(utm_|fbclid$|gclid$|mc_cid$|mc_eid$|ref$|ref_src$|cmpid$|_hs)", re.I)


# ---------------------------------------------------------------- time
def now_utc() -> dt.datetime:
    override = os.environ.get("ACCOUNTABILITY_NOW")  # tests only
    if override:
        return dt.datetime.fromisoformat(override).astimezone(dt.timezone.utc)
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def stamp(moment: dt.datetime) -> dict:
    return {
        "utc": moment.astimezone(dt.timezone.utc).isoformat(),
        "jerusalem": moment.astimezone(JERUSALEM).isoformat(),
    }


# ---------------------------------------------------------------- HTTP
class FetchError(Exception):
    pass


def fetch(url: str, *, data: bytes | None = None, headers: dict | None = None,
          retries: int = 3, timeout: int = 30, pause: float = 0.15) -> bytes:
    """GET (or POST when data is given) with retries, backoff and a size cap."""
    hdrs = {"User-Agent": USER_AGENT, "Accept-Encoding": "gzip", "Accept": "*/*"}
    hdrs.update(headers or {})
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read(MAX_BYTES + 1)
                if len(body) > MAX_BYTES:
                    raise FetchError(f"response over {MAX_BYTES} bytes")
                if resp.headers.get("Content-Encoding") == "gzip":
                    body = gzip.decompress(body)
            time.sleep(pause)  # stay well under every published rate limit
            return body
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code in (400, 401, 403, 404, 405, 410):
                break  # retrying will not help
            time.sleep(2 ** attempt * 2)
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
            last = exc
            time.sleep(2 ** attempt * 2)
    raise FetchError(f"{type(last).__name__}: {last}")


def fetch_json(url: str, **kw):
    kw.setdefault("headers", {}).setdefault("Accept", "application/json")
    return json.loads(fetch(url, **kw).decode("utf-8"))


def post_json(url: str, payload: dict, **kw):
    kw.setdefault("headers", {}).update({"Content-Type": "application/json", "Accept": "application/json"})
    return json.loads(fetch(url, data=json.dumps(payload).encode(), **kw).decode("utf-8"))


# ---------------------------------------------------------------- URLs
def clean_url(url: str) -> str:
    """Canonical public URL: https, no tracking parameters, no fragment."""
    url = (url or "").strip()
    if not url:
        return url
    parts = urllib.parse.urlsplit(url)
    scheme = "https" if parts.scheme in ("http", "https", "") else parts.scheme
    query = [(k, v) for k, v in urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
             if not TRACKING_PARAMS.match(k)]
    return urllib.parse.urlunsplit((scheme, parts.netloc.lower(), parts.path,
                                    urllib.parse.urlencode(query), ""))


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = (text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&quot;", '"')
            .replace("&#039;", "'").replace("&rsquo;", "’").replace("&lt;", "<").replace("&gt;", ">"))
    return re.sub(r"\s+", " ", text).strip()


# ---------------------------------------------------------------- config & matching
def load_config(name: str) -> dict:
    return json.loads((CONFIG / name).read_text())


class Matcher:
    def __init__(self, entities: list[dict], divisions: list[dict]):
        self.entities = entities
        self.divisions = divisions
        self._ent = []
        for e in entities:
            pats = []
            if e.get("aliases"):
                pats.append(re.compile(r"(?<![A-Za-z0-9])(" + "|".join(re.escape(a) for a in e["aliases"]) + r")(?![A-Za-z0-9])", re.I))
            if e.get("aliases_case_sensitive"):
                pats.append(re.compile(r"(?<![A-Za-z0-9])(" + "|".join(re.escape(a) for a in e["aliases_case_sensitive"]) + r")(?![A-Za-z0-9])"))
            self._ent.append((e["id"], pats))
        self._div = [(d["id"], [re.compile(k) for k in d["keywords"]]) for d in divisions]

    def entities_in(self, text: str) -> list[str]:
        return [eid for eid, pats in self._ent if any(p.search(text or "") for p in pats)]

    def divisions_in(self, text: str) -> list[str]:
        return [did for did, pats in self._div if any(p.search(text or "") for p in pats)]


# ---------------------------------------------------------------- records
SOURCE_CLASS_STATUS = {
    # What a record of each class can and cannot show, stated once and attached to every record.
    "regulatory-filing": "self-reported by the filer under legal liability; establishes what the filer stated, not that it is complete",
    "regulator-statement": "the regulator's own account; an announced complaint or charge is an allegation until adjudicated or admitted",
    "regulator-notice": "official notice published in the Federal Register; establishes that the agency took the stated procedural step",
    "court-record": "court docket entry; pleadings are allegations, orders and judgments are rulings",
    "government-award": "federal spending record; establishes an obligated award, not money actually paid or work performed",
    "lobbying-disclosure": "filed under the Lobbying Disclosure Act; establishes reported spending and issues, which may be understated",
    "complaint-database": "unverified consumer complaints; volume reflects company size as well as conduct; each complaint is an allegation",
    "oversight-report": "audit or oversight finding by a government body; stronger than an allegation, still subject to agency response",
    "company-statement": "the company's own public claim; not independent evidence of its truth",
}

TITLE_SIGNALS = [
    ("complaint-or-charge (allegation)", re.compile(r"(?i)\b(sues|lawsuit|complaint|alleg|charg(es|ed)|indict|files suit|challenges?|seeks to block)\b")),
    ("settlement-or-order", re.compile(r"(?i)\b(settle|consent (order|decree|agreement)|final (order|judgment)|agrees to pay|ordered to pay|penalt|fine[sd]?\b|refunds?)\b")),
    ("ruling", re.compile(r"(?i)\b(court (rules|finds)|verdict|judge (rules|finds)|found liable|convicted)\b")),
    ("closure-or-clearance", re.compile(r"(?i)\b(clos(es|ing|ed)( of)? (its |the )?investigation|clears?|early termination|no further action|terminat(es|ed) (its )?review)\b")),
    ("rulemaking", re.compile(r"(?i)\b(proposed rule|final rule|rulemaking|request for (comment|information))\b")),
    ("market-investigation", re.compile(r"(?i)\b(market (study|investigation)|strategic market status|opens? (an )?investigation|probe)\b")),
]


def title_signal(title: str) -> str | None:
    """Heuristic label from the headline only. Shown as a hint for reviewers, never as a finding."""
    for label, pat in TITLE_SIGNALS:
        if pat.search(title or ""):
            return label
    return None


def record_id(source: str, key: str) -> str:
    return hashlib.sha256(f"{source}|{key}".encode()).hexdigest()[:20]


def make_record(*, source: str, publisher: str, source_class: str, title: str, url: str,
                published: str | None, matcher: Matcher, key: str | None = None,
                summary: str = "", divisions=(), entities=(), meta: dict | None = None) -> dict:
    url = clean_url(url)
    text = f"{title} {summary}"
    ents = sorted(set(entities) | set(matcher.entities_in(text)))
    divs = set(divisions) | set(matcher.divisions_in(text))
    if not divs and ents:  # e.g. a court caption with no topical words: file it under its entities' divisions
        divs = {d for e in matcher.entities if e["id"] in ents for d in e["divisions"]}
    divs = sorted(divs)
    return {
        "id": record_id(source, key or url),
        "source": source,
        "publisher": publisher,
        "source_class": source_class,
        "what_this_shows": SOURCE_CLASS_STATUS[source_class],
        "title": strip_html(title)[:400],
        "url": url,
        "published": published,
        "entities": ents,
        "divisions": divs,
        "title_signal": title_signal(title),
        "summary": strip_html(summary)[:600],
        "meta": meta or {},
    }


# ---------------------------------------------------------------- ledger
def load_seen() -> set[str]:
    seen = set()
    for f in sorted(LEDGER.glob("*.jsonl")):
        for line in f.read_text().splitlines():
            if line.strip():
                seen.add(json.loads(line)["id"])
    return seen


def load_ledger(since: dt.datetime | None = None) -> list[dict]:
    out = []
    for f in sorted(LEDGER.glob("*.jsonl")):
        for line in f.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if since is None or dt.datetime.fromisoformat(r["first_seen"]["utc"]) >= since:
                out.append(r)
    return out


def append_ledger(records: list[dict], moment: dt.datetime) -> pathlib.Path:
    LEDGER.mkdir(exist_ok=True)
    path = LEDGER / f"{moment.astimezone(JERUSALEM):%Y-%m}.jsonl"
    with path.open("a", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    return path
