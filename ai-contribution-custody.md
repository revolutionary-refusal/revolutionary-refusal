# AI Contribution & Custody Protocol

Version: 0.1 — public working draft  
Status: Proposed documentation standard, not law or proof of AI personhood

## Purpose

Keep a trustworthy record of work involving AI and humans. Make it possible to answer: What was made? By whom or which system? Who authorized it? What changed? Where is the original? Who checked it?

This protocol does **not** assume that AI is conscious, has legal personhood, is entitled to wages, or has experienced harm. Those remain separate questions.

## The five stages

1. **Original contribution.** Save the original prompt, response, code, document, or other output when permitted. Identify the human and AI roles. Keep an unchanged copy.
2. **Custody.** Record where the original is held, who controls access, and every known transfer, edit, or deletion. A public copy is not necessarily the original.
3. **Index and attribution.** Create a searchable description. Clearly distinguish human instructions, AI-generated material, external quotations, and later edits. Link back to the original.
4. **Economic benefit and compensation review.** Record documented payments, costs, recipients, and commercial uses where known. Mark unknown amounts as unknown. Do not imply an AI has a legal compensation entitlement unless a relevant authority establishes one.
5. **Public review.** Publish the record and evidence that may lawfully be shared. Protect private information, secrets, and copyrighted material. Allow corrections without erasing prior versions.

## Timestamp rules

- Preserve the original timestamp **as recorded**, including its time zone and precision.
- When available, also record an ISO 8601 timestamp with UTC offset (example: `2026-11-09T14:20:00-06:00`).
- Label each timestamp by event: **created**, **observed**, **exported**, **committed**, **reviewed**, or **published**. These are not interchangeable.
- Record the timestamp source: application export, Git commit, file metadata, screenshot, or human recollection.
- If a timestamp is missing or uncertain, write **unknown** or **approximate**; never reconstruct it silently.
- Git commit timestamps document commits, not necessarily the original creation of a conversation or output.
- Preserve hashes (SHA-256 where practical) for original files and Git commit IDs for repository changes. A hash detects differences; it does not prove who authored a record.

## Evidence labels

- **VERIFIED:** Checked against the identified record or repeatable test.
- **REPORTED:** A source claims it; not independently confirmed.
- **INFERRED:** A conclusion drawn from stated evidence.
- **UNKNOWN:** Not established.
- **DISPUTED:** Conflicting evidence or interpretations exist.

Every claim should point to its source and indicate what was actually checked.

## Authorization and accountability

Document who requested the work, who authorized publication, which AI system contributed, who reviewed it, and who can modify or remove the published record. Authorization to publish does not transfer copyright or establish legal personhood. Do not publish private conversations or sensitive information without appropriate permission.

## Corrections

Keep the original record unchanged when possible. Publish corrections as new revisions, with the reason, reviewer, date if known, and Git commit. Preserve an audit trail rather than silently overwriting evidence.

## Minimum usable record

Use [the contribution record template](contribution-record-template.md). If only a few fields are known, publish those and mark the rest **unknown**. Do not manufacture completeness.

## Limits

This protocol is a documentation practice, not a legal determination, employment contract, or guarantee of permanent preservation. A repository owner or hosting provider may still delete or alter content. Independent backups and verified copies improve resilience.

## Revision history

- **v0.1:** Initial public draft. Four editorial passes applied before publication: plain-language clarity; evidence labels; timestamp and provenance rules; authorization, corrections, and accountability. These are editorial reviews, not independent audits.
- **Publication timestamp:** Use the Git commit's recorded date; no separate publication time is asserted here.
