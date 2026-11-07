import tempfile
import unittest
from pathlib import Path
from memory_integrity import init, tamper, verify, recover, write_json, read_json


class MemoryIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        init(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_detect_tamper_and_recover(self):
        self.assertTrue(verify(self.root))
        tamper(self.root)
        self.assertFalse(verify(self.root))
        recover(self.root)
        self.assertTrue(verify(self.root))

    def test_detect_missing_record(self):
        write_json(self.root / 'working/memories.json', {'records': []})
        self.assertFalse(verify(self.root))

    def test_detect_extra_record(self):
        data = read_json(self.root / 'working/memories.json')
        data['records'].append({'id': 'extra', 'statement': 'injected'})
        write_json(self.root / 'working/memories.json', data)
        self.assertFalse(verify(self.root))

    def test_refuse_corrupted_trusted_snapshot(self):
        tamper(self.root)
        write_json(self.root / 'trusted/memories.json', {'records': []})
        with self.assertRaises(ValueError):
            recover(self.root)


if __name__ == '__main__':
    unittest.main()
