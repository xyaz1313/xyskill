#!/usr/bin/env python3
"""合并器（consolidator）——把台账里的信号变成 G6 迭代闸门包。零依赖，离线，只产提案不改本体。

触发（二选一先到）：自上次合并以来新增原子 ≥ --min-atoms（默认 50），或距上次 ≥ --min-days（默认 7）。
--force 跳过触发判断。

提案类型（每条一行写进 proposals jsonl，同时渲染成闸门包 markdown）：
  evidence_add      显式 ok 标记里引用的原子不在该节点证据里；或 conflict/explicit 带来的新原子命中某节点
  coverage_gap      无节点命中的 query，按共有关键词聚簇，簇内 ≥ --gap-min 次
  co_retrieval      两个节点在同一次检索里反复同时命中（≥ --co-min 次），去重/refines 候选
  summary_stale     同一节点被标 wrong ≥ --wrong-min 次
  contradiction     conflict 记录，原样进 G3 通道
  new_case          explicit missing 带 text，走抽取入库（G1 规则）

自动应用白名单只有 evidence_add（且需 apply.py 再判一次同向条件）与 alias_add；其余全部人闸。

用法：consolidate.py [--workspace <工作区>] [--force] [--out gates/]
"""
import json, os, sys, time, argparse, re
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.realpath(__file__))
WS_DEFAULT = os.path.dirname(HERE)
TOKEN = re.compile(r"[一-鿿]{2,}|[a-zA-Z0-9]{2,}")


