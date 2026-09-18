#!/usr/bin/env python3
"""XY 原子库本体校验（零依赖）。规则见 knowledge/ontology-schema.md。
用法：python3 scripts/ontology-lint.py [--file knowledge/atoms.jsonl] [--profile knowledge/profile.json]
只读，不改数据；退出码非0表示发现违规。

不变核（type 枚举、rel 枚举、结构硬规则）写死在这里；画像（topics 枚举、id 格式）从 profile.json 读，
默认取 atoms.jsonl 同目录的 profile.json，找不到就用内置的 XY 默认值。
"""
import json, sys, re, argparse, os

VALID_TYPES = {"principle", "method", "case", "anti-pattern", "definition", "number", "insight", "risk"}
VALID_RELS = {"supports", "contradicts", "example_of", "prerequisite_of", "refines"}
DEFAULT_TOPICS = {
    "商业案例与实战复盘", "团队与模式设计", "认知与心态", "私域运营", "流量获取",
    "AI与工具", "成交与话术", "选品逻辑", "内容创作与平台", "IP人设",
    "合规与风控", "新人起步方法论", "中国市场与下沉", "通用商业管理",
    "本体论与FDE方法论",
}
DEFAULT_ID_PATTERN = r"^[A-Z0-9]+-[A-Z0-9-]+[a-z]?$"  # 允许 RZP-020b 这类子编号后缀


def load_profile(atoms_path, explicit=None):
    """画像查找顺序：--profile 显式 > atoms 同目录 profile.json（XY 布局）> 工作区 ontology/profile.json（企业布局）。"""
    kn = os.path.dirname(os.path.abspath(atoms_path))
    cands = [explicit] if explicit else [os.path.join(kn, "profile.json"), os.path.join(os.path.dirname(kn), "ontology", "profile.json")]
    for cand in cands:
        if cand and os.path.isfile(cand):
            with open(cand, encoding="utf-8") as f:
                return json.load(f), cand
    if explicit:
        raise SystemExit(f"profile 不存在: {explicit}")
    return None, None


def _resolve(profile_path, rel):
    if not rel:
        return None
    if os.path.isabs(rel):
        return rel
    base = os.path.dirname(os.path.abspath(profile_path)) if profile_path else os.getcwd()
    for b in (base, os.path.dirname(base)):
        c = os.path.join(b, rel)
        if os.path.exists(c):
            return c
    return None


def load_blocklist(profile, profile_path):
    """来源名单：一行一个名字/笔名/账号名，# 开头是注释。命中即违规——'重塑不照搬'的第一道机器检查。"""
    p = _resolve(profile_path, (profile or {}).get("blocklist_file"))
    if not p:
        return [], None
    names = []
    for l in open(p, encoding="utf-8"):
        l = l.strip()
        if l and not l.startswith("#"):
            names.append(l)
    return names, p


def load_source_windows(sources_dir, width=24):
    """第三方原始素材的定长字符窗口集合。原子 knowledge 里出现任何一个完整窗口 = 原文照搬。
    只在显式给 --sources-dir 时启用；素材目录通常在 .gitignore 里，不进仓库。"""
    win = set()
    if not sources_dir or not os.path.isdir(sources_dir):
        return win
    strip = re.compile(r"\s+")
    for root, _, files in os.walk(sources_dir):
        for fn in files:
            if not fn.lower().endswith((".txt", ".md", ".srt", ".json", ".jsonl")):
                continue
            try:
                t = strip.sub("", open(os.path.join(root, fn), encoding="utf-8", errors="ignore").read())
            except OSError:
                continue
            for i in range(0, max(0, len(t) - width + 1)):
                win.add(t[i:i + width])
    return win


def lint(path, profile=None, profile_path=None, sources_dir=None, window=24):
    VALID_TOPICS = set(profile["topics"]) if profile and profile.get("topics") else DEFAULT_TOPICS
    ID_PATTERN = re.compile((profile or {}).get("id_pattern") or DEFAULT_ID_PATTERN)
    blocklist, blocklist_path = load_blocklist(profile, profile_path)
    windows = load_source_windows(sources_dir, window)
    ws = re.compile(r"\s+")
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

        text = (d.get("knowledge") or "") + " " + (d.get("original") or "")
        for nm in blocklist:
            if nm in text:
                issues.append((lineno, aid, f"命中来源名单: {nm!r}"))
        if windows:
            k = ws.sub("", d.get("knowledge") or "")
            for i in range(0, max(0, len(k) - window + 1), 4):
                if k[i:i + window] in windows:
                    issues.append((lineno, aid, f"疑似原文照搬(与素材有≥{window}字连续重合): …{k[i:i + window]}…"))
                    break

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
        "blocklist": blocklist_path,
        "blocklist_names": len(blocklist),
        "source_windows": len(windows),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge", "atoms.jsonl"))
    ap.add_argument("--profile", help="画像文件；默认取 atoms.jsonl 同目录的 profile.json")
    ap.add_argument("--sources-dir", help="第三方原始素材目录；给了就做'原文照搬'检查（≥--window 字连续重合即违规）")
    ap.add_argument("--window", type=int, default=24)
    ap.add_argument("--max-print", type=int, default=30)
    args = ap.parse_args()

    profile, profile_path = load_profile(args.file, args.profile)
    result = lint(args.file, profile, profile_path, args.sources_dir, args.window)
    print(f"画像: {profile_path or '内置默认(XY)'}")
    print(f"来源名单: {result['blocklist'] or '无'}（{result['blocklist_names']} 个名字）；素材窗口: {result['source_windows']}")
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
