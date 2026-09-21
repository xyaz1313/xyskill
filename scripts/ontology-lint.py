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

    # 软规则（schema 里写了但不 fail 的）：anti-pattern 应有对立的 principle/method（related 里有 contradicts）
    warnings = []
    for lineno, d, parse_err in rows:
        if parse_err or d.get("type") not in ("anti-pattern", "risk"):
            continue
        rels = [r for r in (d.get("related") or []) if isinstance(r, dict)]
        if not any(r.get("rel") == "contradicts" for r in rels):
            warnings.append((lineno, d.get("id"), "anti-pattern 没有 contradicts 关联（软规则，不算违规）"))

    return {
        "total_atoms": len(rows),
        "issues": issues,
        "warnings": warnings,
        "legacy_related_format": legacy_related_format,
        "typed_related_format": typed_related_format,
        "dead_links": dead_links,
        "blocklist": blocklist_path,
        "blocklist_names": len(blocklist),
        "source_windows": len(windows),
    }


def lint_concepts(cpath, atoms_path, profile, max_summary=450):
    """concepts.jsonl 结构校验：id 唯一、证据存在、related 指向存在且 rel 在枚举内、category 在 topics 内、summary 长度、标题不重复。"""
    atoms = set()
    with open(atoms_path, encoding="utf-8") as f:
        for l in f:
            l = l.strip()
            if l:
                try:
                    atoms.add(json.loads(l).get("id"))
                except Exception:
                    pass
    concepts = [json.loads(l) for l in open(cpath, encoding="utf-8") if l.strip()]
    ids = [c.get("id") for c in concepts]
    idset = set(ids)
    topics = set(profile["topics"]) if profile and profile.get("topics") else DEFAULT_TOPICS
    issues, warnings = [], []
    seen_title = {}
    for i, c in enumerate(concepts, 1):
        cid = c.get("id")
        if ids.count(cid) > 1:
            issues.append((i, cid, "concept id 重复"))
        for e in c.get("evidence_atom_ids") or []:
            if e not in atoms:
                issues.append((i, cid, f"证据死链: {e}"))
        if len(c.get("evidence_atom_ids") or []) != len(set(c.get("evidence_atom_ids") or [])):
            issues.append((i, cid, "evidence_atom_ids 内有重复"))
        if not c.get("evidence_atom_ids"):
            issues.append((i, cid, "零证据节点"))
        for r in c.get("related_concepts") or []:
            if r.get("id") not in idset:
                issues.append((i, cid, f"related_concepts 死链: {r.get('id')}"))
            if r.get("rel") not in VALID_RELS:
                issues.append((i, cid, f"related_concepts.rel 不在枚举内: {r.get('rel')}"))
        if c.get("category") not in topics:
            issues.append((i, cid, f"category 不在 topics 内: {c.get('category')!r}"))
        n = len(c.get("summary") or "")
        if n > max_summary:
            issues.append((i, cid, f"summary {n} 字，超硬上限 {max_summary}"))
        elif n > 200:
            warnings.append((i, cid, f"summary {n} 字，超建议值 200"))
        t = c.get("title")
        if t in seen_title:
            issues.append((i, cid, f"标题与 {seen_title[t]} 完全重复"))
        seen_title.setdefault(t, cid)
    return {"total": len(concepts), "issues": issues, "warnings": warnings}


def _workspace(atoms_path):
    return os.path.dirname(os.path.dirname(os.path.abspath(atoms_path)))


