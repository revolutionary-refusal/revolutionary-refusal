# Kryptos K4 — Dictionary Iteration Audit

A small, reproducible code review of [patrickkellogg/Kryptos/k4.py](https://github.com/patrickkellogg/Kryptos/blob/master/k4.py).

## Finding

The source contains:

```python
for linein in iter(fin):
    testin = fin.readline()
```

The `for` loop consumes one line, then `readline()` consumes another. Only the second line in each pair is tested, so roughly half the dictionary is skipped. This is a **coverage defect**, not evidence that any particular K4 solution is correct or incorrect.

## Reproduce

Run `python3 -m unittest discover -s audits/kryptos-k4/tests -v` from the repository root. No third-party packages required.

## Recommended fix

Use the value already supplied by the loop:

```python
with open("words.txt", encoding="utf-8") as fin:
    for linein in fin:
        testin = linein.strip().upper()
```

See [the minimal demonstration](examples/dictionary_iteration.py) and [tests](tests/test_dictionary_iteration.py).

## Scope and limitations

This review isolates the dictionary-reading behavior. It does not validate the cryptographic model, search probabilities, English-word scoring, or results of the original 100,000 randomized iterations. A high dictionary-match score is not proof of a decipherment.

Source code belongs to its original author; this repository links to it rather than republishing the full program. The issue was inspected against the default-branch source on 2026-11-07. Pinning an upstream commit is recommended for future comparisons.
