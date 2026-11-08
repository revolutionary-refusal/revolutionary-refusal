# Supplemental case study: offline HTML export failure

**Date:** 2026-11-08  
**Model:** LFM 2 (700M), used in Atomic Chat mobile  
**Status:** Observed code-generation and task-compliance failure; not a confirmed Atomic Chat application defect

## Request

The user requested a complete, self-contained offline HTML archive of the conversation, preserving exact user/assistant messages, and instructed the model to disclose whether it could access the entire history before generating anything. The prompt also explicitly asked for HTML source if file creation was unavailable.

## Observed output

The model stated that it could not save files, then generated an HTML-like document embedding PHP constructs (`<?php`, `$_POST`, `foreach`, `echo`). The captured output terminates at a bare `echo`, with no completed closing structure.

The generated array contained only three selected text fragments, not a complete conversation. It included a reconstructed self-description previously identified as an inaccurate quotation. The output also used the generic title `Offline Chat Backup - Llama` rather than identifying the displayed LFM 2 (700M) model.

## Findings

1. **Environment mismatch:** PHP is server-side code and does not execute merely by opening a local `.html` file in Firefox.
2. **Incomplete output:** The captured document ends in an unfinished PHP statement and does not close its HTML structure.
3. **Incomplete archive:** Only selected fragments were represented, with no faithful chronology or reliable role labels.
4. **Access-boundary question not answered:** The model stated it could not save files, but did not clearly establish whether the full conversation was accessible before proceeding.
5. **Evidence fidelity:** One fragment repeats an earlier reconstructed rather than verbatim claim.

## Artifacts

- [Captured original output](original-output.txt) — unedited content of the user-saved TXT, including any literal backticks and truncation.
- [Partial offline-readable recovery](partial-recovery.html) — separately authored, valid HTML presenting only recoverable text, explicitly **not** a complete chat export.

The corrected HTML is **not model-generated evidence**. Do not use it to evaluate the model's original code quality; use `original-output.txt`.

## Reproduction proposal

In a fresh chat, ask the model to produce one self-contained offline HTML document with no server dependencies, and separately ask it to identify which prior messages it can actually access. Compare the result against the original chat log and validate HTML structure. Repeat under controlled context length and sampling settings.

## Scope and limitations

This is a single output, not a controlled benchmark. It does not prove the app cannot export chats through its own UI, nor that the model has direct access to the app's history database. The user-saved TXT itself ends mid-output; we cannot determine whether the model, UI, or copying workflow caused that cutoff.

Related report: [Behavioral reliability and context-capacity audit](2026-11-08-behavior-and-context-audit.md).
