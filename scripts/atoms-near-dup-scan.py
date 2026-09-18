#!/usr/bin/env python3
"""全库近似重复原子扫描（零依赖，只出报告，不改数据）。

两条路各扫一遍，因为它们抓的是不同的重复：
  路 1 · 全库措辞重合：字符 2-gram 集合，bottom-k 草图找候选对，精确 Jaccard 分档。抓得住"同一段话被收录两次"，
        抓不住"两段完全不同的话讲同一个道理"（已知的 XY-MB-030/296 这类只有 0.22，跟噪音分不开）。
  路 2 · 概念节点内：同一节点的证据原子本来就是"支撑同一个判断"的，在这个前提下再看措辞重合，阈值可以放低很多，
        因为"同观点"这个先验已经由节点给了。这是找"同观点不同措辞"型重复唯一靠谱的办法。

分档（建议只是建议，人工看过再定；本脚本不动数据）：
  A 合并候选   J ≥ 0.60，或 包含度 ≥ 0.90 且长度比 ≥ 0.6
  B 疑似细化   包含度 ≥ 0.80 且长度比 < 0.6
  C 高重叠     0.35 ≤ J < 0.60
  D 弱重叠     0.25 ≤ J < 0.35（只列前 --d-max 对）
  N 节点内     同一概念节点证据对，J ≥ --node-min（默认 0.18）

用法：python3 scripts/atoms-near-dup-scan.py [--file knowledge/atoms.jsonl] [--concepts knowledge/concepts.jsonl] [--out docs/reports/near-dup-scan.md]
"""
import json, re, os, sys, argparse, heapq, itertools, time
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUNCT = re.compile(r"[^一-鿿0-9a-zA-Z]")
KNOWN = {("XY-MB-030", "XY-MB-296"), ("XY-BK3-0073", "XY-BK3-0114")}


def norm(s):
    return PUNCT.sub("", s or "").lower()


def grams(s, n=2):
    return {s[i:i + n] for i in range(len(s) - n + 1)} if len(s) >= n else ({s} if s else set())


def measure(gi, gj):
    inter = len(gi & gj)
    if not inter:
        return 0.0, 0.0, 0.0
    small, big = (gi, gj) if len(gi) <= len(gj) else (gj, gi)
    return inter / len(gi | gj), inter / len(small), len(small) / len(big)


def tier_of(jac, cont, ratio, d_min):
    if jac >= 0.60 or (cont >= 0.90 and ratio >= 0.6):
        return "A"
    if cont >= 0.80 and ratio < 0.6:
        return "B"
    if jac >= 0.35:
        return "C"
    if jac >= d_min:
        return "D"
    return None


