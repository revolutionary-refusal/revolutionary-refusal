import datetime as dt
import hashlib
import json
import pathlib
import urllib.request
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).parent
SOURCES = {
    "ftc": "https://www.ftc.gov/feeds/press-release.xml",
    "doj": "https://www.justice.gov/atr/press-room",
    "ec": "https://competition-policy.ec.europa.eu/index_en",
    "cfpb": "https://www.consumerfinance.gov/about-us/newsroom/",
    "openai": "https://openai.com/news/rss.xml",
    "nvidia": "https://nvidianews.nvidia.com/",
    "federal_reserve": "https://www.federalreserve.gov/feeds/press_all.xml",
    "sec": "https://www.sec.gov/newsroom/press-releases",
    "gao": "https://www.gao.gov/reports-testimonies",
}
now = dt.datetime.now(dt.timezone.utc)
local = now.astimezone(ZoneInfo("Asia/Jerusalem"))
if local.hour not in (8, 10, 14, 17, 20, 23):
    print("Outside scheduled Israel-time windows")
    raise SystemExit(0)
ledger = ROOT / "evidence"
ledger.mkdir(exist_ok=True)
state_path = ROOT / "state.json"
state = json.loads(state_path.read_text()) if state_path.exists() else {}
records = []
for name, url in SOURCES.items():
    row = {"source": name, "url": url, "checked_utc": now.isoformat()}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PublicAccountabilityResearch/1.0"})
        with urllib.request.urlopen(req, timeout=25) as response:
            data = response.read(4000001)
            if len(data) > 4000000:
                raise ValueError("response exceeds size limit")
            row["http_status"] = response.status
        digest = hashlib.sha256(data).hexdigest()
        row["sha256"] = digest
        row["changed"] = state.get(name) != digest
        if row["changed"]:
            try:
                tree = ET.fromstring(data)
                row["feed_titles"] = [e.text for e in tree.iter() if e.tag.split("}")[-1] == "title" and e.text][:40]
            except ET.ParseError:
                pass
        state[name] = digest
    except Exception as exc:
        row["error"] = str(exc)
    records.append(row)
(ledger / (now.strftime("%Y-%m-%dT%H%M%SZ") + ".json")).write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n")
state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
