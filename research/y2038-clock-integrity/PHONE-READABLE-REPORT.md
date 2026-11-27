# Clock investigation — phone-readable report

**Updated: 27 November 2026**

## What happened?
We repeatedly observed a **six-hour difference** when converting timestamps in Wolfram. Follow-up tests reproduced it with a particular conversion expression. Wolfram's built-in `UnixTime` gave the expected result. **No evidence establishes that an actual clock moved backward.**

## Important findings

| Date (UTC) | Observation | What happened |
|---|---:|---|
| 21 Nov 2026 | 144 | Wolfram timestamp calculation was six hours behind; corrected |
| 22 Nov 2026 | 158 | Similar six-hour conversion difference |
| 23 Nov 2026 | 179, 181 | Faulty conversion and timezone display confirmed |
| 24 Nov 2026 | 207 | Wolfram reported a six-hour offset; underlying source fault unproven |
| 25 Nov 2026 | 225 | Platform's 63 ms apparent discrepancy was within one-second reporting precision |
| 25 Nov 2026 | 226 | Six-hour Wolfram discrepancy appeared again |
| 26 Nov 2026 | 259 | File storage permission error; record saved elsewhere |
| 26 Nov 2026 | 263 | Six-hour Wolfram conversion error reproduced on retry |
| 27 Nov 2026 | 268 | Fixed-input tests reproduced the exact 21,600-second error; native `UnixTime` worked |

## What does it mean?
**Finding:** In the tested Wolfram environment, one timestamp-conversion method mixed timezone assumptions and produced an incorrect Unix timestamp. This is an error in the measurement procedure, **not evidence that a physical clock failed**.

**Y2038:** Signed 32-bit arithmetic produced the expected rollover value. No vulnerable hardware or operating system was actually rolled forward to 2038.

## What is saved?
The source set includes **139 original JSON observation files (130–268)**. Those contain exact readings, sources, tests, and hashes. They were packaged into a ZIP in ChatGPT, but **the original 139 JSONs have not been uploaded individually to GitHub**. This GitHub page is a human-readable explanation, not a substitute for the original measurement files.

**Accuracy limits:** The services were sampled at different instants. Their upstream UTC independence and absolute accuracy were not established. Monitoring was not continuous. Earlier local file availability is not a guarantee of long-term storage.

## How to use this page
Read this page on a phone; no downloads or software required. If a later investigation changes the conclusion, add a new dated note rather than quietly replacing an old finding.
