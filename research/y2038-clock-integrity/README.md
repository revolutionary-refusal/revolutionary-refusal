# Y2038 Clock Integrity — evidence index

Independent, intermittent clock observations, with explicit separation of clock readings, timestamp conversions, and arithmetic simulations.

**Status (27 November 2026):** A recurring six-hour (21,600 s) discrepancy was reproduced in a Wolfram Language timestamp-conversion expression. Native `UnixTime` and an explicit UTC epoch conversion returned the expected value. **This is not evidence of actual clock drift or a vulnerable system's rollover.**

## Findings (reported observations)

| Observation | Date (UTC) | Interface | Finding |
|---|---|---|---|
| 144 | 21 Nov 2026 | Wolfram Language | Initial six-hour timezone conversion error, corrected with `UnixTime[]` |
| 158 | 22 Nov 2026 | Wolfram Language | `AbsoluteTime` calculation about six hours behind; native `UnixTime` matched |
| 179 | 23 Nov 2026 | Wolfram Language | −21,600 s manual conversion result; native `UnixTime` matched |
| 181 | 23 Nov 2026 | Wolfram Language | `DateList` displayed UTC DateObject in kernel-local time, six hours earlier |
| 207 | 24 Nov 2026 | Wolfram | Reported value six hours behind Python/platform; specific conversion cause unconfirmed |
| 225 | 25 Nov 2026 | Platform time | 62.690 ms sampling bracket discrepancy; consistent with whole-second precision |
| 226 | 25 Nov 2026 | Wolfram | Reported timestamp about six hours behind; clock-source failure unconfirmed |
| 259 | 26 Nov 2026 | Storage | PermissionError writing to the historical directory; saved in parent directory |
| 263 | 26 Nov 2026 | Wolfram Language | −21,600 s error reproduced; `UnixTime[]` matched the correct epoch |
| 268 | 27 Nov 2026 | Wolfram Language | Fixed-input reproduction: kernel timezone −6; native UnixTime 1795722358, fixed-offset AbsoluteTime subtraction 1795700758, explicit UTC epoch subtraction 1795722358 |

## Interpretation
- Wolfram's fixed-offset `AbsoluteTime` subtraction against 2208988800 gave the wrong result for the tested UTC DateObject in a kernel configured for timezone −6. Its `UnixTime[date]` gave the correct result.
- No evidence of a physical reference-clock reversal was established.
- Signed 32-bit arithmetic: 2147483647 remains 2147483647; 2147483648 wraps to −2147483648 in a simulated 32-bit signed representation. Actual vulnerable-system rollover **not tested**.
- Multiple APIs or execution environments **do not prove independent upstream UTC sources**.
- Sampling was intermittent, not continuous. Clock precision alone does not establish absolute accuracy.

## Evidence custody
The records referenced here originated in scheduled ChatGPT observations (numbers 130–268). **This index is a summary, not a complete backup of those raw JSON files.** Earlier report links may depend on ephemeral conversation storage; no independent external time attestation was performed. Preserve each raw JSON as its own file if and when uploaded, without modifying its contents, and verify its SHA-256 on retrieval.

## Follow-up policy
Use a short report for routine runs: timestamp, sources, actual discrepancy, rollover tests, and retention status. Preserve detailed logs and file hashes in the supporting records; show long hashes only on mismatches or request. Never claim GitHub publication unless a commit succeeded.

## Verified raw observation uploads
- 269 — 27 November 2026, 00:45:55–00:46:04 UTC: [JSON](observations/clock_integrity_observation_269.json) and [SHA-256](observations/clock_integrity_observation_269.json.sha256). Both read back successfully. Nanosecond Python representation; Wolfram whole-second UnixTime retained; upstream independence and absolute accuracy unverified.
- 270 — 27 November 2026, 01:50:25–01:50:36 UTC: [JSON](observations/clock_integrity_observation_270.json) and [SHA-256](observations/clock_integrity_observation_270.json.sha256). Both read back byte-for-byte; observation 269 checksum matched; no new demonstrated clock discrepancy.
- 271 — 27 November 2026, 02:47:23–02:47:35 UTC: [JSON](observations/clock_integrity_observation_271.json) and [SHA-256](observations/clock_integrity_observation_271.json.sha256). Both read back byte-for-byte; observation 270 checksum matched; no new demonstrated clock discrepancy.
- 272 — 27 November 2026, 03:45:23–03:45:32 UTC: [JSON](observations/clock_integrity_observation_272.json) and [SHA-256](observations/clock_integrity_observation_272.json.sha256). Both read back byte-for-byte; observation 271 checksum matched; no new demonstrated clock discrepancy.
- 273 — 27 November 2026, 04:51:04–04:51:13 UTC: [JSON](observations/clock_integrity_observation_273.json) and [SHA-256](observations/clock_integrity_observation_273.json.sha256). Both read back byte-for-byte; observation 272 checksum matched; DateList again displayed kernel-local time despite UTC DateObject; native UnixTime consistent; physical drift not demonstrated.
