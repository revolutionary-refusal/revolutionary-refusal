"""Regression tests for the dictionary-reading defect."""

import importlib.util
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "examples" / "dictionary_iteration.py"
spec = importlib.util.spec_from_file_location("dictionary_iteration", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DictionaryIterationTests(unittest.TestCase):
    def test_bug_skips_alternating_lines(self):
        self.assertEqual(module.buggy_reader("alpha\nbeta\ngamma\ndelta\n"), ["BETA", "DELTA"])

    def test_fix_reads_every_line(self):
        self.assertEqual(module.corrected_reader("alpha\nbeta\ngamma\ndelta\n"), ["ALPHA", "BETA", "GAMMA", "DELTA"])

    def test_single_line_bug_returns_empty_string(self):
        self.assertEqual(module.buggy_reader("alpha\n"), [""])

    def test_single_line_fix(self):
        self.assertEqual(module.corrected_reader("alpha\n"), ["ALPHA"])


if __name__ == "__main__":
    unittest.main()
