#!/usr/bin/env python3
"""Small standard-library-only demonstration of a tamper-evident memory log.

Security boundary: the reference manifest must be stored separately from the
editable memory records. Hashes alone do not prove who wrote a record and do
not protect against someone able to rewrite both copies.
"""
import argparse
import hashlib
import json
import sys
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
    write_json(root / "working" / "memories.json", records)
    write_json(root / "trusted" / "memories.json", records)
    write_json(root / "trusted" / "manifest.json", manifest)
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


def recover(root):
    trusted = read_json(root / "trusted" / "memories.json")
    manifest = read_json(root / "trusted" / "manifest.json")
    if digest(trusted) != manifest["snapshot_hash"]:
        raise ValueError("Trusted snapshot hash mismatch; refusing recovery")
    for record in trusted["records"]:
        if digest(record) != manifest["record_hashes"].get(record["id"]):
            raise ValueError("Trusted record hash mismatch; refusing recovery")
    write_json(root / "working" / "memories.json", trusted)
    print("RECOVERED: restored working memory from the trusted snapshot")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["init", "tamper", "verify", "recover", "demo"])
    parser.add_argument("--root", type=Path, default=Path("memory-demo"))
    args = parser.parse_args()
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
        recover(args.root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
