#!/usr/bin/env python3
"""从 knowledge/concepts.jsonl 生成 knowledge/concepts-index.md（零依赖，确定性）。

索引不再手工维护：节点改了就重跑本脚本。按 category 分组，每个节点一行：id · 标题 · 一句话摘要（取 summary 第一句，≤60 字）· 证据数 · 关系。
用法：python3 scripts/concepts-build-index.py [--concepts knowledge/concepts.jsonl] [--out knowledge/concepts-index.md] [--check]
--check：只比较，不写；索引与当前 concepts 不一致时退出码 1（给 CI / 提交前用）。
"""
import json, os, re, sys, argparse, time
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def first_sentence(s, n=60):
    s = re.split(r"[。；;\n]", s.strip(), 1)[0]
    return s if len(s) <= n else s[:n] + "…"


def build(concepts, atoms_count=None):
    by_cat = defaultdict(list)
    for c in concepts:
        by_cat[c.get("category", "未分类")].append(c)
    ids = {c["id"] for c in concepts}
    n_ev = sum(len(c.get("evidence_atom_ids", [])) for c in concepts)
    n_rel = sum(len(c.get("related_concepts") or []) for c in concepts)
    cross = sum(1 for c in concepts for r in c.get("related_concepts") or [] if r["id"].split("-")[1] != c["id"].split("-")[1])
    L = ["# 概念节点索引", "",
         f"由 `scripts/concepts-build-index.py` 从 `concepts.jsonl` 生成，手改无效。节点 {len(concepts)} 个 · 证据边 {n_ev} 条 · 节点关系 {n_rel} 条（跨 topic {cross}）· 覆盖 {len(by_cat)} 个 topic。",
         "", "| topic | 节点数 | 证据边 |", "|---|---|---|"]
    for cat, rows in sorted(by_cat.items(), key=lambda x: -len(x[1])):
        L.append(f"| {cat} | {len(rows)} | {sum(len(c.get('evidence_atom_ids', [])) for c in rows)} |")
    L.append("")
    for cat, rows in sorted(by_cat.items(), key=lambda x: -len(x[1])):
        L += [f"## {cat}（{len(rows)} 个）", "", "| id | 节点 | 一句话 | 证据 | 关系 |", "|---|---|---|---|---|"]
        for c in sorted(rows, key=lambda c: c["id"]):
            rels = "；".join(f"{r['rel']}→{r['id']}" for r in c.get("related_concepts") or []) or "—"
            L.append(f"| `{c['id']}` | {c['title']} | {first_sentence(c.get('summary', ''))} | {len(c.get('evidence_atom_ids', []))} | {rels} |")
        L.append("")
    # 关系总表
    L += ["## 节点关系总表", "", "| 从 | 关系 | 到 | 跨 topic |", "|---|---|---|---|"]
    for c in sorted(concepts, key=lambda c: c["id"]):
        for r in c.get("related_concepts") or []:
            L.append(f"| `{c['id']}` | {r['rel']} | `{r['id']}` | {'是' if r['id'].split('-')[1] != c['id'].split('-')[1] else ''} |")
    L.append("")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--concepts", default=os.path.join(ROOT, "knowledge", "concepts.jsonl"))
    ap.add_argument("--out", default=os.path.join(ROOT, "knowledge", "concepts-index.md"))
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    concepts = [json.loads(l) for l in open(a.concepts, encoding="utf-8") if l.strip()]
    text = build(concepts)
    if a.check:
        cur = open(a.out, encoding="utf-8").read() if os.path.isfile(a.out) else ""
        if cur != text:
            print("索引与 concepts.jsonl 不一致，请重跑 scripts/concepts-build-index.py"); return 1
        print("索引一致"); return 0
    open(a.out, "w", encoding="utf-8").write(text)
    print(f"索引已生成：{a.out}（{len(concepts)} 个节点）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
