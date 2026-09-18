#!/usr/bin/env python3
"""使用台账（usage_ledger.jsonl）——G6 迭代机制的信号来源。零依赖，只追加。

三种信号（对应架构提案第 3 节）：
  explicit  用户对一次回答的显式标记：ok / wrong / missing，可附新案例文本
  implicit  检索日志：query 命中了哪些概念节点、原子（无命中也记，那是覆盖缺口信号）
  conflict  入库时发现新原子与某节点既有证据方向相反（G3 候选）

用法：
  ledger.py log --kind implicit --query "一转 定价" --concepts CPT-SY-002 --atoms IPP-031,XY-DY-053
  ledger.py log --kind explicit --query "..." --mark wrong --concepts CPT-SY-002 --note "客户说这条在他们行业不成立"
  ledger.py log --kind explicit --mark missing --query "..." --text "客户口述的新案例……"
  ledger.py log --kind conflict --atoms NEW-001 --concepts CPT-SY-002 --against IPP-031 --note "方向相反"
  ledger.py stats [--since 2026-09-01]
台账文件默认 <工作区>/knowledge/usage_ledger.jsonl；--file 覆盖。
"""
import json, os, sys, time, argparse
from collections import Counter

HERE = os.path.dirname(os.path.realpath(__file__))
DEFAULT = os.path.join(os.path.dirname(HERE), "knowledge", "usage_ledger.jsonl")


def split(s):
    return [x for x in (s or "").replace("，", ",").split(",") if x.strip()]


def cmd_log(a):
    row = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "kind": a.kind}
    if a.query: row["query"] = a.query
    if a.mark: row["mark"] = a.mark
    if a.concepts: row["concept_ids"] = split(a.concepts)
    if a.atoms: row["atom_ids"] = split(a.atoms)
    if a.against: row["against_atom_id"] = a.against
    if a.text: row["text"] = a.text
    if a.note: row["note"] = a.note
    if a.actor: row["actor"] = a.actor
    if a.kind == "explicit" and not a.mark:
        sys.exit("explicit 必须带 --mark ok|wrong|missing")
    if a.kind == "conflict" and not (a.atoms and a.concepts):
        sys.exit("conflict 必须带 --atoms 与 --concepts")
    os.makedirs(os.path.dirname(a.file), exist_ok=True)
    with open(a.file, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps(row, ensure_ascii=False))


def cmd_stats(a):
    if not os.path.isfile(a.file):
        print("台账不存在"); return
    rows = [json.loads(l) for l in open(a.file, encoding="utf-8") if l.strip()]
    if a.since:
        rows = [r for r in rows if r["ts"] >= a.since]
    kinds = Counter(r["kind"] for r in rows)
    marks = Counter(r.get("mark") for r in rows if r["kind"] == "explicit")
    nohit = sum(1 for r in rows if r["kind"] == "implicit" and not r.get("concept_ids"))
    concepts = Counter(c for r in rows for c in r.get("concept_ids") or [])
    print(f"记录 {len(rows)} 条：{dict(kinds)}；显式标记 {dict(marks)}；无节点命中的检索 {nohit}")
    print("被命中最多的节点：", concepts.most_common(8))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=DEFAULT)
    sub = ap.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("log")
    l.add_argument("--kind", required=True, choices=["explicit", "implicit", "conflict"])
    l.add_argument("--query"); l.add_argument("--mark", choices=["ok", "wrong", "missing"])
    l.add_argument("--concepts"); l.add_argument("--atoms"); l.add_argument("--against")
    l.add_argument("--text"); l.add_argument("--note"); l.add_argument("--actor")
    s = sub.add_parser("stats"); s.add_argument("--since")
    args = ap.parse_args()
    {"log": cmd_log, "stats": cmd_stats}[args.cmd](args)
