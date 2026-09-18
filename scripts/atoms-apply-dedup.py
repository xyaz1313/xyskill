#!/usr/bin/env python3
"""按人判定的决定文件执行近似重复处理（零依赖）。决定文件由 scripts/atoms-near-dup-scan.py 的报告经人工逐对判定得到。

决定行格式（jsonl）：{"a","b","decision":"merge|refines|keep","keep","from","to","rel","reason"}
- merge：保留 keep，删除另一条；全库 related 里指向被删 id 的改指 keep（去重、去自指）；concepts.jsonl 证据里被删 id 改指 keep（去重）；
          各 skills/*/references/atoms.jsonl 里删掉被删条；keep 原子加 merged_ids 记录来历
- refines：from 原子的 related 加 {"id": to, "rel": rel or "refines"}（已存在则跳过）
- keep：不动
默认 --dry-run 只打印；加 --apply 才写盘。写盘后自己跑 ontology-lint.py 与 regression/run.py check。
"""
import json, os, sys, glob, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def dump(p, rows):
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("decisions")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true", help="有'问题'行时仍写盘（问题行本身会被跳过）")
    a = ap.parse_args()
    dec = load(a.decisions)
    atoms_p = os.path.join(ROOT, "knowledge", "atoms.jsonl")
    concepts_p = os.path.join(ROOT, "knowledge", "concepts.jsonl")
    atoms = load(atoms_p)
    by = {x["id"]: x for x in atoms}
    concepts = load(concepts_p) if os.path.isfile(concepts_p) else []

    redirect = {}
    refines = []
    problems = []
    type_override = {}
    for d in dec:
        if d["decision"] == "merge":
            keep, drop = d.get("keep"), (d["b"] if d.get("keep") == d["a"] else d["a"])
            if keep not in by or drop not in by:
                problems.append(f"merge 涉及不存在的 id: {d}"); continue
            if keep == drop:
                problems.append(f"keep 与 drop 相同: {d}"); continue
            if drop in redirect and redirect[drop] != keep:
                problems.append(f"同一原子 {drop} 被两次并入不同目标（{redirect[drop]} / {keep}），以先出现的为准")
                continue
            redirect[drop] = keep
            if d.get("type"):
                type_override[keep] = d["type"]
        elif d["decision"] == "refines":
            fr, to = d.get("from"), d.get("to")
            if fr not in by or to not in by:
                problems.append(f"refines 涉及不存在的 id: {d}"); continue
            refines.append((fr, to, d.get("rel") or "refines"))
    # 链式重定向（A→B，B→C）压平；A→B 且 B→A 这种环是两份决定文件互相矛盾，必须停下
    def final(i):
        seen = set()
        while i in redirect and i not in seen:
            seen.add(i); i = redirect[i]
        return i, (i in redirect)
    flat = {}
    for k, v in redirect.items():
        f, cyc = final(v)
        if cyc:
            problems.append(f"合并环：{k} → {v} → … 回到自身，两份决定互相矛盾，已跳过这条")
            continue
        flat[k] = f
    redirect = flat
    drops = set(redirect)
    if problems and a.apply and not a.force:
        print("\n".join("  问题: " + p for p in problems))
        print("有问题未处理，拒绝写盘；确认无误后加 --force"); return 1

    n_rel_fix = n_ev_fix = n_ref_add = 0
    for x in atoms:
        if x["id"] in drops:
            continue
        rels = [r for r in (x.get("related") or []) if isinstance(r, dict)]
        new, seen = [], set()
        for r in rels:
            tid = redirect.get(r["id"], r["id"])
            if tid == x["id"]:
                n_rel_fix += 1; continue
            key = (tid, r["rel"])
            if key in seen:
                n_rel_fix += 1; continue
            seen.add(key)
            if tid != r["id"]:
                n_rel_fix += 1
            new.append({"id": tid, "rel": r["rel"]})
        if new or rels:
            x["related"] = new
    # 被删原子的出链随迁到 keep（改指向、去自指、去重）
    n_out = 0
    for drop, keep in redirect.items():
        k = by[keep]
        k.setdefault("merged_ids", []).append(drop)
        krels = [r for r in (k.get("related") or []) if isinstance(r, dict)]
        have = {(r["id"], r["rel"]) for r in krels}
        for r in by[drop].get("related") or []:
            if not isinstance(r, dict):
                continue
            tid = redirect.get(r["id"], r["id"])
            if tid == keep or (tid, r["rel"]) in have:
                continue
            krels.append({"id": tid, "rel": r["rel"]}); have.add((tid, r["rel"])); n_out += 1
        if krels:
            k["related"] = krels
    for keep, t in type_override.items():
        by[keep]["type"] = t
    for fr, to, rel in refines:
        if fr in drops or to in drops:
            continue
        x = by[fr]
        rels = [r for r in (x.get("related") or []) if isinstance(r, dict)]
        if not any(r["id"] == to and r["rel"] == rel for r in rels):
            rels.append({"id": to, "rel": rel}); x["related"] = rels; n_ref_add += 1
    for c in concepts:
        ev, seen = [], set()
        for e in c.get("evidence_atom_ids", []):
            t = redirect.get(e, e)
            if t in seen:
                n_ev_fix += 1; continue
            seen.add(t)
            if t != e:
                n_ev_fix += 1
            ev.append(t)
        c["evidence_atom_ids"] = ev

    print(f"决定 {len(dec)} 条：merge {len(redirect)}（删 {len(drops)} 条原子）/ refines 加关系 {n_ref_add} / related 修正 {n_rel_fix} / 出链随迁 {n_out} / 证据修正 {n_ev_fix} / type 覆盖 {len(type_override)}")
    for p in problems:
        print("  问题:", p)
    if not a.apply:
        print("[dry-run] 未写盘；加 --apply 执行"); return 0
    atoms_new = [x for x in atoms if x["id"] not in drops]
    dump(atoms_p, atoms_new)
    if concepts:
        dump(concepts_p, concepts)
    n_ref_files = 0
    for rp in glob.glob(os.path.join(ROOT, "skills", "*", "references", "atoms.jsonl")):
        rows = load(rp)
        kept = [r for r in rows if r.get("id") not in drops]
        if len(kept) != len(rows):
            dump(rp, kept); n_ref_files += 1
    print(f"已写盘：atoms {len(atoms)} → {len(atoms_new)}；references 子集更新 {n_ref_files} 个文件。请跑 ontology-lint.py 与 regression/run.py check。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
