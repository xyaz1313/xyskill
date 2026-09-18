#!/usr/bin/env python3
"""把 atoms.jsonl 里 related 字段从纯ID列表升级成带 rel 类型的结构。
v1 规则：基于(源type, 目标type)类型对做系统性默认推断，不是逐条人工精读判断。
规则依据见 knowledge/ontology-schema.md 的 Relation 定义。
"""
import json, sys, os
from collections import Counter

ATOMS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge", "atoms.jsonl")


def infer_rel(src_type, tgt_type):
    if src_type == tgt_type:
        return "refines"
    if src_type == "definition" or tgt_type == "definition":
        return "prerequisite_of"
    if src_type == "case" and tgt_type in ("principle", "method"):
        return "example_of"
    if tgt_type == "case" and src_type in ("principle", "method"):
        return "supports"  # 反向：被案例佐证
    # 注：anti-pattern<->principle/method 抽查发现大量并非真实"矛盾"关系——
    # 很多是同一观点被不同来源重复收录(近似重复内容,分属anti-pattern/principle两个type)，
    # 也有弱相关/不相关的批量导入噪音。规则粒度不足以可靠判断"真矛盾"，
    # 不做contradicts的自动推断，统一走supports兜底，contradicts留给人工二次标注。
    return "supports"  # 默认：弱关联，互相佐证


def main(dry_run=True):
    atoms = {}
    lines = []
    with open(ATOMS_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            d = json.loads(line)
            atoms[d["id"]] = d
            lines.append(d)

    rel_counter = Counter()
    upgraded = 0
    for d in lines:
        rel_list = d.get("related")
        if not rel_list:
            continue
        new_rel = []
        changed = False
        for r in rel_list:
            if isinstance(r, dict):
                new_rel.append(r)  # 已是新格式，跳过
                continue
            tgt = atoms.get(r)
            if tgt is None:
                new_rel.append(r)  # 死链，理论上不存在（lint已确认0死链），保留原样以防万一
                continue
            rel = infer_rel(d.get("type"), tgt.get("type"))
            new_rel.append({"id": r, "rel": rel})
            rel_counter[rel] += 1
            changed = True
        if changed:
            d["related"] = new_rel
            upgraded += 1

    print(f"升级的原子数(拥有related且被转换): {upgraded}")
    print("推断出的rel分布:")
    for rel, cnt in rel_counter.most_common():
        print(f"  {rel:16s}: {cnt}")

    if dry_run:
        print("\n[dry-run] 未写回文件。加 --write 才会实际写入 atoms.jsonl")
        return

    with open(ATOMS_PATH, "w", encoding="utf-8") as f:
        for d in lines:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    print(f"\n已写回 {ATOMS_PATH}")


if __name__ == "__main__":
    main(dry_run="--write" not in sys.argv)
