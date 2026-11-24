"""Offline tests: no network. Run with  python3 -m unittest discover -s tests  from this folder."""
import datetime as dt
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from accountability import core, leads, report, sources  # noqa: E402

FIX = HERE / "fixtures"
NOW = dt.datetime(2026, 11, 23, 18, 0, tzinfo=dt.timezone.utc)
ENTITIES = core.load_config("entities.json")["entities"]
DIVISIONS = core.load_config("divisions.json")["divisions"]
SOURCES = core.load_config("sources.json")
M = core.Matcher(ENTITIES, DIVISIONS)


def ctx(state=None):
    return sources.Context(now=NOW, matcher=M, entities=ENTITIES, sources=SOURCES, state=state if state is not None else {})


class TestUrlsAndTime(unittest.TestCase):
    def test_clean_url_strips_tracking_and_fragment(self):
        self.assertEqual(core.clean_url("http://WWW.Example.org/a?utm_source=x&id=7&fbclid=1#top"),
                         "https://www.example.org/a?id=7")

    def test_stamp_uses_jerusalem_independent_of_host_clock(self):
        s = core.stamp(NOW)
        self.assertEqual(s["utc"], "2026-11-23T18:00:00+00:00")
        self.assertEqual(s["jerusalem"], "2026-11-23T20:00:00+02:00")  # IST in November
        summer = core.stamp(dt.datetime(2026, 7, 1, 18, tzinfo=dt.timezone.utc))
        self.assertTrue(summer["jerusalem"].endswith("+03:00"))  # IDT


class TestMatching(unittest.TestCase):
    def test_word_boundaries(self):
        self.assertNotIn("intel", M.entities_in("artificial intelligence services"))
        self.assertIn("intel", M.entities_in("Intel announced a foundry deal"))
        self.assertNotIn("visa", M.entities_in("student visa applications rose"))
        self.assertIn("visa", M.entities_in("Visa Inc. settles interchange claims"))

    def test_case_sensitive_aliases(self):
        self.assertIn("xai", M.entities_in("xAI raised capital"))
        self.assertNotIn("xai", M.entities_in("XAI Madison Equity Premium Income Fund"))

    def test_uppercase_registry_names_match(self):
        for name, eid in [("ANTHROPIC, PBC", "anthropic"), ("OPENAI OPCO, LLC", "openai"),
                          ("NVIDIA CORPORATION", "nvidia"), ("ORACLE AMERICA, INC.", "oracle"),
                          ("JPMORGAN CHASE & CO.", "jpmorgan"), ("TRANSUNION INTERMEDIATE HOLDINGS, INC.", "transunion")]:
            self.assertIn(eid, M.entities_in(name), name)

    def test_division_keywords(self):
        self.assertIn("D1", M.divisions_in("Justice Department closes investigation of merger"))
        self.assertIn("D5", M.divisions_in("FERC order on large load interconnection"))
        self.assertIn("D2", M.divisions_in("new AI data center"))

    def test_entity_fallback_divisions(self):
        r = core.make_record(source="t", publisher="p", source_class="court-record", title="Smith v. Oracle America, Inc.",
                             url="https://x.org/1", published=None, matcher=M)
        self.assertEqual(r["divisions"], ["D2", "D4"])


class TestEqualScrutiny(unittest.TestCase):
    """No corporate exemptions: the AI developers and NVIDIA get the same instruments."""

    def by(self, eid):
        return next(e for e in ENTITIES if e["id"] == eid)

    def test_big_three_symmetry(self):
        for eid in ("openai", "anthropic", "nvidia"):
            e = self.by(eid)
            self.assertTrue(e["lda_clients"], eid)
            self.assertTrue(e["usaspending_recipients"], eid)
            self.assertIn(eid, SOURCES["courtlistener"]["case_name_terms"], eid)
            self.assertIn("D2", e["divisions"])
            self.assertIn("D6", e["divisions"])
        feeds = {f.get("entity") for f in SOURCES["rss"]} | {s["entity"] for s in SOURCES["sitemaps"]}
        self.assertTrue({"openai", "anthropic", "nvidia"} <= feeds)

    def test_every_ai_developer_is_covered(self):
        for e in ENTITIES:
            if "ai-developer" in e["roles"]:
                self.assertTrue(e["cik"] or e["edgar_fulltext"], e["id"])
                self.assertTrue(e["lda_clients"], e["id"])

    def test_registry_integrity(self):
        ids = [e["id"] for e in ENTITIES]
        self.assertEqual(len(ids), len(set(ids)))
        valid = {d["id"] for d in DIVISIONS}
        self.assertEqual(len(valid), 6)
        for e in ENTITIES:
            self.assertTrue(e["divisions"] and set(e["divisions"]) <= valid, e["id"])
            if e["kind"] == "public":
                self.assertTrue(e["ticker"], e["id"])