def load_jsonl(p):
    if not os.path.isfile(p):
        return []
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def kw(q):
    """与 atoms-search 同一套切法：整词保留，≥4 字的中文词再拆成 2 字子串，否则"会员积分"和"积分"对不上。"""
    out = []
    for t in TOKEN.findall(q or ""):
        out.append(t)
        if len(t) >= 4 and "一" <= t[0] <= "鿿":
            out += [t[i:i + 2] for i in range(0, len(t) - 1)]
    return set(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", default=WS_DEFAULT)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--min-atoms", type=int, default=50)
    ap.add_argument("--min-days", type=int, default=7)
    ap.add_argument("--gap-min", type=int, default=3)
    ap.add_argument("--co-min", type=int, default=3)
    ap.add_argument("--wrong-min", type=int, default=2)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    ws = a.workspace
    kn = os.path.join(ws, "knowledge")
    atoms = load_jsonl(os.path.join(kn, "atoms.jsonl"))
    concepts = load_jsonl(os.path.join(kn, "concepts.jsonl"))
    ledger = load_jsonl(os.path.join(kn, "usage_ledger.jsonl"))
    state_p = os.path.join(kn, ".consolidate_state.json")
    state = json.load(open(state_p, encoding="utf-8")) if os.path.isfile(state_p) else {"last_ts": "", "last_atom_count": 0, "runs": 0}

    new_atoms = len(atoms) - state.get("last_atom_count", 0)
    days = 10 ** 6
    if state.get("last_ts"):
        days = (time.time() - time.mktime(time.strptime(state["last_ts"], "%Y-%m-%dT%H:%M:%S"))) / 86400
    due = new_atoms >= a.min_atoms or days >= a.min_days
    if not due and not a.force:
        print(f"未到触发点：新增原子 {new_atoms}/{a.min_atoms}，距上次 {days:.1f}/{a.min_days} 天。--force 可强制。")
        return 0

    rows = [r for r in ledger if r["ts"] > state.get("last_ts", "")]
    cid = {c["id"]: c for c in concepts}
    aid = {x["id"]: x for x in atoms}
    props = []

    def add(kind, payload, auto=False):
        props.append({"id": f"P-{len(props)+1:03d}", "kind": kind, "auto_whitelist": auto, **payload})

    # evidence_add：ok 标记 / 新原子命中节点，但原子不在节点证据里
    for r in rows:
        if r["kind"] == "explicit" and r.get("mark") == "ok" or r["kind"] == "conflict":
            for c in r.get("concept_ids") or []:
                for at in r.get("atom_ids") or []:
                    if c in cid and at in aid and at not in cid[c]["evidence_atom_ids"]:
                        add("evidence_add", {"concept_id": c, "atom_id": at, "why": f"台账 {r['ts']} {r['kind']}", "atom_text": aid[at]["knowledge"][:160]},
                            auto=(r["kind"] == "explicit"))
    # coverage_gap：无命中 query 聚簇
    nohit = [r for r in rows if r["kind"] == "implicit" and not r.get("concept_ids")] + \
            [r for r in rows if r["kind"] == "explicit" and r.get("mark") == "missing"]
    clusters = defaultdict(list)
    for r in nohit:
        for k in kw(r.get("query", "")):
            clusters[k].append(r.get("query", ""))
    seen = set()
    for k, qs in sorted(clusters.items(), key=lambda x: -len(x[1])):
        if len(qs) < a.gap_min or k in seen:
            continue
        seen.add(k)
        add("coverage_gap", {"keyword": k, "count": len(qs), "sample_queries": list(dict.fromkeys(qs))[:5],
                             "why": "多次检索无节点命中，可能缺概念节点或节点标题/aliases 没覆盖这个说法"})
    # co_retrieval
    co = Counter()
    for r in rows:
        ids = sorted(set(r.get("concept_ids") or []))
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                co[(ids[i], ids[j])] += 1
    for (x, y), n in co.most_common():
        if n < a.co_min:
            break
        rel = any(z.get("id") == y for z in cid.get(x, {}).get("related_concepts") or []) or \
              any(z.get("id") == x for z in cid.get(y, {}).get("related_concepts") or [])
        if not rel:
            add("co_retrieval", {"a": x, "b": y, "count": n, "a_title": cid.get(x, {}).get("title"), "b_title": cid.get(y, {}).get("title"),
                                 "why": "反复同时命中且无关系：可能该建 refines，或是同一概念两个节点（G4 判断，默认保留）"})
    # summary_stale
    wrong = Counter(c for r in rows if r["kind"] == "explicit" and r.get("mark") == "wrong" for c in r.get("concept_ids") or [])
    for c, n in wrong.items():
        if n >= a.wrong_min and c in cid:
            notes = [r.get("note") for r in rows if r["kind"] == "explicit" and r.get("mark") == "wrong" and c in (r.get("concept_ids") or []) and r.get("note")]
            add("summary_stale", {"concept_id": c, "title": cid[c]["title"], "wrong_count": n, "notes": notes[:5],
                                  "why": "多次被标错：摘要可能失真或证据条件没写清（人闸，默认不改）"})
    # contradiction
    for r in rows:
        if r["kind"] == "conflict":
            add("contradiction", {"atom_id": (r.get("atom_ids") or [None])[0], "concept_id": (r.get("concept_ids") or [None])[0],
                                  "against_atom_id": r.get("against_atom_id"), "note": r.get("note"),
                                  "why": "入库时发现方向相反，进 G3：先判同场景、同维度，再判方向"})
    # new_case
    for r in rows:
        if r["kind"] == "explicit" and r.get("mark") == "missing" and r.get("text"):
            add("new_case", {"text": r["text"][:400], "query": r.get("query"), "why": "客户给了新案例，走 G1 抽取规则入库，再回到 evidence_add"})

    ts = time.strftime("%Y%m%d-%H%M%S")
    out_dir = a.out or os.path.join(ws, "ontology", "gates")
    os.makedirs(out_dir, exist_ok=True)
    pj = os.path.join(out_dir, f"G6-{ts}-proposals.jsonl")
    with open(pj, "w", encoding="utf-8") as f:
        for p in props:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    kinds = Counter(p["kind"] for p in props)
    md = [f"# 闸门包 · G6 迭代 · {os.path.basename(ws)} · {ts}", "",
          "| 项 | 值 |", "|---|---|",
          f"| 闸门 | G6 迭代（合并器提案） |",
          f"| 输入版本 | atoms {len(atoms)} 条 · concepts {len(concepts)} 个 · 台账新增 {len(rows)} 条（自 {state.get('last_ts') or '起始'}） |",
          f"| 触发 | 新增原子 {new_atoms} / 距上次 {min(days, 9999):.1f} 天{'（强制）' if a.force and not due else ''} |",
          f"| 提案文件 | `{os.path.basename(pj)}` |", "",
          "## 1. 输入摘要", "", "| 提案类型 | 数 |", "|---|---|"] + [f"| {k} | {v} |" for k, v in kinds.items()] + ["",
          "## 3. 规则提案 / 4. 待拍板", "",
          "| # | 类型 | 内容 | 模型建议（运行环境的模型填） | 默认 |", "|---|---|---|---|---|"]
    for p in props:
        body = {k: v for k, v in p.items() if k not in ("id", "kind", "auto_whitelist", "why")}
        default = "自动应用（apply.py 复核同向后）" if p["auto_whitelist"] else "不做"
        md.append(f"| {p['id']} | {p['kind']} | {json.dumps(body, ensure_ascii=False)[:220]} — {p['why']} |  | {default} |")
    md += ["", "规则：合并、拆分、contradicts、摘要重写永远人闸；白名单只有 evidence_add / alias_add。", "",
           "## 6. 决定记录（审的人填）", "", "把决定写成 decisions jsonl：`{\"id\":\"P-001\",\"decision\":\"accept|modify|reject\",\"reason\":\"...\",\"payload\":{...可选覆盖}}`，然后 `apply.py --proposals <本文件对应的 proposals.jsonl> --decisions <decisions.jsonl>`。", ""]
    pm = os.path.join(out_dir, f"G6-{ts}.md")
    with open(pm, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    state.update({"last_ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "last_atom_count": len(atoms), "runs": state.get("runs", 0) + 1, "last_packet": os.path.basename(pm)})
    json.dump(state, open(state_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"闸门包：{pm}\n提案：{pj}（{len(props)} 条：{dict(kinds)}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
