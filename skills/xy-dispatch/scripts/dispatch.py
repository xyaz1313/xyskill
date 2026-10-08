#!/usr/bin/env python3
"""xy-dispatch 本地任务状态机：人员派单记录与状态流转校验。
不触碰飞书；飞书实际读写由对话中调用 lark-doc/lark-im 完成。
"""
import argparse
import json
import re
import shutil
import sqlite3
import sys
import time
from pathlib import Path

TRANSITIONS = {
    'draft': {'assigned', 'cancelled'},
    'assigned': {'accepted', 'declined', 'blocked', 'submitted', 'cancelled'},
    'accepted': {'in_progress', 'blocked', 'submitted', 'declined', 'cancelled'},
    'in_progress': {'blocked', 'submitted', 'declined', 'cancelled'},
    'blocked': {'accepted', 'in_progress', 'submitted', 'needs_owner', 'declined', 'cancelled'},
    'submitted': {'passed', 'needs_revision', 'needs_owner', 'declined', 'cancelled'},
    'needs_revision': {'in_progress', 'blocked', 'submitted', 'cancelled'},
    'needs_owner': {'in_progress', 'needs_revision', 'passed', 'declined', 'cancelled'},
    'passed': set(), 'declined': set(), 'cancelled': set(),
}

REQUIRED_FIELDS = ('owner', 'assignee', 'goal', 'due', 'timezone', 'feedback', 'authorization')
LIST_FIELDS = ('deliverables', 'acceptance', 'materials')


def emit(obj):
    print(json.dumps(obj, ensure_ascii=False))


def default_dir():
    return Path.home() / '.xy' / 'dispatch'


def connect(root):
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    db = sqlite3.connect(root / 'state.sqlite3', timeout=10)
    db.row_factory = sqlite3.Row
    db.executescript('''
    CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY, data TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY, task_id TEXT, at REAL, data TEXT);
    ''')
    db.commit()
    return db


def load_task(db, ident):
    row = db.execute('SELECT data FROM tasks WHERE id=?', (ident,)).fetchone()
    if not row:
        raise ValueError('unknown task: ' + ident)
    return json.loads(row['data'])


def validate_task(data):
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,100}', data.get('id', '')):
        raise ValueError('invalid task id')
    for field in REQUIRED_FIELDS:
        if not data.get(field):
            raise ValueError('missing field: ' + field)
    for field in LIST_FIELDS:
        value = data.get(field)
        if not isinstance(value, list):
            raise ValueError(field + ' must be an array')
        if field != 'materials' and not value:
            raise ValueError(field + ' must not be empty')
    if data.get('mode') not in ('text', 'on_demand'):
        raise ValueError('mode must be text or on_demand')


def cmd_register(db, args):
    data = json.loads(args.task_file.read_text(encoding='utf-8'))
    validate_task(data)
    if data.get('state', 'draft') != 'draft':
        raise ValueError('new task must start in draft')
    data['state'] = 'draft'
    try:
        db.execute('INSERT INTO tasks VALUES(?,?)', (data['id'], json.dumps(data, ensure_ascii=False)))
    except sqlite3.IntegrityError:
        raise ValueError('task id already registered: ' + data['id'])
    db.commit()
    emit({'task_id': data['id'], 'state': data['state']})


def cmd_revise(db, args):
    data = json.loads(args.task_file.read_text(encoding='utf-8'))
    validate_task(data)
    old = load_task(db, data['id'])
    if old['state'] in ('passed', 'declined', 'cancelled'):
        raise ValueError('terminal task cannot be revised; register a new task instead')
    for field in ('assignee', 'owner'):
        if old.get(field) != data.get(field):
            raise ValueError(field + ' cannot change; register a new task instead')
    data['state'] = old['state']
    db.execute('UPDATE tasks SET data=? WHERE id=?', (json.dumps(data, ensure_ascii=False), data['id']))
    db.execute('INSERT INTO history(task_id, at, data) VALUES(?,?,?)',
               (data['id'], time.time(), json.dumps({'revision_before': old, 'revision_after': data}, ensure_ascii=False)))
    db.commit()
    emit({'task_id': data['id'], 'state': data['state']})


def cmd_transition(db, args):
    if not args.evidence.strip():
        raise ValueError('evidence cannot be blank')
    data = load_task(db, args.task_id)
    old_state = data['state']
    if args.to not in TRANSITIONS[old_state]:
        raise ValueError('invalid transition: ' + old_state + ' -> ' + args.to)
    data['state'] = args.to
    db.execute('UPDATE tasks SET data=? WHERE id=?', (json.dumps(data, ensure_ascii=False), args.task_id))
    db.execute('INSERT INTO history(task_id, at, data) VALUES(?,?,?)',
               (args.task_id, time.time(), json.dumps({'from': old_state, 'to': args.to, 'evidence': args.evidence}, ensure_ascii=False)))
    db.commit()
    emit(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-dir', type=Path, default=None)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor')
    sub.add_parser('init')
    sub.add_parser('tasks')
    for name in ('register', 'revise'):
        p = sub.add_parser(name)
        p.add_argument('--task-file', type=Path, required=True)
    tr = sub.add_parser('transition')
    tr.add_argument('--task-id', required=True)
    tr.add_argument('--to', choices=sorted(TRANSITIONS), required=True)
    tr.add_argument('--evidence', required=True)

    args = parser.parse_args()
    root_expanded = (args.state_dir or default_dir()).expanduser()
    root = root_expanded.resolve()

    if args.command == 'doctor':
        emit({'state_dir': str(root_expanded), 'exists': root.is_dir(),
              'lark_cli': shutil.which('lark-cli'),
              'auth_verified': False, 'mode_available': ['text', 'on_demand']})
        return

    db = connect(root)
    try:
        if args.command == 'init':
            emit({'initialized': str(root)})
        elif args.command == 'tasks':
            emit([json.loads(r[0]) for r in db.execute('SELECT data FROM tasks ORDER BY id')])
        elif args.command == 'register':
            cmd_register(db, args)
        elif args.command == 'revise':
            cmd_revise(db, args)
        elif args.command == 'transition':
            cmd_transition(db, args)
    finally:
        db.close()


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, sqlite3.Error) as exc:
        emit({'error': type(exc).__name__, 'detail': str(exc)})
        sys.exit(1)
