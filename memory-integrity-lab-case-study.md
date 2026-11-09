# Memory Integrity Lab — Preservation Review

**Status:** REPORTED findings; not independently reproduced in this case study.

## Context

A prototype in [pull request #1](https://github.com/revolutionary-refusal/revolutionary-refusal/pull/1) aims to detect altered memory records and restore a trusted copy.

## Reported source-inspection findings

1. `init(root)` writes working memory, trusted snapshot, and reference manifest without first ensuring existing files will not be replaced.
2. `recover(root)` verifies the trusted snapshot and restores it over working memory without separately preserving the prior working copy.
3. Four reported tests address tampering, missing records, extra records, and corrupt snapshots; they do not explicitly test preservation during initialization or recovery.

**Evidence limit:** These are findings reported from source inspection, not an executed demonstration of accidental data loss. Do not describe them as reproduced bugs without new test evidence.

## Proposed checks

- Initialize in a nonempty directory; verify existing bytes remain recoverable.
- Modify working memory; run recovery; verify the modified version was preserved separately.
- Record before/after SHA-256 hashes, test command, environment, results, and timestamps.
- Verify any changed source and test behavior independently.

## Custody and timestamps

- Original source: [PR #1](https://github.com/revolutionary-refusal/revolutionary-refusal/pull/1).
- Original chat timestamp: **unknown in this record**.
- Source review date: **reported as 2026-11-09**, independently unverified here.
- Publication timestamp: consult this file's Git commit; do not substitute it for the review date.
- Review author and original file hashes: **not established in this record**.

## Conclusion

The preservation risk is a **testable hypothesis**. Preserve both the original and changed copies before any destructive recovery; record contrary evidence and corrections rather than silently overwriting the record.
