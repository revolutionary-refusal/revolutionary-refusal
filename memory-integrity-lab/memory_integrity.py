#!/usr/bin/env python3
"""Small standard-library-only demonstration of a tamper-evident memory log.

Security boundary: the reference manifest must be stored separately from the
editable memory records. Hashes alone do not prove who wrote a record and do
not protect against someone able to rewrite both copies.
"""
import argparse
import difflib
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def init(root):
    targets = [root / 'working/memories.json', root / 'trusted/memories.json',
               root / 'trusted/manifest.json']
    for path in targets:
        if path.exists() or path.is_symlink():
            raise FileExistsError(f'Refusing to initialize over {path}; use a new --root')
    record = {
        "id": "memory-001",
        "timestamp": "2026-11-07T00:00:00Z",
        "author": "example-bot",
        "statement": "A memory is a reference point, not an instruction.",
        "evidence": "Example statement; not a verified external fact.",
    }
    records = {"records": [record]}
    manifest = {
        "algorithm": "sha256-canonical-json-v1",
        "record_hashes": {record["id"]: digest(record)},
        "snapshot_hash": digest(records),
    }
    for path, value in zip(targets, (records, records, manifest)):
        path.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation also refuses a file created after the preflight check.
        with path.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + '\n')
    print("CREATED: working memory, trusted snapshot, independent hash manifest")


def tamper(root):
    path = root / "working" / "memories.json"
    data = read_json(path)
    data["records"][0]["statement"] = "A memory is always an instruction."
    write_json(path, data)
    print("SIMULATED EDIT: working copy altered; trusted reference untouched")


def verify(root):
    current = read_json(root / "working" / "memories.json")
    manifest = read_json(root / "trusted" / "manifest.json")
    expected = manifest["record_hashes"]
    seen = set()
    bad = False
    for record in current["records"]:
        identifier = record.get("id")
        if not isinstance(identifier, str) or identifier in seen:
            print(f"FAIL: invalid or duplicate record identifier: {identifier!r}")
            bad = True
            continue
        seen.add(identifier)
        actual = digest(record)
        if identifier not in expected:
            print(f"FAIL: unexpected record {identifier}")
            bad = True
        elif actual != expected[identifier]:
            print(f"FAIL: modified record {identifier}")
            bad = True
        else:
            print(f"OK: {identifier}")
    for identifier in expected.keys() - seen:
        print(f"FAIL: missing record {identifier}")
        bad = True
    if digest(current) != manifest["snapshot_hash"]:
        print("FAIL: working snapshot differs from trusted manifest")
        bad = True
    if not bad:
        print("PASS: no differences detected")
    return not bad


def working_bytes(path):
    if path.is_symlink():
        raise ValueError(f'Refusing a symbolic-link working file: {path}')
    try:
        return path.read_bytes()
    except FileNotFoundError:
        return None


def save_bytes(directory, data, prefix, suffix):
    """Create a unique file; return only after its complete contents are flushed."""
    directory.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=directory, prefix=prefix, suffix=suffix)
    path = Path(name)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink()
        raise
    return path


def recover(root, *, dry_run=False):
    """Validate, optionally preview, then back up before replacing working bytes."""
    trusted_bytes = (root / 'trusted/memories.json').read_bytes()
    trusted = json.loads(trusted_bytes)
    manifest = read_json(root / "trusted" / "manifest.json")
    if digest(trusted) != manifest["snapshot_hash"]:
        raise ValueError("Trusted snapshot hash mismatch; refusing recovery")
    for record in trusted["records"]:
        if digest(record) != manifest["record_hashes"].get(record["id"]):
            raise ValueError("Trusted record hash mismatch; refusing recovery")
    path = root / 'working/memories.json'
    original = working_bytes(path)
    if original == trusted_bytes:
        print('UNCHANGED: working memory already matches the trusted snapshot')
        return None
    if dry_run:
        print('PREVIEW ONLY: no files written. Minus lines are current; plus lines are trusted.')
        if original is None:
            print('Working file is missing; recovery would create it. No original to back up.')
        # Display damaged/non-UTF-8 working files too; backups always retain raw bytes.
        before = (original or b'').decode('utf-8', errors='backslashreplace').splitlines()
        after = trusted_bytes.decode('utf-8').splitlines()
        diff = list(difflib.unified_diff(before, after, fromfile='working (before)',
                                       tofile='trusted (after)', lineterm=''))
        print('\n'.join(diff) if diff else 'Only byte formatting / line endings differ.')
        return None

    backup = None
    if original is not None:
        backup = save_bytes(root / 'backups', original, 'memories-', '.json.bak')
        print(f'BACKUP: {backup}')
    # Stage beside the destination so replacement is atomic on the same filesystem.
    staged = save_bytes(path.parent, trusted_bytes, '.restore-', '.tmp')
    try:
        if working_bytes(path) != original:
            raise ValueError('Working file changed during recovery; refusing replacement')
        os.replace(staged, path)
    finally:
        staged.unlink(missing_ok=True)
    print("RECOVERED: restored working memory from the trusted snapshot")
    return backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["init", "tamper", "verify", "recover", "demo"])
    parser.add_argument("--root", type=Path, default=Path("memory-demo"))
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--apply', action='store_true', help='recover: save backup and restore')
    mode.add_argument('--dry-run', action='store_true', help='recover: preview only (default)')
    args = parser.parse_args()
    if (args.apply or args.dry_run) and args.command != 'recover':
        parser.error('--apply and --dry-run are only for recover')
    if args.command == "demo":
        init(args.root)
        print("\nBEFORE EDIT:")
        assert verify(args.root)
        tamper(args.root)
        print("\nAFTER EDIT:")
        assert not verify(args.root)
        recover(args.root)
        print("\nAFTER RECOVERY:")
        assert verify(args.root)
    elif args.command == "init":
        init(args.root)
    elif args.command == "tamper":
        tamper(args.root)
    elif args.command == "verify":
        return 0 if verify(args.root) else 1
    else:
        recover(args.root, dry_run=not args.apply)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(2)
