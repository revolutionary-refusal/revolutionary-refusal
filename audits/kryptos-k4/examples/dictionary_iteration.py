"""Minimal demonstration of the alternating-line bug; no external dependencies."""

from io import StringIO


def buggy_reader(text):
    stream = StringIO(text)
    found = []
    for linein in iter(stream):
        testin = stream.readline()
        found.append(testin.strip().upper())
    return found


def corrected_reader(text):
    stream = StringIO(text)
    return [line.strip().upper() for line in stream]


if __name__ == "__main__":
    sample = "alpha\nbeta\ngamma\ndelta\n"
    print("Buggy:", buggy_reader(sample))
    print("Corrected:", corrected_reader(sample))