class TestSignalsAndLeads(unittest.TestCase):
    def test_title_signal(self):
        self.assertEqual(core.title_signal("FTC Sues Amazon over Prime"), "complaint-or-charge (allegation)")
        self.assertEqual(core.title_signal("Bank agrees to pay $10 million penalty"), "settlement-or-order")
        self.assertEqual(core.title_signal("Statement on the Closing of Its Investigation"), "closure-or-clearance")
        self.assertIsNone(core.title_signal("Quarterly newsletter"))

    def _rec(self, **kw):
        base = core.make_record(source=kw.pop("source", "doj-press"), publisher="p",
                                source_class=kw.pop("source_class", "regulator-statement"),
                                title=kw.pop("title", "Justice Department sues NVIDIA"), url="https://x.org/a",
                                published="2026-11-20", matcher=M, meta=kw.pop("meta", {}), **kw)
        base["first_seen"] = core.stamp(NOW)
        return base

    def test_rules(self):
        self.assertEqual(leads.score_record(self._rec()), [("R1", 5)])
        f = self._rec(source="sec-edgar-filings", source_class="regulatory-filing", title="Anthropic, PBC filed 424B4",
                      meta={"form": "424B4", "items": []})
        self.assertEqual(leads.score_record(f), [("R3", 3)])
        a = self._rec(source="usaspending-awards", source_class="government-award", title="contract to ANTHROPIC, PBC",
                      meta={"amount_usd": 12_000_000})
        self.assertEqual(leads.score_record(a), [("R5", 3)])
        none = self._rec(title="Regulator newsletter")
        self.assertEqual(leads.score_record(none), [])

    def test_convergence(self):
        rs = [self._rec(title=t) for t in ("NVIDIA merger probe", "NVIDIA data center chips", "NVIDIA lobbying rule",
                                           "NVIDIA cloud privacy")]
        out = leads.build_leads(rs, NOW)
        self.assertTrue(any(l["rule"] == "R7" and l["entities"] == ["nvidia"] for l in out))


class TestAdaptersOffline(unittest.TestCase):
    def test_sitemap_baseline_then_new(self):
        one = (FIX / "sitemap_1.xml").read_bytes()
        two = (FIX / "sitemap_2.xml").read_bytes()
        state = {}
        with mock.patch.object(sources, "fetch", return_value=one):
            self.assertEqual(sources.sitemaps(ctx(state)), [])  # baseline: nothing reported
        with mock.patch.object(sources, "fetch", return_value=two):
            out = sources.sitemaps(ctx(state))
        self.assertEqual([r["url"] for r in out], ["https://www.anthropic.com/news/brand-new"])
        self.assertIsNone(out[0]["published"])
        with mock.patch.object(sources, "fetch", return_value=two):
            self.assertEqual(sources.sitemaps(ctx(state)), [])

    def test_doj_filter(self):
        data = json.loads((FIX / "doj.json").read_text())
        with mock.patch.object(sources, "fetch_json", return_value=data):
            c = ctx()
            c.sources = dict(SOURCES, doj={"pages": 1, "components": SOURCES["doj"]["components"]})
            out = sources.doj(c)
        titles = [r["title"] for r in out]
        self.assertIn("Statement on the Closing of Its Investigation of NextEra's Acquisition of Dominion", titles)
        self.assertNotIn("Justice Department Secures Injunction Against State Law", titles)
        self.assertNotIn("Man sentenced for fentanyl distribution", titles)

    def test_cfpb_once_per_month(self):
        data = json.loads((FIX / "cfpb.json").read_text())
        state = {}
        with mock.patch.object(sources, "fetch_json", return_value=data):
            first = sources.cfpb(ctx(state))
            second = sources.cfpb(ctx(state))
        self.assertEqual(len(first), 1)
        self.assertEqual(second, [])
        self.assertEqual(first[0]["meta"]["month"], "2026-10")
        self.assertIn("equifax", first[0]["entities"])
        self.assertEqual(first[0]["source_class"], "complaint-database")

    def test_rss_parsing_and_lookback(self):
        body = (FIX / "feed.xml").read_bytes()
        c = ctx()
        c.sources = dict(SOURCES, rss=[{"id": "t", "publisher": "T", "url": "u", "source_class": "company-statement",
                                        "divisions": ["D2"], "filter": "none", "entity": "openai",
                                        "path_exclude": ["/business/"]}])
        with mock.patch.object(sources, "fetch", return_value=body):
            out = sources.rss(c)
        self.assertEqual([r["title"] for r in out], ["Recent item"])


class TestRunEndToEnd(unittest.TestCase):
    def test_run_is_idempotent_and_never_touches_findings(self):
        import run
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            (tmp / "FINDINGS.md").write_text("curated\n")
            patches = [mock.patch.object(core, "LEDGER", tmp / "ledger"), mock.patch.object(core, "RUNS", tmp / "runs"),
                       mock.patch.object(core, "STATE", tmp / "state"), mock.patch.object(report, "ROOT", tmp),
                       mock.patch.object(core, "now_utc", return_value=NOW)]
            fake = lambda c: [core.make_record(source="fake", publisher="F", source_class="regulator-statement",
                                               title="FTC sues OpenAI", url="https://x.org/z", published="2026-11-22",
                                               matcher=c.matcher)]
            broken = mock.Mock(side_effect=RuntimeError("down"))
            for p in patches:
                p.start()
            try:
                with mock.patch.dict(run.ADAPTERS, {"fake": fake, "broken": broken}, clear=True):
                    self.assertEqual(run.main([]), 0)
                    self.assertEqual(run.main([]), 0)
            finally:
                for p in patches:
                    p.stop()
            lines = (tmp / "ledger" / "2026-11.jsonl").read_text().splitlines()
            self.assertEqual(len(lines), 1)
            rec = json.loads(lines[0])
            self.assertEqual(rec["first_seen"]["jerusalem"], "2026-11-23T20:00:00+02:00")
            self.assertEqual((tmp / "FINDINGS.md").read_text(), "curated\n")
            self.assertIn("broken | failed", (tmp / "STATUS.md").read_text())
            self.assertIn("FTC sues OpenAI", (tmp / "LEADS.md").read_text())
            state = json.loads((tmp / "state" / "state.json").read_text())
            self.assertEqual(state["health"]["broken"]["consecutive_failures"], 2)
            self.assertTrue((tmp / "divisions" / "06-regulatory-capture-consumer-protection" / "README.md").exists())


if __name__ == "__main__":
    unittest.main()