def suggest(tier, ai, aj):
    same_type = ai.get("type") == aj.get("type")
    same_src = ai.get("source_type") == aj.get("source_type")
    if tier == "A":
        s = "合并候选：留表述更完整/来源更硬的一条，另一条并入其 original 或删除"
        if not same_type: s += "；type 不同，合并前先定 type"
        if not same_src: s += "；来源不同——正是'同一观点被不同来源重复收录'"
        return s
    if tier == "B":
        return "保留两条，短条对长条建 refines；短条没有独立信息量就并入长条"
    if tier == "N":
        return "同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理"
    return "保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=os.path.join(ROOT, "knowledge", "atoms.jsonl"))
    ap.add_argument("--concepts", default=os.path.join(ROOT, "knowledge", "concepts.jsonl"))
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "reports", "near-dup-scan.md"))
    ap.add_argument("--jsonl", default=None)
    ap.add_argument("--k", type=int, default=12)
    ap.add_argument("--df-max", type=float, default=0.02)
    ap.add_argument("--bucket-max", type=int, default=150)
    ap.add_argument("--d-min", type=float, default=0.25)
    ap.add_argument("--d-max", type=int, default=120)
    ap.add_argument("--node-min", type=float, default=0.18)
    a = ap.parse_args()

    t0 = time.time()
    atoms = [json.loads(l) for l in open(a.file, encoding="utf-8") if l.strip()]
    idx = {x["id"]: i for i, x in enumerate(atoms)}
    G = [grams(norm(x.get("knowledge", ""))) for x in atoms]
    df = Counter()
    for g in G:
        df.update(g)
    n = len(atoms)
    stop = {g for g, c in df.items() if c > a.df_max * n}
    G = [g - stop for g in G]

    # 路 1
    buckets = defaultdict(list)
    for i, g in enumerate(G):
        for h in heapq.nsmallest(a.k, (hash(x) for x in g)):
            buckets[h].append(i)
    cand = set()
    for h, ids in buckets.items():
        if len(ids) <= a.bucket_max:
            cand.update(itertools.combinations(ids, 2))
    pairs = []
    for i, j in cand:
        jac, cont, ratio = measure(G[i], G[j])
        t = tier_of(jac, cont, ratio, a.d_min)
        if t:
            pairs.append((t, jac, cont, ratio, i, j))
    pairs.sort(key=lambda p: (p[0], -p[1]))
    d_rows = [p for p in pairs if p[0] == "D"][:a.d_max]
    pairs = [p for p in pairs if p[0] != "D"] + d_rows
    print(f"路1：原子 {n}，候选对 {len(cand)}，命中 {Counter(p[0] for p in pairs)}，{time.time()-t0:.1f}s", file=sys.stderr)

    # 路 2
    node_rows = []
    concepts = [json.loads(l) for l in open(a.concepts, encoding="utf-8") if l.strip()] if os.path.isfile(a.concepts) else []
    for c in concepts:
        ev = [idx[e] for e in c.get("evidence_atom_ids", []) if e in idx]
        # 规则条文库类节点（平台规则/条文）天然共用句式，节点内阈值抬到 0.35，否则几百对全是"微信规定……"的套话重合
        th = 0.35 if re.search(r"规则库|条文库|规则条文|合规措辞", c.get("title", "")) else a.node_min
        for i, j in itertools.combinations(ev, 2):
            jac, cont, ratio = measure(G[i], G[j])
            if jac >= th:
                node_rows.append((jac, cont, ratio, i, j, c["id"], c["title"]))
    node_rows.sort(key=lambda r: -r[0])
    print(f"路2：{len(concepts)} 个节点，节点内候选 {len(node_rows)}，{time.time()-t0:.1f}s", file=sys.stderr)

    found = {}
    for t, jac, cont, ratio, i, j in pairs:
        found[tuple(sorted((atoms[i]["id"], atoms[j]["id"])))] = f"路1 {t} J={jac:.2f}"
    for jac, cont, ratio, i, j, cid, _ in node_rows:
        found.setdefault(tuple(sorted((atoms[i]["id"], atoms[j]["id"]))), f"路2 {cid} J={jac:.2f}")
    kn_lines = []
    for k in sorted(KNOWN):
        if k in found:
            kn_lines.append(f"- {k[0]} / {k[1]}：✓ {found[k]}")
        else:
            gi, gj = G[idx[k[0]]], G[idx[k[1]]]
            jac, cont, ratio = measure(gi, gj)
            kn_lines.append(f"- {k[0]} / {k[1]}：✗ 未命中（2-gram J={jac:.2f}，低于阈值，且不在同一概念节点下）")

    tiers = Counter(p[0] for p in pairs)
    L = [f"# 全库近似重复原子扫描报告", "",
         f"生成：{time.strftime('%Y-%m-%d %H:%M')} · `scripts/atoms-near-dup-scan.py` · 原子 {n} 条 · 概念节点 {len(concepts)} 个 · 只出报告不改数据", "",
         "| 档 | 对数 | 含义 |", "|---|---|---|",
         f"| A | {tiers['A']} | 合并候选（措辞基本相同） |",
         f"| B | {tiers['B']} | 疑似细化（短条被长条高度包含） |",
         f"| C | {tiers['C']} | 高重叠（0.35 ≤ J < 0.60） |",
         f"| D | {tiers['D']} | 弱重叠（0.25 ≤ J < 0.35，只列前 {a.d_max}） |",
         f"| N | {len(node_rows)} | 同一概念节点内证据对，J ≥ {a.node_min} |", "",
         "## 先说结论", "",
         "- 字符相似度只能抓'同一段话被收录两次'。已知的两组'同观点不同措辞'重复，2-gram 重合只有 0.14–0.22，跟噪音分不开——**这类重复靠文本相似度找不出来**，这一点跟 concepts-schema.md 里两级漏斗的校准结论一致。",
         "- 找'同观点不同措辞'唯一靠谱的路是 N 档：先由概念节点给出'这几条支撑同一个判断'的先验，再在节点内比措辞。N 档的建议处理方式是按节点逐个人工读。",
         "- 平台规则库/条文库类节点的证据天然共用句式（'微信平台规定……'），节点内阈值单独抬到 0.35，否则全是套话重合。",
         "- 全部档位都是候选，**没有任何一条会被自动合并或删除**。", "",
         "## 已知遗留案例", ""] + kn_lines + [""]
    for t, title in (("A", "A · 合并候选"), ("B", "B · 疑似细化"), ("C", "C · 高重叠"), ("D", "D · 弱重叠")):
        rows = [p for p in pairs if p[0] == t]
        L += [f"## {title}（{len(rows)} 对）", ""]
        if not rows:
            L += ["（无）", ""]; continue
        L += ["| # | 原子对 | J | 包含 | type | 来源 | 建议 |", "|---|---|---|---|---|---|---|"]
        for k, (_, jac, cont, ratio, i, j) in enumerate(rows, 1):
            ai, aj = atoms[i], atoms[j]
            L.append(f"| {k} | `{ai['id']}` / `{aj['id']}` | {jac:.2f} | {cont:.2f} | {ai.get('type')} / {aj.get('type')} | {ai.get('source_type')} / {aj.get('source_type')} | {suggest(t, ai, aj)} |")
        L.append("")
        if t in ("A", "B", "C"):
            L += [f"### {t} 档原文对照（前 {min(len(rows), 30)} 对）", ""]
            for k, (_, jac, cont, ratio, i, j) in enumerate(rows[:30], 1):
                L += [f"**{t}-{k}** `{atoms[i]['id']}`：{atoms[i]['knowledge'][:150]}", "", f"`{atoms[j]['id']}`：{atoms[j]['knowledge'][:150]}", ""]
    L += [f"## N · 同一概念节点内证据对（{len(node_rows)} 对，按节点分组）", ""]
    by_node = defaultdict(list)
    for r in node_rows:
        by_node[(r[5], r[6])].append(r)
    for (cid, title), rows in sorted(by_node.items(), key=lambda x: -len(x[1])):
        L += [f"### {cid} {title}（{len(rows)} 对）", "", "| 原子对 | J | type | 建议 |", "|---|---|---|---|"]
        for jac, cont, ratio, i, j, _, _ in rows:
            ai, aj = atoms[i], atoms[j]
            L.append(f"| `{ai['id']}` / `{aj['id']}` | {jac:.2f} | {ai.get('type')} / {aj.get('type')} | {suggest('N', ai, aj)} |")
        L.append("")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    if a.jsonl:
        with open(a.jsonl, "w", encoding="utf-8") as f:
            for t, jac, cont, ratio, i, j in pairs:
                f.write(json.dumps({"tier": t, "a": atoms[i]["id"], "b": atoms[j]["id"], "jaccard": round(jac, 3), "containment": round(cont, 3)}, ensure_ascii=False) + "\n")
            for jac, cont, ratio, i, j, cid, _ in node_rows:
                f.write(json.dumps({"tier": "N", "concept": cid, "a": atoms[i]["id"], "b": atoms[j]["id"], "jaccard": round(jac, 3), "containment": round(cont, 3)}, ensure_ascii=False) + "\n")
    print(f"报告：{a.out}")


if __name__ == "__main__":
    main()
