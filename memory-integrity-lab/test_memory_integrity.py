import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
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
        before = self.files()
        with self.assertRaises(ValueError):
            recover(self.root)
        self.assertEqual(self.files(), before)

    def files(self, root=None):
        root = root or self.root
        return {str(p.relative_to(root)): p.read_bytes()
                for p in root.rglob('*') if p.is_file()}

    def test_init_refuses_existing_data_without_changing_any_file(self):
        path = self.root / 'working/memories.json'
        path.write_bytes(b'legitimate notes not in the snapshot\r\n')
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        try:
            init(self.root)
        except FileExistsError:
            pass
        after = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after, 'init must leave existing information intact')
        with self.assertRaises(FileExistsError):
            init(self.root)

    def test_recovery_preserves_legitimate_additions_as_exact_bytes(self):
        path = self.root / 'working/memories.json'
        data = read_json(path)
        data['records'].append({'id': 'new-note', 'statement': 'Legitimate later note'})
        write_json(path, data)
        original = path.read_bytes().replace(b'\n', b'\r\n')
        path.write_bytes(original)
        recover(self.root)
        self.assertTrue(verify(self.root))
        backups = list((self.root / 'backups').glob('*.bak'))
        self.assertEqual(len(backups), 1, 'recovery must preserve the working version')
        self.assertEqual(backups[0].read_bytes(), original)

    def test_init_checks_every_target_before_any_write(self):
        for relative in ('working/memories.json', 'trusted/memories.json',
                         'trusted/manifest.json'):
            with self.subTest(target=relative), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                path = root / relative
                path.parent.mkdir(parents=True)
                path.write_bytes(b'keep me')
                before = self.files(root)
                with self.assertRaises(FileExistsError):
                    init(root)
                self.assertEqual(self.files(root), before)

    def test_init_refuses_directory_at_target(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'trusted/manifest.json').mkdir(parents=True)
            with self.assertRaises(FileExistsError):
                init(root)
            self.assertFalse((root / 'working').exists())

    def test_init_exclusive_creation_refuses_late_file(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / 'working/memories.json'
            real_open = Path.open

            def create_before_open(path, mode='r', *args, **kwargs):
                if path == target and mode == 'x':
                    path.write_bytes(b'created after preflight')
                return real_open(path, mode, *args, **kwargs)

            with patch.object(Path, 'open', create_before_open):
                with self.assertRaises(FileExistsError):
                    init(root)
            self.assertEqual(target.read_bytes(), b'created after preflight')

    def test_preview_shows_changes_without_writing(self):
        tamper(self.root)
        before = self.files()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            recover(self.root, dry_run=True)
        self.assertEqual(self.files(), before)
        self.assertFalse((self.root / 'backups').exists())
        self.assertIn('--- working (before)', output.getvalue())
        self.assertIn('+++ trusted (after)', output.getvalue())
        self.assertIn('-      "statement": "A memory is always an instruction."', output.getvalue())

    def test_recovery_preserves_malformed_and_empty_working_files(self):
        path = self.root / 'working/memories.json'
        for original in (b'{broken JSON\r\n\xff', b''):
            with self.subTest(original=original):
                path.write_bytes(original)
                before = self.files()
                recover(self.root, dry_run=True)
                self.assertEqual(self.files(), before)
                backup = recover(self.root)
                self.assertEqual(backup.read_bytes(), original)
                self.assertTrue(verify(self.root))

    def test_recovery_missing_working_file(self):
        path = self.root / 'working/memories.json'
        path.unlink()
        recover(self.root, dry_run=True)
        self.assertFalse(path.exists())
        self.assertIsNone(recover(self.root))
        self.assertFalse((self.root / 'backups').exists())
        self.assertTrue(verify(self.root))

    def test_unchanged_recovery_is_noop(self):
        before = self.files()
        self.assertIsNone(recover(self.root))
        self.assertEqual(self.files(), before)
        self.assertFalse((self.root / 'backups').exists())

    def test_repeated_recovery_keeps_all_backups(self):
        path = self.root / 'working/memories.json'
        saved = []
        for content in (b'first working version', b'second working version'):
            path.write_bytes(content)
            saved.append((recover(self.root), content))
        self.assertNotEqual(saved[0][0], saved[1][0])
        for backup, content in saved:
            self.assertEqual(backup.read_bytes(), content)

    def test_backup_failure_aborts_without_changing_working(self):
        tamper(self.root)
        before = self.files()
        with patch('memory_integrity.os.fsync', side_effect=OSError('simulated full disk')):
            with self.assertRaises(OSError):
                recover(self.root)
        self.assertEqual(self.files(), before)

    def test_replace_failure_keeps_working_and_complete_backup(self):
        tamper(self.root)
        path = self.root / 'working/memories.json'
        original = path.read_bytes()
        with patch('memory_integrity.os.replace', side_effect=OSError('simulated failure')):
            with self.assertRaises(OSError):
                recover(self.root)
        self.assertEqual(path.read_bytes(), original)
        backups = list((self.root / 'backups').glob('*.bak'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)
        self.assertEqual(list(path.parent.glob('.restore-*')), [])

    def test_observed_concurrent_edit_aborts_recovery(self):
        import memory_integrity
        tamper(self.root)
        path = self.root / 'working/memories.json'
        original = path.read_bytes()
        save = memory_integrity.save_bytes

        def edit_after_staging(*args):
            result = save(*args)
            if args[2] == '.restore-':
                path.write_bytes(b'newer edit')
            return result

        with patch('memory_integrity.save_bytes', side_effect=edit_after_staging):
            with self.assertRaises(ValueError):
                recover(self.root)
        self.assertEqual(path.read_bytes(), b'newer edit')
        backup, = (self.root / 'backups').glob('*.bak')
        self.assertEqual(backup.read_bytes(), original)

    def test_symbolic_link_targets_are_refused(self):
        path = self.root / 'working/memories.json'
        path.unlink()
        try:
            path.symlink_to(self.root / 'absent')
        except (OSError, NotImplementedError):
            self.skipTest('symbolic links unavailable')
        with self.assertRaises(FileExistsError):
            init(self.root)
        with self.assertRaises(ValueError):
            recover(self.root)
        self.assertTrue(path.is_symlink())
        self.assertFalse((self.root / 'absent').exists())

    def cli(self, *arguments):
        return subprocess.run([sys.executable, str(Path(__file__).with_name('memory_integrity.py')),
                               *arguments, '--root', str(self.root)],
                              capture_output=True, text=True)

    def test_cli_recovery_requires_apply(self):
        tamper(self.root)
        before = self.files()
        for arguments in (('recover',), ('recover', '--dry-run')):
            result = self.cli(*arguments)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('PREVIEW ONLY', result.stdout)
            self.assertEqual(self.files(), before)
        result = self.cli('recover', '--apply')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('BACKUP:', result.stdout)
        self.assertTrue(verify(self.root))

    def test_cli_init_and_demo_refuse_existing_root(self):
        tamper(self.root)
        before = self.files()
        for command in ('init', 'demo'):
            result = self.cli(command)
            self.assertEqual(result.returncode, 2)
            self.assertIn('Refusing to initialize', result.stderr)
            self.assertNotIn('Traceback', result.stderr)
            self.assertEqual(self.files(), before)


if __name__ == '__main__':
    unittest.main()
