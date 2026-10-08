#!/usr/bin/env python3
"""离线测试：不连飞书，只验证本地任务状态机。"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent / 'dispatch.py'


def run(state_dir, *args):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), '--state-dir', str(state_dir), *args],
        capture_output=True, text=True,
    )
    out = json.loads(result.stdout) if result.stdout.strip() else None
    return result.returncode, out


def valid_task(task_id='t1', **overrides):
    data = {
        'id': task_id,
        'owner': '小爷',
        'assignee': '小王',
        'goal': '写一篇产品介绍',
        'deliverables': ['800字初稿'],
        'acceptance': ['包含三个卖点', '无错别字'],
        'due': '待协商',
        'timezone': 'Asia/Shanghai',
        'materials': [],
        'feedback': '飞书文档追加回复',
        'authorization': '仅可读写指定文档',
        'mode': 'text',
    }
    data.update(overrides)
    return data


class DispatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.state_dir = Path(self.tmp.name)
        self.task_path = self.state_dir / 'task.json'

    def tearDown(self):
        self.tmp.cleanup()

    def write_task(self, data):
        self.task_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        return self.task_path

    def test_register_valid_task_starts_draft(self):
        self.write_task(valid_task())
        code, out = run(self.state_dir, 'register', '--task-file', str(self.task_path))
        self.assertEqual(code, 0, msg=out)
        self.assertEqual(out['state'], 'draft')

    def test_register_duplicate_id_rejected(self):
        self.write_task(valid_task())
        run(self.state_dir, 'register', '--task-file', str(self.task_path))
        code, out = run(self.state_dir, 'register', '--task-file', str(self.task_path))
        self.assertNotEqual(code, 0)
        self.assertIn('already registered', out['detail'])

    def test_register_missing_field_rejected(self):
        data = valid_task()
        del data['acceptance']
        self.write_task(data)
        code, out = run(self.state_dir, 'register', '--task-file', str(self.task_path))
        self.assertNotEqual(code, 0)

    def test_register_bad_id_rejected(self):
        self.write_task(valid_task(task_id='任务 1'))
        code, out = run(self.state_dir, 'register', '--task-file', str(self.task_path))
        self.assertNotEqual(code, 0)

    def test_register_bad_mode_rejected(self):
        self.write_task(valid_task(mode='automatic'))
        code, out = run(self.state_dir, 'register', '--task-file', str(self.task_path))
        self.assertNotEqual(code, 0)

    def test_legal_transition_path(self):
        self.write_task(valid_task())
        run(self.state_dir, 'register', '--task-file', str(self.task_path))
        for to_state in ('assigned', 'accepted', 'in_progress', 'submitted', 'passed'):
            code, out = run(self.state_dir, 'transition', '--task-id', 't1', '--to', to_state, '--evidence', '已核实')
            self.assertEqual(code, 0, msg=out)
            self.assertEqual(out['state'], to_state)

    def test_illegal_transition_rejected(self):
        self.write_task(valid_task())
        run(self.state_dir, 'register', '--task-file', str(self.task_path))
        code, out = run(self.state_dir, 'transition', '--task-id', 't1', '--to', 'passed', '--evidence', '已核实')
        self.assertNotEqual(code, 0)
        self.assertIn('invalid transition', out['detail'])

    def test_empty_evidence_rejected(self):
        self.write_task(valid_task())
        run(self.state_dir, 'register', '--task-file', str(self.task_path))
        code, out = run(self.state_dir, 'transition', '--task-id', 't1', '--to', 'assigned', '--evidence', '   ')
        self.assertNotEqual(code, 0)

    def test_terminal_task_cannot_revise(self):
        self.write_task(valid_task())
        run(self.state_dir, 'register', '--task-file', str(self.task_path))
        run(self.state_dir, 'transition', '--task-id', 't1', '--to', 'cancelled', '--evidence', '用户取消')
        self.write_task(valid_task(goal='改过的目标'))
        code, out = run(self.state_dir, 'revise', '--task-file', str(self.task_path))
        self.assertNotEqual(code, 0)
        self.assertIn('terminal task', out['detail'])

    def test_revise_rejects_assignee_change(self):
        self.write_task(valid_task())
        run(self.state_dir, 'register', '--task-file', str(self.task_path))
        self.write_task(valid_task(assignee='小李'))
        code, out = run(self.state_dir, 'revise', '--task-file', str(self.task_path))
        self.assertNotEqual(code, 0)

    def test_tasks_lists_registered(self):
        self.write_task(valid_task())
        run(self.state_dir, 'register', '--task-file', str(self.task_path))
        code, out = run(self.state_dir, 'tasks')
        self.assertEqual(code, 0)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]['id'], 't1')

    def test_doctor_reports_state_dir(self):
        code, out = run(self.state_dir, 'doctor')
        self.assertEqual(code, 0)
        self.assertEqual(out['state_dir'], str(self.state_dir))
        self.assertIn('lark_cli', out)

    def test_declined_reachable_from_in_progress(self):
        self.write_task(valid_task())
        run(self.state_dir, 'register', '--task-file', str(self.task_path))
        for to_state in ('assigned', 'accepted', 'in_progress'):
            run(self.state_dir, 'transition', '--task-id', 't1', '--to', to_state, '--evidence', '已核实')
        code, out = run(self.state_dir, 'transition', '--task-id', 't1', '--to', 'declined', '--evidence', '对方明确拒绝')
        self.assertEqual(code, 0, msg=out)
        self.assertEqual(out['state'], 'declined')


if __name__ == '__main__':
    unittest.main()