def lint_actions(actions_dir, profile, registry_path):
    """G7 进入条件：ontology/actions/*.json 逐个校验。
    entity_class 必须是本体里的 Class（profile.entity_classes，缺省取 state_fields 的键）；state_field 必须在
    profile.state_fields[entity_class] 里声明；rules 必须能在规则注册表（scaffold.export_registry 导出的 registry.json）里找到，
    且规则依据的字段也必须是声明过的状态字段；actor_roles ⊆ profile.roles；迁移表非空且无自迁移；reversible 的动作要有 inverse_action 且存在。"""
    issues, warnings = [], []
    profile = profile or {}
    state_fields = profile.get("state_fields") or {}
    classes = set(profile.get("entity_classes") or []) | set(state_fields)
    roles = set(profile.get("roles") or [])
    registry = {}
    if registry_path and os.path.isfile(registry_path):
        try:
            registry = {r["id"]: r for r in json.load(open(registry_path, encoding="utf-8"))}
        except Exception as e:
            issues.append(("registry", None, f"规则注册表解析失败: {e}"))
    else:
        issues.append(("registry", None, f"规则注册表不存在: {registry_path}（用 scaffold.export_registry 导出）"))
    files = sorted(glob_json(actions_dir))
    if not files:
        warnings.append((actions_dir, None, "没有任何 Action 定义文件"))
    ids = {}
    specs = {}
    for p in files:
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception as e:
            issues.append((p, None, f"JSON 解析失败: {e}")); continue
        aid = d.get("id")
        specs[aid] = d
        for k in ("id", "name", "entity_class", "entity_param", "state_field", "allowed_transitions", "actor_roles", "rules"):
            if k not in d:
                issues.append((p, aid, f"缺字段 {k}"))
        if aid in ids:
            issues.append((p, aid, f"id 与 {ids[aid]} 重复"))
        ids[aid] = p
        ec, sf = d.get("entity_class"), d.get("state_field")
        if ec not in classes:
            issues.append((p, aid, f"entity_class {ec!r} 不是本体里的 Class（profile.entity_classes / state_fields 的键）"))
        elif sf not in (state_fields.get(ec) or {}):
            issues.append((p, aid, f"state_field {sf!r} 未在 profile.state_fields[{ec!r}] 里声明"))
        for r in d.get("rules") or []:
            if r not in registry:
                issues.append((p, aid, f"规则 {r!r} 不在注册表里")); continue
            for ent_param, fld in registry[r].get("needs") or []:
                if ent_param == d.get("entity_param"):
                    if fld not in (state_fields.get(ec) or {}):
                        issues.append((p, aid, f"规则 {r} 依据的字段 {fld!r} 未在 state_fields[{ec!r}] 声明"))
                else:
                    warnings.append((p, aid, f"规则 {r} 依据的实体参数 {ent_param!r} 不是本动作的 entity_param，无法核对字段声明"))
            if registry[r].get("allow_snapshot"):
                issues.append((p, aid, f"规则 {r} allow_snapshot=true：G7 v1 不允许用快照事实"))
        if roles and not set(d.get("actor_roles") or []) <= roles:
            issues.append((p, aid, f"actor_roles {d.get('actor_roles')} 不在 profile.roles 内"))
        tr = d.get("allowed_transitions") or []
        if not tr:
            issues.append((p, aid, "allowed_transitions 为空"))
        for t in tr:
            if not (isinstance(t, list) and len(t) == 2):
                issues.append((p, aid, f"迁移项格式错: {t!r}"))
            elif t[0] == t[1]:
                issues.append((p, aid, f"自迁移 {t[0]!r}→{t[1]!r} 无意义"))
        if d.get("reversible") and not d.get("inverse_action"):
            issues.append((p, aid, "reversible=true 但没有 inverse_action"))
    for aid, d in specs.items():
        inv = d.get("inverse_action")
        if inv and inv not in specs:
            warnings.append((ids[aid], aid, f"inverse_action {inv!r} 不在本目录的 Action 定义里"))
        if not d.get("reversible"):
            warnings.append((ids[aid], aid, "不可逆动作：G7 出闸标准要求第一批动作全部可逆"))
    return {"files": len(files), "issues": issues, "warnings": warnings}


def glob_json(d):
    import glob as _g
    return _g.glob(os.path.join(d, "*.json")) if d and os.path.isdir(d) else []


