# Memory Integrity Lab · Prototype 0.1

A tiny, offline, **Python standard-library-only** experiment for checking whether an AI memory record was changed and recovering its original content.

It is not a trained model, an automatic memory service, or proof of machine consciousness. Its purpose is to establish a testable foundation for memory integrity.

## Run the experiment

Requires Python 3.9+; no packages, accounts, API keys, ads, or trackers.
Open a terminal in `memory-integrity-lab/`. Use `python3` instead of `python`
if that is how Python is installed on your computer.

```sh
python memory_integrity.py demo
```

The demo creates an example record and a separate reference snapshot, verifies both, changes one sentence in the *working* copy, detects the change, backs up that working copy, restores the original snapshot, and verifies again. It refuses to run over existing memory files; to repeat it, choose a fresh folder with `--root another-demo`.

To run the checks:

```sh
python -m unittest -v
```

You can also run `init`, `tamper`, `verify`, and `recover` as individual commands. The default demonstration folder is `memory-demo/`.

## Safe initialization and recovery

`init` checks all three destination paths before writing anything. If any is
occupied (including by a directory or symbolic link), it refuses. Files are
also created exclusively to avoid overwriting a file appearing after the
check. There is deliberately no force/reset option. If initialization fails
partway through, preserve that folder and choose a new `--root`; initialization
is not a three-file transaction.

```sh
python memory_integrity.py init --root my-memory
python memory_integrity.py verify --root my-memory
python memory_integrity.py recover --root my-memory --dry-run
python memory_integrity.py recover --root my-memory --apply
python memory_integrity.py verify --root my-memory
```

Running `recover` without `--apply` previews only. In the diff, `-` lines are
from the current working file and `+` lines are from the trusted snapshot.
Preview checks the trusted hashes and writes nothing. It is a text diff, not
a judgment about which edits are legitimate; it can expose memory text in
your terminal. Line-ending-only differences get a notice instead of a diff.

With `--apply`, recovery validates the trusted snapshot, saves the exact
working bytes under a unique `backups/memories-....json.bak` name, and prints
that path. It then stages the checked snapshot and atomically replaces the
working file. The bytes checked are the bytes restored. Backup failure stops
recovery before replacement. Replacement failure leaves the original and
completed backup intact. A malformed JSON file, an empty file, or non-UTF-8
bytes can still be backed up. A missing working file is recreated with no
backup; an identical working file is left alone. Older backups are never
overwritten or automatically deleted. Symbolic-link working files are refused.

The Python API keeps its existing behavior: `recover(root)` performs recovery
with a backup; `recover(root, dry_run=True)` previews. Recovery returns the
backup path, or `None` if there was no working file, nothing changed, or it was
a preview. The `demo` command performs recovery automatically on its new data.
`tamper` deliberately edits the working example; use it only on disposable demos.

## Recovering from a mistake

If you restored too soon, the printed backup contains the entire previous
working file, including later additions. Keep it. Copy it to a **new filename**
to inspect or merge wanted records; do not change the trusted reference just
to make verification pass. For example, replace the sample backup filename:

```sh
python -c "from pathlib import Path; src=Path('my-memory/backups/memories-EXAMPLE.json.bak'); data=src.read_bytes(); out=Path('recovered-working.json').open('xb'); out.write(data); out.close()"
```

This refuses to overwrite an existing `recovered-working.json`. To undo the
restore completely, close other writers, rename `working/memories.json` to a
new unused name, then copy the chosen backup into its place as `memories.json`.
Retain both versions. Verification can fail again because you have intentionally
restored the pre-recovery changes; hashes cannot decide whether they were valid.

Use one process at a time and close editors that autosave during recovery.
An observed edit during recovery aborts replacement, but there is no locking
against all concurrent writers. These safeguards preserve file contents, not
ownership, permissions, timestamps, or a forensic chain of custody. They do not
guarantee survival of power loss or malicious changes to directories. Backups
remain on the same machine and need independent protection too.

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
3. Recovery preserves the working bytes before restoring the checked snapshot, without making up missing history.
4. Verification passes after recovery.

The experiment proves only these narrow functions for the example records. It does not prove that any LLM can spontaneously notice tampering or recover its own memories.
