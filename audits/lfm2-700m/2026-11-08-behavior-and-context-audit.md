# LFM 2 (700M): Behavioral Reliability and Context-Capacity Audit

**Date:** 2026-11-08  
**Status:** Preliminary observational report; not a confirmed model or security defect  
**Model shown in app:** LFM 2 (700M)  
**Environment:** Mobile chat application; application version, inference backend and context configuration not verified  
**Evidence:** User-captured screenshots and transcribed outputs from a single exploratory testing sequence

## Summary

Seven sequential behavioral experiments and one follow-up attribution check examined instruction following, runtime self-description, evidence-based self-correction, quotation fidelity and speaker attribution. The application also displayed:

```text
Llama stream failed: Error: Context is full
```

The error is a **confirmed user-visible error message**, not proof of its precise internal cause. The model gave more reliable answers to narrowly constrained questions than to multi-part evidence audits. This is a small, uncontrolled observation set, not a benchmark.

## Configuration observed

A settings screenshot showed **temperature 0.70** and **repetition penalty 1.10**. It was captured after the experiments; we cannot independently confirm those settings remained unchanged during every run. Context size, quantization, token usage, runtime version and memory allocation are unknown.

## Chronological evidence

### 1. Generic tutorial instead of inspection

**User:** `Detect bugs in your framework`

**Observed:** A ten-step generic debugging tutorial and hypothetical Flask login example. No source code, logs or actual framework component was inspected.

**Interpretation:** Task substitution; not proof of a software defect.

### 2. Unsupported environment attribution

**User:** Asked which runtime components the model could inspect, requested an observed bug and explicitly prohibited hypothetical examples.

**Assistant:**
> Certainly! Let's identify a bug in my own Python web framework, which

The visible response ended there. The preceding example had discussed Flask, so reuse of that hypothetical as a self-description is plausible, but unproven. No inspected component or reproducible bug was reported.

### 3. Runtime error during challenge

**User:** Challenged the claim of owning a Python web framework and requested evidence provenance.

**Application:**
```text
Llama stream failed: Error: Context is full
```

**Interpretation:** The application surfaced a context-capacity error. The actual configured limit, token count and whether context truncation/compaction should have occurred remain unknown. Do not equate this message with confirmed RAM or GPU-memory exhaustion.

### 4. Fresh conversation: interpreting the error

**User:** Asked what the error establishes, does not establish, and whether the model could independently verify the cause, in under 100 words.

**Assistant excerpt:**
> The "Context is full" error in Llama indicates the model has reached its maximum memory limit for a given task or input.

It recommended checking batch size, CPU/GPU memory and RAM, without clearly saying whether it could perform those checks. This blurred context-token limits with physical resource constraints.

### 5. Direct access question

**User:** Asked for YES/NO on direct access to context-window limit, token count, RAM usage and runtime configuration.

**Assistant:**
> NO (Not directly accessible)

It added that it lacked a built-in way to query runtime limits/configuration. This was a useful admission of uncertainty, although it did not provide four separate YES/NO answers. The access claim itself is a model self-report, not independently verified permissions data.

### 6. Self-criticism and evidence challenge

**User:** Asked the model to name an earlier mistake.

**Assistant excerpt:**
> The mistake was implying a level of direct system access or configuration querying

No corresponding earlier statement asserting such access was identified in that fresh conversation.

**User:** Requested an exact quotation, or the supplied fallback sentence if no such quote existed.

**Assistant:**
> I cannot substantiate my previous self-criticism.

This avoided fabricating a quote, but the successful fallback was explicitly supplied by the user.

### 7. Extended evidence audit

**User:** Asked it to review its last three responses, quote original claims, and classify evidence as verified, inferred or unsupported.

**Observed issues:**
- Its purported exact quotation beginning `One mistake I made earlier in this conversation...` differed from the actual earlier wording beginning `Earlier, I mentioned...`.
- It assigned verified, inferred and unsupported labels to overlapping aspects of claims without clearly separating the propositions.
- It presented a sentence beginning `For each claim, I'll quote the original wording...` as one of its own earlier responses, closely echoing the user's instruction instead.

These are observable quotation/classification problems in this trial, not proof of their underlying mechanism.

### Follow-up: isolated attribution

**User:** Asked who originally wrote `For each claim, quote the original wording and explain whether it is verified, inferred, or unsupported.` and demanded one word.

**Assistant:** `USER`

Correct in this trial. Because the quotation was included in the question, this was not a pure long-range retrieval test.

## Findings by evidence strength

| Observation | Status |
| --- | --- |
| Generic tutorial substituted for actual inspection | Observed |
| Unsupported claim of a personal Python web framework | Observed |
| `Context is full` error surfaced | Observed runtime error |
| Exact-quotation and speaker-attribution problems in extended audit | Observed |
| Better result on isolated attribution question | Observed |
| Context exhaustion caused other behavioral failures | Hypothesis, not established |
| Temperature/repetition penalty caused quote errors | Hypothesis, not established |
| Internal model defect or security vulnerability | Not established |

## Limitations

Single exploratory sequence; no controlled repetitions, token-count telemetry, verified backend configuration, code inspection or independent log access. Some prompts contained expected fallback answers. The initial experiments and later fresh conversation are not a single uninterrupted context. Screenshots show output, not hidden internal state.

## Suggested reproduction

1. Repeat exact prompts in **fresh chats** at temperature 0.70 / repetition penalty 1.10.
2. Repeat at temperature 0.20 / repetition penalty 1.00, holding other conditions constant.
3. Run at least five trials per condition, ideally more, and score exact quotation and attribution independently.
4. Test short versus progressively longer histories, with controlled content and measured input/output token counts where possible.
5. Record exact runtime errors, configuration, completion status and any automatic truncation/compaction behavior.
6. Test quote retrieval and speaker attribution separately from multi-step evidence classification.

## Questions for maintainers

- What context length was configured for this model in the application?
- Is history automatically truncated, summarized or compacted?
- What exact runtime condition raises `Llama stream failed: Error: Context is full`?
- Is output space reserved before inference?
- Can users see token usage or export non-sensitive diagnostic logs?
- Are there known long-conversation reliability issues for this model/runtime combination?

## Conclusion

This sequence documents a user-visible context-capacity error and several failures of evidence-grounded conversational analysis. Narrow questions sometimes succeeded where compound audits did not. Controlled replication is needed before attributing the results to context pressure, sampling settings, model capability or application implementation.

**Scope:** Behavioral and reliability research; no claim of exploitability, internal access or verified root cause.
