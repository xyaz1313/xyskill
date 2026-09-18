#!/usr/bin/env python3
"""应用 G6 决定：把人拍板后的提案落到 concepts.jsonl，写 concepts_revisions.jsonl，把判例回写 rules/precedents.jsonl。零依赖。

规则：
- 只处理 decisions 里出现的提案；没决定的提案不动。
- evidence_add 在 auto_whitelist=true 且 --auto 时可无决定自动应用，但还要过"同向"复核：该原子的 related 里
  没有指向节点任何既有证据的 contradicts；有就降级为人闸。
- alias_add 同上（白名单）。
- 其余类型（co_retrieval→refines、summary_stale→摘要重写、contradiction→contradicts、new_case）只在 decision=accept/modify 时应用；
  modify 时用 decisions 行里的 payload 覆盖提案字段。
- 每次改动 concepts.jsonl 都：version+1，写一条 revision（edit_source: human | pipeline），ledger_ref 指回提案 id。
- reject 也记判例（判例的价值一半在"为什么不"）。

用法：apply.py --proposals gates/G6-...-proposals.jsonl [--decisions decisions.jsonl] [--auto] [--workspace <工作区>] [--dry-run]
"""
import json, os, sys, time, argparse, shutil

HERE = os.path.dirname(os.path.realpath(__file__))
WS_DEFAULT = os.path.dirname(HERE)


def load_jsonl(p):
    if not os.path.isfile(p):
        return []
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def dump_jsonl(p, rows):
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    shutil.move(tmp, p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", default=WS_DEFAULT)
    ap.add_argument("--proposals", required=True)
    ap.add_argument("--decisions")
    ap.add_argument("--auto", action="store_true", help="无决定的白名单提案自动应用")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    ws = a.workspace
    kn = os.path.join(ws, "knowledge")
    cpath = os.path.join(kn, "concepts.jsonl")
    concepts = load_jsonl(cpath)
    cid = {c["id"]: c for c in concepts}
    atoms = {x["id"]: x for x in load_jsonl(os.path.join(kn, "atoms.jsonl"))}
    props = {p["id"]: p for p in load_jsonl(a.proposals)}
    decisions = {d["id"]: d for d in load_jsonl(a.decisions)} if a.decisions else {}
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    revisions, precedents, applied, held = [], [], [], []

    def bump(c, reason, source, ref):
        revisions.append({"concept_id": c["id"], "version": c.get("version", 1) + 1, "timestamp": now, "edit_source": source,
                          "prev_summary": c.get("summary"), "prev_evidence_atom_ids": list(c.get("evidence_atom_ids", [])),
                          "reason": reason, "ledger_ref": ref})
        c["version"] = c.get("version", 1) + 1

    def same_direction(concept, atom_id):
        ev = set(concept.get("evidence_atom_ids", []))
        for r in atoms.get(atom_id, {}).get("related") or []:
            if isinstance(r, dict) and r.get("rel") == "contradicts" and r.get("id") in ev:
                return False
        return True

    for pid, p in props.items():
        d = decisions.get(pid)
        kind = p["kind"]
        if d is None:
            if a.auto and p.get("auto_whitelist"):
                d = {"id": pid, "decision": "accept", "reason": "白名单自动应用", "_auto": True}
            else:
                continue
        dec = d.get("decision")
        payload = {**p, **(d.get("payload") or {})}
        precedents.append({"ts": now, "proposal_id": pid, "kind": kind, "decision": dec, "reason": d.get("reason"),
                           "payload": {k: v for k, v in payload.items() if k not in ("id", "auto_whitelist")}})
        if dec == "reject":
            continue
        source = "pipeline" if d.get("_auto") else "human"
        if kind == "evidence_add":
            c = cid.get(payload["concept_id"])
            if not c or payload["atom_id"] not in atoms:
                held.append((pid, "节点或原子不存在")); continue
            if d.get("_auto") and not same_direction(c, payload["atom_id"]):
                held.append((pid, "原子与节点既有证据有 contradicts，降级人闸")); continue
            if payload["atom_id"] in c["evidence_atom_ids"]:
                continue
            bump(c, f"evidence_add {payload['atom_id']}", source, pid)
            c["evidence_atom_ids"].append(payload["atom_id"]); applied.append(pid)
        elif kind == "alias_add":
            c = cid.get(payload["concept_id"])
            if not c: held.append((pid, "节点不存在")); continue
            al = c.setdefault("aliases", [])
            if payload["alias"] not in al:
                bump(c, f"alias_add {payload['alias']}", source, pid); al.append(payload["alias"]); applied.append(pid)
        elif kind == "co_retrieval":
            rel = payload.get("rel", "refines")
            x, y = cid.get(payload["a"]), cid.get(payload["b"])
            if not x or not y: held.append((pid, "节点不存在")); continue
            if rel == "merge":
                held.append((pid, "合并不由脚本执行：请人工合并后手动记 revision")); continue
            x.setdefault("related_concepts", [])
            if not any(z.get("id") == y["id"] for z in x["related_concepts"]):
                bump(x, f"related_concepts +{rel} {y['id']}", "human", pid)
                x["related_concepts"].append({"id": y["id"], "rel": rel}); applied.append(pid)
        elif kind == "summary_stale":
            c = cid.get(payload["concept_id"])
            if not c or not payload.get("new_summary"): held.append((pid, "需要 payload.new_summary")); continue
            bump(c, "summary rewrite after wrong marks", "human", pid); c["summary"] = payload["new_summary"]; applied.append(pid)
        elif kind == "contradiction":
            held.append((pid, "contradicts 落在 atoms.jsonl 的 related 字段，按 rules/contradicts.md 三步人工标注；脚本不代写"))
        elif kind == "new_case":
            held.append((pid, "新案例先走 G1 抽取入库，再回到 evidence_add"))

    if a.dry_run:
        print(f"[dry-run] 将应用 {len(applied)} 条，搁置 {len(held)} 条，判例 {len(precedents)} 条")
        for h in held: print("  搁置", h)
        return 0
    if applied:
        dump_jsonl(cpath, concepts)
        with open(os.path.join(kn, "concepts_revisions.jsonl"), "a", encoding="utf-8") as f:
            for r in revisions:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    if precedents:
        rp = os.path.join(ws, "ontology", "rules", "precedents.jsonl")
        os.makedirs(os.path.dirname(rp), exist_ok=True)
        with open(rp, "a", encoding="utf-8") as f:
            for r in precedents:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"应用 {len(applied)} 条：{applied}\n搁置 {len(held)} 条：")
    for h in held: print("  ", h)
    print(f"判例回写 {len(precedents)} 条 → ontology/rules/precedents.jsonl；revision {len(revisions)} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