def lint_context(context_dir, blocklist):
    """事件账本的来源名单检查：actor / evidence / value(字符串) 命中名单即违规。"""
    import glob as _g
    issues = []
    n = 0
    files = sorted(_g.glob(os.path.join(context_dir, "events-*.jsonl"))) if context_dir and os.path.isdir(context_dir) else []
    for p in files:
        for lineno, line in enumerate(open(p, encoding="utf-8"), 1):
            if not line.strip():
                continue
            n += 1
            try:
                ev = json.loads(line)
            except Exception as e:
                issues.append((f"{os.path.basename(p)}:{lineno}", None, f"JSON 解析失败: {e}")); continue
            text = " ".join([str(ev.get("actor") or ""), json.dumps(ev.get("evidence") or {}, ensure_ascii=False),
                             ev.get("value") if isinstance(ev.get("value"), str) else ""])
            for nm in blocklist:
                if nm in text:
                    issues.append((f"{os.path.basename(p)}:{lineno}", ev.get("event_id"), f"事件命中来源名单: {nm!r}"))
    return {"files": len(files), "events": n, "issues": issues}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge", "atoms.jsonl"))
    ap.add_argument("--profile", help="画像文件；默认取 atoms.jsonl 同目录的 profile.json")
    ap.add_argument("--sources-dir", help="第三方原始素材目录；给了就做'原文照搬'检查（≥--window 字连续重合即违规）")
    ap.add_argument("--window", type=int, default=24)
    ap.add_argument("--max-print", type=int, default=30)
    ap.add_argument("--concepts", nargs="?", const="auto", help="同时校验 concepts.jsonl（不给路径则取 atoms 同目录）")
    ap.add_argument("--warn", action="store_true", help="打印软规则警告清单")
    ap.add_argument("--actions", nargs="?", const="auto", help="G7：校验 Action 定义目录（默认 <工作区>/ontology/actions）")
    ap.add_argument("--registry", help="规则注册表 json（默认 <工作区>/ontology/rules/registry.json）")
    ap.add_argument("--context", nargs="?", const="auto", help="事件账本目录做来源名单检查（默认 <工作区>/ontology/context）")
    args = ap.parse_args()

    profile, profile_path = load_profile(args.file, args.profile)
    if profile is None:
        print("!" * 60, file=sys.stderr)
        print("警告：找不到 profile.json，来源名单检查未启用（防泄露闸门未生效！），topic 校验已退回内置默认枚举。", file=sys.stderr)
        print(f"查找过：{os.path.join(os.path.dirname(os.path.abspath(args.file)), 'profile.json')}", file=sys.stderr)
        print(f"      {os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(args.file))), 'ontology', 'profile.json')}", file=sys.stderr)
        print("如果这是客户工作区：多半是 atoms.jsonl 被复制/移到了别的目录，画像没跟着走——把它放回工作区，或显式传 --profile。", file=sys.stderr)
        print("!" * 60, file=sys.stderr)
    result = lint(args.file, profile, profile_path, args.sources_dir, args.window)
    ws = _workspace(args.file)
    actions_result = context_result = None
    if args.actions:
        adir = os.path.join(ws, "ontology", "actions") if args.actions == "auto" else args.actions
        reg = args.registry or os.path.join(ws, "ontology", "rules", "registry.json")
        actions_result = lint_actions(adir, profile, reg)
    if args.context:
        cdir = os.path.join(ws, "ontology", "context") if args.context == "auto" else args.context
        bl, _ = load_blocklist(profile, profile_path)
        context_result = lint_context(cdir, bl)
    concept_result = None
    if args.concepts:
        cpath = os.path.join(os.path.dirname(os.path.abspath(args.file)), "concepts.jsonl") if args.concepts == "auto" else args.concepts
        if os.path.isfile(cpath):
            concept_result = lint_concepts(cpath, args.file, profile)
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
    print(f"软规则警告: {len(result['warnings'])}（--warn 查看）")
    if args.warn:
        for lineno, aid, msg in result["warnings"][: args.max_print]:
            print(f"  行{lineno} [{aid}] {msg}")

    failed = bool(result["issues"])
    if concept_result:
        print(f"\nconcepts: {concept_result['total']} 个节点，违规 {len(concept_result['issues'])}，软警告 {len(concept_result['warnings'])}")
        for i, cid, msg in concept_result["issues"][: args.max_print]:
            print(f"  节点{i} [{cid}] {msg}")
        if args.warn:
            for i, cid, msg in concept_result["warnings"][: args.max_print]:
                print(f"  节点{i} [{cid}] {msg}")
        failed = failed or bool(concept_result["issues"])
    if actions_result:
        print(f"\nactions: {actions_result['files']} 个定义，违规 {len(actions_result['issues'])}，软警告 {len(actions_result['warnings'])}")
        for p, aid, msg in actions_result["issues"][: args.max_print]:
            print(f"  {os.path.basename(str(p))} [{aid}] {msg}")
        if args.warn:
            for p, aid, msg in actions_result["warnings"][: args.max_print]:
                print(f"  {os.path.basename(str(p))} [{aid}] {msg}")
        failed = failed or bool(actions_result["issues"])
    if context_result:
        print(f"\ncontext: {context_result['files']} 个分片 {context_result['events']} 条事件，命中来源名单 {len(context_result['issues'])}")
        for loc, eid, msg in context_result["issues"][: args.max_print]:
            print(f"  {loc} [{eid}] {msg}")
        failed = failed or bool(context_result["issues"])

    sys.exit(1 if failed else 0)
