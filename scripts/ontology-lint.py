#!/usr/bin/env python3
"""XY 原子库本体校验（零依赖）。规则见 knowledge/ontology-schema.md。
用法：python3 scripts/ontology-lint.py [--file knowledge/atoms.jsonl]
只读，不改数据；退出码非0表示发现违规。
"""
import json, sys, re, argparse, os

VALID_TYPES = {"principle", "method", "case", "anti-pattern", "definition", "number", "insight", "risk"}
VALID_TOPICS = {
    "商业案例与实战复盘", "团队与模式设计", "认知与心态", "私域运营", "流量获取",
    "AI与工具", "成交与话术", "选品逻辑", "内容创作与平台", "IP人设",
    "合规与风控", "新人起步方法论", "中国市场与下沉", "通用商业管理",
}
VALID_RELS = {"supports", "contradicts", "example_of", "prerequisite_of", "refines"}
ID_PATTERN = re.compile(r"^[A-Z0-9]+-[A-Z0-9-]+[a-z]?$")  # 允许 RZP-020b 这类子编号后缀


def lint(path):
    atoms = {}
    rows = []
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception as e:
                rows.append((lineno, None, f"JSON解析失败: {e}"))
                continue
            atoms[d.get("id")] = d
            rows.append((lineno, d, None))

    issues = []
    legacy_related_format = 0
    typed_related_format = 0

    for lineno, d, parse_err in rows:
        if parse_err:
            issues.append((lineno, d.get("id") if d else "?", parse_err))
            continue
        aid = d.get("id")

        if not aid or not ID_PATTERN.match(aid):
            issues.append((lineno, aid, f"id格式不合法: {aid!r}"))

        t = d.get("type")
        if t not in VALID_TYPES:
            issues.append((lineno, aid, f"type不在枚举内: {t!r}"))

        for topic in d.get("topics") or []:
            if topic not in VALID_TOPICS:
                issues.append((lineno, aid, f"topic不在枚举内: {topic!r}"))

        rel_list = d.get("related")
        if rel_list:
            for r in rel_list:
                if isinstance(r, str):
                    legacy_related_format += 1
                    if r not in atoms and r not in [row[1].get("id") for _, row, _ in [] ]:
                        pass  # 死链检查放到第二遍(全部加载完再查)
                elif isinstance(r, dict):
                    typed_related_format += 1
                    if r.get("rel") not in VALID_RELS:
                        issues.append((lineno, aid, f"related.rel不在枚举内: {r.get('rel')!r} (指向 {r.get('id')})"))
                else:
                    issues.append((lineno, aid, f"related条目格式非法: {r!r}"))

        if t in ("case", "number") and not d.get("source_type"):
            issues.append((lineno, aid, f"{t}类型缺少source_type"))

    # 第二遍：死链检查（related 指向的 id 必须存在）
    dead_links = 0
    for lineno, d, parse_err in rows:
        if parse_err:
            continue
        for r in d.get("related") or []:
            rid = r.get("id") if isinstance(r, dict) else r
            if rid not in atoms:
                dead_links += 1
                issues.append((lineno, d.get("id"), f"related死链: 指向不存在的id {rid!r}"))

    return {
        "total_atoms": len(rows),
        "issues": issues,
        "legacy_related_format": legacy_related_format,
        "typed_related_format": typed_related_format,
        "dead_links": dead_links,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge", "atoms.jsonl"))
    ap.add_argument("--max-print", type=int, default=30)
    args = ap.parse_args()

    result = lint(args.file)
    print(f"原子总数: {result['total_atoms']}")
    print(f"related 旧格式(纯ID字符串)条目数: {result['legacy_related_format']}")
    print(f"related 新格式(带rel类型)条目数: {result['typed_related_format']}")
    print(f"死链数: {result['dead_links']}")
    print(f"违规总数: {len(result['issues'])}")
    print()
    for lineno, aid, msg in result["issues"][: args.max_print]:
        print(f"  行{lineno} [{aid}] {msg}")
    if len(result["issues"]) > args.max_print:
        print(f"  ...还有 {len(result['issues']) - args.max_print} 条未显示")

    sys.exit(1 if result["issues"] else 0)
