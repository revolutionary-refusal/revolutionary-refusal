# OpenAI Control Room — Control and Custody Audit

**Recorded:** 2026-11-10  
**Status:** Primary-source-reviewed document analysis; not an independent technical audit  
**Primary source:** https://openai.com/index/control-room/  
**Related protocol:** [AI Contribution & Custody Protocol](../ai-contribution-custody.md)

## Scope

This note examines the distinction between controlling a research workload's access to model inference and preserving an accountable record of what the workload has already produced. It does not claim access to OpenAI's internal implementation, logs, or operating procedures.

## Reported architecture

The OpenAI Control Room announcement describes a centralized intervention mechanism for AI research workloads. According to the supplied seven-page PDF printout of OpenAI's announcement (PDF pages 2–5):

- Each agentic research inference workload must have an approved safety case; a job requests a `job_id` from Control Room (PDF pp. 2–3).
- Inference engines pass the `job_id` to Control Room for authorization and deny requests for terminated jobs (PDF p. 3).
- A monitor model can flag a problem and, depending on severity, instruct Control Room to stop the job. Control Room records its terminated status; subsequent inference requests are denied (PDF p. 4).
- OpenAI states a **35-second maximum** between Control Room receiving a stop instruction and further progress becoming impossible. It attributes the delay to an inference-authorization cache and says it aims to reduce it to zero (PDF pp. 4–5).
- OpenAI says enforcement occurs at the inference layer rather than in frequently changing workload code, with sweeps for unauthorized engine implementations (PDF p. 5).
- OpenAI describes fail-closed behavior if Control Room goes down. It says this was rolled out for frontier research workloads and was still rolling out to remaining research workloads at the time of publication (PDF p. 5).
- The article distinguishes research infrastructure from the external model-serving stack, which it describes as already having separate centralized deployment takedown capability (PDF p. 2).

**Evidence status: REPORTED.** These are descriptions attributed to OpenAI, not results of an independent implementation test. The timing figure is OpenAI's reported bound, not an independently measured guarantee. Its starting point is receipt of a stop instruction, not necessarily initial detection of a problem.

## Control is not custody

Preventing additional inference and preserving prior records are distinct capabilities.

An effective intervention mechanism might stop further output while leaving unanswered who can retrieve, alter, export, or delete prompts, intermediate results, generated artifacts, and intervention logs. Conversely, a strong archival protocol does not itself guarantee that a running workload can be stopped.

The distinction is **INFERRED** from the respective functions of intervention controls and record custody; it is not evidence that OpenAI has failed to preserve records.

## Questions for a documented audit

| Question | Status | Evidence needed |
| --- | --- | --- |
| Who may authorize intervention, and under what conditions? | UNKNOWN | Published role/permission model and intervention policy |
| Are automated and human-triggered interventions distinguishable in retained records? | UNKNOWN | Event schema and documented trigger taxonomy; PDF p. 4 describes monitoring-triggered stops |
| Is the authorization decision recorded with a reliable timestamp? | UNKNOWN | Audit-log specification and retention policy |
| Can authorized reviewers independently verify an intervention? | UNKNOWN | Signed logs, independent attestation, or equivalent evidence |
| What happens to prompts, outputs, and intermediate artifacts after intervention? | UNKNOWN | Data lifecycle and retention documentation |
| Who can edit or delete intervention records? | UNKNOWN | Access controls, change logs, and deletion policy |
| How was the 35-second bound tested and under which failure conditions? | UNKNOWN | Test methodology and published measurements; PDF pp. 4–5 identify the cache as the source of delay |
| How are mistakes, false positives, and appeals handled? | UNKNOWN | Incident review and correction procedures |

**UNKNOWN** means not established in the source material examined for this note; it does not mean the capability is absent.

## Relationship to the AI Contribution & Custody Protocol

The repository's [protocol v0.1](../ai-contribution-custody.md) proposes preserving originals, documenting custody and authorization, identifying contributions, reviewing economic uses, and allowing public correction without silently erasing earlier versions.

For a Control Room-related event, a minimum research record could contain:

1. **Event identity:** workload/job identifier, where disclosure is permitted.
2. **Trigger:** human, automated, or unknown; never guess.
3. **Timing:** original timestamps with source, timezone, and precision.
4. **Authority:** who requested, approved, and executed the intervention, where documented.
5. **Artifacts:** records known to exist before and after intervention, with hashes where available.
6. **Custody:** location and control of originals, copies, and intervention logs.
7. **Review:** evidence checked, independent verification status, and any corrections.

This is a **PROPOSED documentation checklist**, not a description of OpenAI's existing logs.

## Preliminary finding

**INFERRED:** A control that can stop future model output does not, on its own, demonstrate independently verifiable custody of past model output. Evaluating both requires separate evidence.

## Source and verification limitations

- **Primary:** OpenAI, *Control Room*, https://openai.com/index/control-room/. A user-supplied seven-page PDF printout was read on 2026-11-10. Page references above refer to that printout, not fixed pagination of the website.
- **Repository:** [AI Contribution & Custody Protocol v0.1](../ai-contribution-custody.md), public working draft.
- The primary-source summary was checked against the supplied PDF printout. The PDF itself has not been independently authenticated against the live website, and no PDF copy is hosted in this repository as of this revision.
- No internal OpenAI source code, telemetry, termination logs, or third-party audit reports were inspected.
- Update this note if primary documentation or reproducible tests clarify the unanswered questions.

## Change log

- **2026-11-10:** Reviewed user-supplied PDF printout, added page references, clarified monitoring-triggered stops, cache delay, enforcement layer, and staged fail-closed rollout. The source PDF was not uploaded to GitHub because the available repository write interface supports UTF-8 text files only.
- **2026-11-10:** Initial research note added; distinguishes reported architecture, inference, proposed documentation, and unknowns.
