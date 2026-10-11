import contextlib
from datetime import date, timedelta
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m = load('portable_memory', ROOT / 'skills/portable-memory/scripts/memory.py')
installer = load('memory_installer', ROOT / 'scripts/install.py')
connector = load('memory_connector', ROOT / 'skills/portable-memory/scripts/connect.py')


def markdown(text, **meta):
    header = {'schema_version': '0.3', 'kind': 'canonical', 'updated': str(date.today())}
    header.update(meta)
    return '---\n' + '\n'.join(f'{key}: {value}' for key, value in header.items()) + '\n---\n' + text + '\n'


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='portable-memory-test-')
        self.base = Path(self.temp.name).resolve()
        self.vault = self.base / 'vault'
        self.config = self.base / 'config.json'
        self.silent(m.initialize, self.vault, self.config)
        m.git(self.vault, 'config', '--local', 'user.name', 'Memory Test')
        m.git(self.vault, 'config', '--local', 'user.email', 'memory-test@example.invalid')

    def tearDown(self):
        self.temp.cleanup()

    def silent(self, function, *args, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return function(*args, **kwargs)

    def write(self, relative, body):
        path = self.vault / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding='utf-8')
        return path

    def plan(self, changes):
        path = self.base / 'plan.json'
        path.write_text(json.dumps({'schema_version': '0.3', 'changes': changes}), encoding='utf-8')
        return path

    def change(self, relative, body, reason='Verified user correction'):
        return {'path': relative, 'base_sha256': m.digest(self.vault / relative),
                'content': body, 'reason': reason}

    def test_init_is_idempotent_and_preserves_existing_data(self):
        profile = self.write('PROFILE.md', markdown('Existing user context'))
        self.silent(m.initialize, self.vault, self.config)
        self.assertIn('Existing user context', profile.read_text(encoding='utf-8'))
        self.assertFalse(self.silent(m.doctor, self.vault))
        review = m.metadata((self.vault / 'CURRENT.md').read_text(encoding='utf-8'))['review_after']
        self.assertEqual(date.fromisoformat(review), date.today() + timedelta(days=14))
        self.assertEqual(json.loads(self.config.read_text(encoding='utf-8'))['vault'], str(self.vault))

    def test_enclosing_public_repository_requires_private_exclusion(self):
        outer = self.base / 'toolkit'
        outer.mkdir()
        m.git(outer, 'init', '-b', 'main')
        with self.assertRaisesRegex(ValueError, 'ignore the private vault'):
            self.silent(m.initialize, outer / 'vault', self.base / 'other-config.json')
        (outer / '.gitignore').write_text('/vault/\n/local/\n')
        self.silent(m.initialize, outer / 'vault', self.base / 'other-config.json')
        self.assertTrue(m.independent(outer / 'vault'))
        self.assertEqual(m.git(outer, 'ls-files', '--', 'vault').stdout, '')

    def test_default_export_scope_and_private_exclusions(self):
        old = str(date.today() - timedelta(days=90))
        recent = self.write('projects/recent.md', markdown('Recent project'))
        active = self.write('projects/active.md', markdown('Old active project', updated=old, status='active'))
        self.write('projects/old.md', markdown('Old completed project', updated=old, status='completed'))
        self.write('projects/private.md', markdown('PRIVATE PROJECT TEXT', share='local'))
        kept = self.write('conversations/retained.md', markdown('Valuable older correction', updated=old, retain='true'))
        unresolved = self.write('conversations/unresolved.md', markdown('A proposal, not a fact', updated=old, status='unresolved'))
        self.write('conversations/candidate.md', markdown('Unverified candidate', kind='candidate'))
        self.write('inbox/raw.md', 'Raw source should stay out')
        self.write('MEMORY.md', markdown('INDEX PRIVATE NAME'))
        selected, _ = m.selection(self.vault, 30)
        names = {item['path'] for item in selected}
        for path in (recent, active, kept, unresolved):
            self.assertIn(path.relative_to(self.vault).as_posix(), names)
        self.assertNotIn('projects/old.md', names)
        self.silent(m.export, self.vault, 30)
        snapshot = next((self.vault / 'exports').glob('*.md')).read_text(encoding='utf-8')
        for omitted in ('PRIVATE PROJECT TEXT', 'INDEX PRIVATE NAME', 'Unverified candidate', 'Raw source should stay out', 'projects/private.md'):
            self.assertNotIn(omitted, snapshot)
        self.assertIn('status: unresolved', snapshot)
        self.assertIn('Valuable older correction', snapshot)

    def test_expired_current_and_legacy_topics_need_selection(self):
        self.write('CURRENT.md', markdown('EXPIRED STATE', review_after=str(date.today() - timedelta(days=1))))
        self.write('projects/legacy.md', '# Historic project\n')
        selected, _ = m.selection(self.vault, 30)
        self.assertNotIn('CURRENT.md', {i['path'] for i in selected})
        self.assertNotIn('projects/legacy.md', {i['path'] for i in selected})
        selected, _ = m.selection(self.vault, 30, include=['projects/legacy.md'])
        self.assertIn('projects/legacy.md', {i['path'] for i in selected})

    def test_snapshot_redacts_paths_and_omitted_links(self):
        self.write('PROFILE.md', markdown('Source directory: /Users/example/Documents/work\n[Secret project](projects/private.md)'))
        self.write('projects/private.md', markdown('Private', share='false'))
        self.silent(m.export, self.vault, 30)
        body = next((self.vault / 'exports').glob('*.md')).read_text(encoding='utf-8')
        self.assertNotIn('/Users/example', body)
        self.assertNotIn('Secret project', body)
        self.assertNotIn('projects/private.md', body)

    def test_import_stages_without_touching_canonical_memory(self):
        before = m.digest(self.vault / 'PROFILE.md')
        source = self.base / 'snapshot.md'
        source.write_text('---\nschema_version: 0.2\nkind: snapshot\n---\nImported context')
        self.silent(m.stage_import, self.vault, source)
        self.assertEqual(before, m.digest(self.vault / 'PROFILE.md'))
        staged = next((self.vault / 'inbox').glob('import-*.md'))
        self.assertIn('kind: candidate', staged.read_text(encoding='utf-8'))
        self.assertEqual(m.git(self.vault, 'check-ignore', '-q', str(staged), check=False).returncode, 0)

    def test_merge_preserves_unselected_projects_and_rejects_stale_hash(self):
        old = self.write('projects/untouched.md', markdown('Unexported historical project'))
        old_hash = m.digest(old)
        plan = self.plan([self.change('PROFILE.md', markdown('User correction'))])
        self.silent(m.apply_plan, self.vault, plan)
        self.assertEqual(old_hash, m.digest(old))
        self.assertIn('User correction', (self.vault / 'PROFILE.md').read_text(encoding='utf-8'))
        with self.assertRaisesRegex(ValueError, 'changed since review'):
            self.silent(m.apply_plan, self.vault, plan)
        self.assertEqual(len(list((self.vault / 'decisions').glob('*.md'))), 1)

    def test_merge_preflights_every_change_and_rolls_back_write_failure(self):
        original = (self.vault / 'PROFILE.md').read_text(encoding='utf-8')
        bad = self.plan([self.change('PROFILE.md', markdown('Should not be applied')),
                         {'path': '../outside.md', 'base_sha256': None, 'content': markdown('Outside'), 'reason': 'No'}])
        with self.assertRaises(ValueError):
            self.silent(m.apply_plan, self.vault, bad)
        self.assertEqual(original, (self.vault / 'PROFILE.md').read_text(encoding='utf-8'))
        plan = self.plan([self.change('PROFILE.md', markdown('New profile')),
                          self.change('projects/new.md', markdown('New project'))])
        real_atomic = m.atomic_text
        def fail_once(path, body):
            if path == self.vault / 'projects/new.md':
                raise OSError('Simulated disk failure')
            real_atomic(path, body)
        with patch.object(m, 'atomic_text', side_effect=fail_once):
            with self.assertRaisesRegex(OSError, 'disk failure'):
                self.silent(m.apply_plan, self.vault, plan)
        self.assertEqual(original, (self.vault / 'PROFILE.md').read_text(encoding='utf-8'))
        self.assertFalse((self.vault / 'projects/new.md').exists())
        self.assertFalse((self.vault / '.memory.lock').exists())

    def test_failed_rollback_preserves_recovery_backups(self):
        original = (self.vault / 'PROFILE.md').read_text(encoding='utf-8')
        plan = self.plan([self.change('PROFILE.md', markdown('New profile')),
                          self.change('projects/new.md', markdown('New project'))])
        real_atomic = m.atomic_text
        calls = {'profile': 0}
        def disk_fails(path, body):
            if path == self.vault / 'PROFILE.md':
                calls['profile'] += 1
                if calls['profile'] == 2:
                    raise OSError('Disk still unavailable during rollback')
            if path == self.vault / 'projects/new.md':
                raise OSError('Disk unavailable')
            real_atomic(path, body)
        with patch.object(m, 'atomic_text', side_effect=disk_fails):
            with self.assertRaisesRegex(ValueError, 'Rollback incomplete'):
                self.silent(m.apply_plan, self.vault, plan)
        recovery = next((self.vault / '.transactions').iterdir())
        self.assertEqual((recovery / '0.before.md').read_text(encoding='utf-8'), original)
        self.assertEqual(json.loads((recovery / 'manifest.json').read_text(encoding='utf-8'))[0]['path'], 'PROFILE.md')
        with self.assertRaisesRegex(ValueError, 'Pending transaction backups'):
            self.silent(m.export, self.vault, 30)

    def test_symlink_escape_and_existing_lock_stop_mutation(self):
        outside = self.base / 'outside.md'
        outside.write_text('Outside file')
        target = self.vault / 'projects/escaped.md'
        try:
            target.symlink_to(outside)
        except OSError:
            self.skipTest('Symlinks unavailable on this runner')
        with self.assertRaisesRegex(ValueError, 'leaves private vault'):
            m.inventory(self.vault)
        target.unlink()
        lock = self.vault / '.memory.lock'
        lock.write_text('Another process owns this lock')
        with self.assertRaisesRegex(ValueError, 'locked'):
            self.silent(m.export, self.vault, 30)
        self.assertEqual(lock.read_text(encoding='utf-8'), 'Another process owns this lock')

    def test_credentials_and_unknown_schema_do_not_enter_exports_or_imports(self):
        self.write('PROFILE.md', markdown('ghp_' + 'X' * 36))
        with self.assertRaisesRegex(ValueError, 'credential'):
            self.silent(m.export, self.vault, 30)
        self.assertEqual(list((self.vault / 'exports').iterdir()), [])
        source = self.base / 'unknown.md'
        source.write_text('---\nschema_version: 99\n---\nFuture data')
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            self.silent(m.stage_import, self.vault, source)

    def test_checkpoint_excludes_raw_data_and_preserves_user_index(self):
        self.write('sources/source.md', 'Raw source')
        self.write('exports/snapshot.md', 'Snapshot')
        self.write('inbox/import-test.md', 'Imported raw snapshot')
        self.silent(m.checkpoint, self.vault, 'Initial canonical version')
        tracked = m.git(self.vault, 'ls-files').stdout
        self.assertIn('PROFILE.md', tracked)
        self.assertNotIn('sources/source.md', tracked)
        self.assertNotIn('exports/snapshot.md', tracked)
        self.assertNotIn('inbox/import-test.md', tracked)
        self.write('user-notes.txt', 'User staged note')
        m.git(self.vault, 'add', 'user-notes.txt')
        with self.assertRaisesRegex(ValueError, 'staged changes'):
            self.silent(m.checkpoint, self.vault, 'Do not mix commits')
        self.assertEqual(m.git(self.vault, 'diff', '--cached', '--name-only').stdout.strip(), 'user-notes.txt')

    def test_failed_initial_commit_restores_empty_index(self):
        real_git = m.git
        def reject_commit(vault, *args, **kwargs):
            if args and args[0] == 'commit':
                raise ValueError('Simulated commit hook failure')
            return real_git(vault, *args, **kwargs)
        with patch.object(m, 'git', side_effect=reject_commit):
            with self.assertRaisesRegex(ValueError, 'hook failure'):
                self.silent(m.checkpoint, self.vault, 'First snapshot')
        self.assertEqual(m.git(self.vault, 'diff', '--cached', '--name-only').stdout, '')
        self.assertTrue((self.vault / 'PROFILE.md').is_file())

    def test_unicode_paths_and_config_survive_checkpoints(self):
        vault = self.base / '中文设备' / '记忆库'
        config = self.base / '中文设备配置.json'
        self.silent(m.initialize, vault, config)
        self.silent(m.initialize, vault, config)
        self.assertTrue(m.independent(vault))
        m.git(vault, 'config', 'user.name', 'Memory Test')
        m.git(vault, 'config', 'user.email', 'memory-test@example.invalid')
        topic = vault / 'projects/旅行计划.md'
        topic.write_text(markdown('中文项目与可靠记忆'), encoding='utf-8')
        self.silent(m.checkpoint, vault, 'Unicode snapshot')
        tracked = m.git(vault, 'ls-files', '-z').stdout.split('\0')
        self.assertIn('projects/旅行计划.md', tracked)
        topic.write_text(markdown('新的中文进度'), encoding='utf-8')
        self.silent(m.checkpoint, vault, 'Unicode correction')
        self.assertEqual(m.git(vault, 'status', '--porcelain').stdout, '')
        self.silent(m.export, vault, 30)
        snapshot = next((vault / 'exports').glob('*.md')).read_text(encoding='utf-8')
        self.assertIn('新的中文进度', snapshot)

    def test_public_github_remote_is_rejected(self):
        response = subprocess.CompletedProcess([], 0, stdout='false\n', stderr='')
        with patch.object(m, 'run', return_value=response):
            with self.assertRaisesRegex(ValueError, 'public repository rejected'):
                self.silent(m.configure_remote, self.vault, 'https://github.com/example/public.git', False)
        self.assertNotIn('origin', m.git(self.vault, 'remote').stdout)

    def test_two_devices_fast_forward_and_divergence(self):
        remote = self.base / 'remote.git'
        m.run('git', 'init', '--bare', '-b', 'main', str(remote))
        self.silent(m.configure_remote, self.vault, str(remote), True)
        self.silent(m.checkpoint, self.vault, 'First snapshot')
        self.silent(m.sync, self.vault)
        second = self.base / 'second-device'
        m.run('git', 'clone', str(remote), str(second))
        m.git(second, 'config', 'user.name', 'Memory Test')
        m.git(second, 'config', 'user.email', 'memory-test@example.invalid')
        self.silent(m.configure_remote, second, str(remote), True)
        (second / 'PROFILE.md').write_text(markdown('Correction from second device'), encoding='utf-8')
        self.silent(m.checkpoint, second, 'Correction')
        self.silent(m.sync, second)
        self.silent(m.sync, self.vault)
        self.assertIn('Correction from second device', (self.vault / 'PROFILE.md').read_text(encoding='utf-8'))
        self.write('PROFILE.md', markdown('First device independent edit'))
        self.silent(m.checkpoint, self.vault, 'First edit')
        head = m.git(self.vault, 'rev-parse', 'HEAD').stdout
        (second / 'PROFILE.md').write_text(markdown('Second device independent edit'), encoding='utf-8')
        self.silent(m.checkpoint, second, 'Second edit')
        self.silent(m.sync, second)
        with self.assertRaisesRegex(ValueError, 'diverged'):
            self.silent(m.sync, self.vault)
        self.assertEqual(head, m.git(self.vault, 'rev-parse', 'HEAD').stdout)
        self.assertIn('First device independent edit', (self.vault / 'PROFILE.md').read_text(encoding='utf-8'))

    def test_installed_skill_runs_without_source_repository(self):
        target = self.base / 'installed/portable-memory'
        self.silent(installer.install, target)
        copy_vault = self.base / 'new-machine-memory'
        result = subprocess.run([sys.executable, str(target / 'scripts/memory.py'), '--config',
                                 str(self.base / 'new-config.json'), '--vault', str(copy_vault), 'init'],
                                cwd=self.base, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((copy_vault / 'LONG_TERM.md').is_file())
        self.silent(installer.install, target)
        (target / 'SKILL.md').write_text('Local custom instructions')
        with self.assertRaisesRegex(ValueError, 'local changes'):
            self.silent(installer.install, target, True)
        self.assertEqual((target / 'SKILL.md').read_text(encoding='utf-8'), 'Local custom instructions')

    def test_connect_preserves_rules_and_keeps_device_path_out_of_shared_files(self):
        project = self.base / 'project'
        project.mkdir()
        m.git(project, 'init', '-b', 'main')
        entry = project / 'AGENTS.md'
        entry.write_text('# Existing project rules\n\nKeep my build settings.\n')
        self.silent(connector.connect, self.vault, project, 'codex')
        first = entry.read_text(encoding='utf-8')
        self.silent(connector.connect, self.vault, project, 'codex')
        self.assertEqual(first, entry.read_text(encoding='utf-8'))
        self.assertIn('Keep my build settings.', first)
        self.assertNotIn(str(self.vault), first)
        self.assertEqual(m.git(project, 'check-ignore', '-q', '.portable-memory.local.json', check=False).returncode, 0)
        with patch.object(m.Path, 'cwd', return_value=project):
            self.assertEqual(m.default_config(), project / '.portable-memory.local.json')


if __name__ == '__main__':
    unittest.main()
