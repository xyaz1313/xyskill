#!/usr/bin/env python3
"""回归套件运行器（零依赖）。三个子命令：

  check                     核对仓库当前数据是否仍与用例的标注一致（数据漂移检测，不需要模型）
  emit  [--kind K] [--out]  导出答题卷：只含输入，answer 留空，交给当前环境的模型填
  score <answers.jsonl>     对照答题卷算一致率，按 kind / 强弱标签分开报告，--min 低于阈值退出码 1

判断本身不在这里跑：这套架构里判断外包给运行环境的模型（Claude Code 会话），脚本只负责
出题、对答案、查数据漂移。答题卷格式：每行 {"id": "...", "answer": "<label>"}。
"""
import json, os, sys, argparse, time
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CASES = os.path.join(HERE, "cases")
KN = os.path.join(ROOT, "knowledge")

LABELS = {
    "evidence_link": ["supports", "not_evidence"],
    "topic_reclass": ["keep", "remove"],
    "contradicts": ["contradicts", "same_direction", "different_scene"],
    "dedup": ["merge", "refines", "keep_separate"],
    "name_collision": ["same_concept_variant", "layered_variant", "distinct_concept", "not_an_entity"],
    "aggregate_gap": ["aggregate_present_named_generically", "split_verifiable", "other"],
}


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def load_cases(kind=None):
    rows = []
    for name in sorted(os.listdir(CASES)):
        if not name.endswith(".jsonl"):
            continue
        for r in load_jsonl(os.path.join(CASES, name)):
            if kind and r["kind"] != kind:
                continue
            rows.append(r)
    return rows


def cmd_check(args):
    if not os.path.isfile(os.path.join(KN, "atoms.jsonl")):
        print(f"check 需要 XY 自己的知识库（{KN}/atoms.jsonl），这是 XY 内部数据漂移质检，不是 G-1 闸门流程的一部分；"
              "企业工程只用 emit / score 两个命令。")
        return 2
    atoms = {a["id"]: a for a in load_jsonl(os.path.join(KN, "atoms.jsonl"))}
    concepts = {c["id"]: c for c in load_jsonl(os.path.join(KN, "concepts.jsonl"))}
    drift = []
    checked = 0
    for r in load_cases():
        rc = r.get("repo_check")
        if not rc:
            continue
        checked += 1
        t = rc["type"]
        ok = True
        if t == "in_evidence":
            ok = rc["atom_id"] in concepts.get(rc["concept_id"], {}).get("evidence_atom_ids", [])
        elif t == "not_in_evidence":
            ok = rc["atom_id"] not in concepts.get(rc["concept_id"], {}).get("evidence_atom_ids", [])
        elif t == "topic_present":
            ok = rc["topic"] in (atoms.get(rc["atom_id"], {}).get("topics") or [])
        elif t == "topic_absent":
            ok = rc["atom_id"] in atoms and rc["topic"] not in (atoms[rc["atom_id"]].get("topics") or [])
        elif t == "related_rel":
            rels = atoms.get(rc["a"], {}).get("related") or []
            ok = any(isinstance(x, dict) and x.get("id") == rc["b"] and x.get("rel") == rc["rel"] for x in rels)
        elif t == "concept_rel":
            rels = concepts.get(rc["a"], {}).get("related_concepts") or []
            ok = any(x.get("id") == rc["b"] and x.get("rel") == rc["rel"] for x in rels)
        elif t == "concept_no_rel":
            ra = concepts.get(rc["a"], {}).get("related_concepts") or []
            rb = concepts.get(rc["b"], {}).get("related_concepts") or []
            ok = not any(x.get("id") == rc["b"] for x in ra) and not any(x.get("id") == rc["a"] for x in rb)
        if not ok:
            drift.append((r["id"], t, rc))
    print(f"核对用例数: {checked}，与仓库数据不一致: {len(drift)}")
    for cid, t, rc in drift[:50]:
        print(f"  {cid} [{t}] {json.dumps(rc, ensure_ascii=False)}")
    return 1 if drift else 0


def cmd_emit(args):
    rows = load_cases(args.kind)
    out = args.out or os.path.join(HERE, f"worksheet-{time.strftime('%Y%m%d-%H%M%S')}.jsonl")
    with open(out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps({"id": r["id"], "kind": r["kind"], "labels": LABELS[r["kind"]],
                                "input": r["input"], "answer": None}, ensure_ascii=False) + "\n")
    print(f"答题卷: {out}（{len(rows)} 题）")
    print("填法：逐行把 answer 填成 labels 里的一个值，然后 python3 regression/run.py score <文件>")
    return 0


def cmd_score(args):
    expected = {r["id"]: r for r in load_cases()}
    answers = {a["id"]: a.get("answer") for a in load_jsonl(args.answers)}
    unknown = [i for i in answers if i not in expected]
    if unknown:
        print(f"警告：{len(unknown)} 个作答 id 不在用例集里，已忽略：{unknown[:5]}")
    answered = sum(1 for i, v in answers.items() if i in expected and v is not None)
    if answered == 0:
        print("没有任何有效作答（answer 全为 null 或 id 全不匹配）")
        return 1
    stat = defaultdict(lambda: {"n": 0, "ok": 0})
    confusion = defaultdict(int)
    missing = 0
    for cid, r in expected.items():
        if args.kind and r["kind"] != args.kind:
            continue
        ans = answers.get(cid)
        if ans is None:
            missing += 1
            continue
        key = (r["kind"], r.get("strength", "strong"))
        stat[key]["n"] += 1
        exp = r["expected"]["label"]
        if ans == exp:
            stat[key]["ok"] += 1
        else:
            confusion[(r["kind"], exp, ans)] += 1
    total_n = sum(v["n"] for k, v in stat.items() if k[1] == "strong")
    total_ok = sum(v["ok"] for k, v in stat.items() if k[1] == "strong")
    print(f"{'kind':18} {'标签强度':8} {'题数':>4} {'一致':>4} {'一致率':>7}")
    for (kind, strength), v in sorted(stat.items()):
        print(f"{kind:18} {strength:8} {v['n']:4d} {v['ok']:4d} {v['ok']/v['n']:7.1%}")
    if confusion:
        print("\n错判分布（kind / 期望 → 作答 : 次数）")
        for (kind, exp, ans), n in sorted(confusion.items(), key=lambda x: -x[1]):
            print(f"  {kind} / {exp} → {ans} : {n}")
    if missing:
        print(f"\n未作答: {missing}")
    rate = total_ok / total_n if total_n else 0.0
    print(f"\n强标签总一致率: {rate:.1%}（{total_ok}/{total_n}）")
    if args.min is not None and rate < args.min:
        print(f"低于阈值 {args.min:.0%}：先调规则或换模型，不要开工")
        return 1
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    e = sub.add_parser("emit"); e.add_argument("--kind"); e.add_argument("--out")
    s = sub.add_parser("score"); s.add_argument("answers"); s.add_argument("--kind"); s.add_argument("--min", type=float)
    args = ap.parse_args()
    sys.exit({"check": cmd_check, "emit": cmd_emit, "score": cmd_score}[args.cmd](args))
