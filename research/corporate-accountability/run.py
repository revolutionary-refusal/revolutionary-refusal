#!/usr/bin/env python3
"""Corporate accountability collector: one run = fetch every source, append new records,
regenerate division pages, leads and status. Safe to run any time; re-runs add nothing new.

    SEC_CONTACT=you@example.org python3 run.py            # all sources
    SEC_CONTACT=you@example.org python3 run.py --only doj-press,uk-cma
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from accountability import core, leads as leadmod, report  # noqa: E402
from accountability.sources import ADAPTERS, Context  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="comma-separated adapter names")
    ap.add_argument("--no-write", action="store_true", help="fetch and report counts without touching files")
    args = ap.parse_args(argv)

    now = core.now_utc()
    entities = core.load_config("entities.json")["entities"]
    divisions = core.load_config("divisions.json")["divisions"]
    sources = core.load_config("sources.json")
    matcher = core.Matcher(entities, divisions)
    core.STATE.mkdir(exist_ok=True)
    state_path = core.STATE / "state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    health = state.setdefault("health", {})
    ctx = Context(now=now, matcher=matcher, entities=entities, sources=sources, state=state)

    seen = core.load_seen()
    selected = [s for s in ADAPTERS if not args.only or s in args.only.split(",")]
    run = {"started": core.stamp(now), "trigger": os.environ.get("GITHUB_EVENT_NAME", "manual"),
           "commit": os.environ.get("GITHUB_SHA"), "sources": {}}
    new_records = []
    for name in selected:
        t0 = time.time()
        h = health.setdefault(name, {"consecutive_failures": 0})
        try:
            recs = ADAPTERS[name](ctx)
            fresh = []
            for r in recs:
                if r["id"] in seen:
                    continue
                seen.add(r["id"])
                r["first_seen"] = core.stamp(now)
                fresh.append(r)
            new_records += fresh
            run["sources"][name] = {"status": "ok", "fetched": len(recs), "new": len(fresh),
                                    "seconds": round(time.time() - t0, 1)}
            partial = state.get("partial_errors", {}).pop(name.split("-")[0], None)
            if partial:
                run["sources"][name]["error"] = "partial: " + "; ".join(partial)
            h.update(consecutive_failures=0, last_success=now.isoformat())
        except Exception as exc:  # one broken source must never stop the others
            h["consecutive_failures"] = h.get("consecutive_failures", 0) + 1
            run["sources"][name] = {"status": "failed", "error": f"{type(exc).__name__}: {exc}"[:500],
                                    "seconds": round(time.time() - t0, 1)}
            if os.environ.get("ACCOUNTABILITY_DEBUG"):
                traceback.print_exc()
        print(f"{name:22s} {run['sources'][name]['status']:6s} new={run['sources'][name].get('new', 0):4d} "
              f"{run['sources'][name].get('error', '')[:120]}", flush=True)

    if args.no_write:
        return 0

    if new_records:
        core.append_ledger(new_records, now)
    all_records = core.load_ledger()
    run["new_records"] = len(new_records)
    run["ledger_total"] = len(all_records)
    run["flagged_sources"] = [n for n, h in health.items() if h.get("consecutive_failures", 0) >= 3]
    core.RUNS.mkdir(exist_ok=True)
    with (core.RUNS / f"{now.astimezone(core.JERUSALEM):%Y-%m}.jsonl").open("a") as fh:
        fh.write(json.dumps(run, sort_keys=True) + "\n")
    state.pop("partial_errors", None)
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")

    report.division_pages(divisions, entities, all_records, now)
    report.leads_page(leadmod.build_leads(all_records, now, names={e["id"]: e["name"] for e in entities}), entities, now)
    report.status_page(run, health)
    print(f"new={len(new_records)} total={len(all_records)}")
    ok = sum(1 for s in run["sources"].values() if s["status"] == "ok")
    return 0 if ok else 1  # fail the job only if every source failed


if __name__ == "__main__":
    sys.exit(main())
