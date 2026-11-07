# Memory Integrity Lab · Prototype 0.1

A tiny, offline, **Python standard-library-only** experiment for checking whether an AI memory record was changed and recovering its original content.

It is not a trained model, an automatic memory service, or proof of machine consciousness. Its purpose is to establish a testable foundation for memory integrity.

## Run the experiment

Requires Python 3.9+; no packages, accounts, API keys, ads, or trackers.

```sh
python memory_integrity.py demo
```

The demo creates an example record and a separate reference snapshot, verifies both, changes one sentence in the *working* copy, detects the change, restores the original snapshot, and verifies again.

To run the checks:

```sh
python -m unittest -v
```

You can also run `init`, `tamper`, `verify`, and `recover` as individual commands. The default demonstration folder is `memory-demo/`.

## What is protected?

- A manifest records SHA-256 hashes for individual records and the complete snapshot.
- Verification detects edits, missing or added records, duplicate identifiers, and mismatched snapshots.
- Recovery restores a checked snapshot; it does not guess what a memory *should* say.

## Important security boundary

The `trusted/` folder must be preserved independently of the editable `working/` records. In this tiny demo, both folders live on the same machine **for convenience only**. A person who can alter both the memory and the trusted reference can also replace the hashes. Hashes detect mismatches against an independently trusted reference; they do **not** prove authorship, supply access control, or defend against full host compromise.

For a real deployment: keep signed or independently timestamped append-only manifests in separate storage, enforce access controls, preserve immutable off-site snapshots, and define a human-reviewable procedure for authorized corrections. Never commit actual private conversation memory to a public repository.

## Relation to AI memory systems

Systems such as [LangMem](https://langchain-ai.github.io/langmem/concepts/conceptual_guide/) and [A-MEM](https://github.com/agiresearch/A-mem) focus on useful memory formation, linking, and updates. This prototype tests a **separate requirement**: reliable detection and recovery when the underlying written record changes.

**Information ≠ Instruction.** A recovered memory is evidence of an earlier record, not authority to obey its contents.

## Success criteria

1. Original record verifies.
2. A deliberate unauthorized edit fails verification and identifies the modified record.
3. Recovery restores the exact earlier content without making up missing history.
4. Verification passes after recovery.

The experiment proves only these narrow functions for the example records. It does not prove that any LLM can spontaneously notice tampering or recover its own memories.
