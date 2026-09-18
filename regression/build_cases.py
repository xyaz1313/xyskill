#!/usr/bin/env python3
"""从仓库里已核实过的真实判断生成回归用例（零依赖，可重跑，结果确定）。

数据来源（全部是已经发生过、有记录的判断，不是新造的标注）：
- 证据链接：concepts.jsonl 私域运营 24 个节点的 evidence_atom_ids（HANDOFF-1 阶段1 精判结果）
- 话题改标：commit 83c8508 之前的 atoms.jsonl 与当前版本的 topics 差异（63.3% 批次规则的落地结果）
- 矛盾判定：concepts-schema.md "真实案例"章节记录的 2 组 contradicts + 2 组被否掉的配对
- 去重/层级：阶段2 的 refines 决定 + 跨 topic 的 7 处 refines
- 命名撞车 / 聚合遗漏：一次真实代码库六步法实操的判断，已匿名化，见 cases/name_collision.jsonl 头部说明

用法：python3 regression/build_cases.py [--base-commit 83c8508]
输出：regression/cases/*.jsonl（覆盖写）
"""
import json, os, random, subprocess, argparse
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KN = os.path.join(ROOT, "knowledge")
OUT = os.path.join(ROOT, "regression", "cases")
TOPIC = "私域运营"
PREFIXES = ("XY-CE-", "XY-CS-", "XY-CF-", "XY-BK3-")


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def git_show_jsonl(commit, relpath):
    out = subprocess.run(["git", "-C", ROOT, "show", f"{commit}:{relpath}"], capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"git show 失败: {out.stderr.strip()}")
    return [json.loads(l) for l in out.stdout.splitlines() if l.strip()]


def write(name, rows):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{name}: {len(rows)}")


def clip(s, n=260):
    return s if len(s) <= n else s[:n] + "…"


def build_evidence(atoms, concepts, rng):
    sy = [c for c in concepts if c["id"].startswith("CPT-SY-")]
    by_id = {a["id"]: a for a in atoms}
    in_node = {c["id"]: set(c["evidence_atom_ids"]) for c in sy}
    any_evidence = set().union(*in_node.values())
    rows = []
    # 正例：每个节点按证据数比例抽，至少 1 条，共约 40
    for c in sy:
        ev = [e for e in c["evidence_atom_ids"] if e in by_id]
        k = max(1, round(len(ev) / 273 * 40))
        for aid in rng.sample(ev, min(k, len(ev))):
            a = by_id[aid]
            rows.append({
                "id": f"EV-{len(rows)+1:04d}", "kind": "evidence_link", "strength": "strong",
                "input": {"concept_id": c["id"], "concept_title": c["title"], "concept_summary": c["summary"],
                          "atom_id": aid, "atom_type": a.get("type"), "atom_text": clip(a["knowledge"])},
                "expected": {"label": "supports"},
                "source": "HANDOFF-1 阶段1 精判，concepts.jsonl evidence_atom_ids",
                "repo_check": {"type": "in_evidence", "concept_id": c["id"], "atom_id": aid},
            })
    # 负例（弱标签）：是真私域内容（在别的节点当证据），但不在目标节点证据里
    n_pos = len(rows)
    pool = sorted(any_evidence)
    tries = 0
    while len(rows) < n_pos * 2 and tries < 5000:
        tries += 1
        c = rng.choice(sy)
        aid = rng.choice(pool)
        if aid in in_node[c["id"]] or aid not in by_id:
            continue
        a = by_id[aid]
        rows.append({
            "id": f"EV-{len(rows)+1:04d}", "kind": "evidence_link", "strength": "weak",
            "input": {"concept_id": c["id"], "concept_title": c["title"], "concept_summary": c["summary"],
                      "atom_id": aid, "atom_type": a.get("type"), "atom_text": clip(a["knowledge"])},
            "expected": {"label": "not_evidence"},
            "source": "阶段1 精判未将其列入该节点证据；弱标签：精判做的是'列入'判断，不是'排除'判断",
            "repo_check": {"type": "not_in_evidence", "concept_id": c["id"], "atom_id": aid},
        })
    return rows


def build_topic(atoms_old, atoms_new, concepts, rng):
    old = {a["id"]: a for a in atoms_old}
    new = {a["id"]: a for a in atoms_new}
    removed, kept_prefix = [], []
    for aid, a in old.items():
        if TOPIC not in (a.get("topics") or []) or aid not in new:
            continue
        now_has = TOPIC in (new[aid].get("topics") or [])
        if aid.startswith(PREFIXES):
            (kept_prefix if now_has else removed).append(aid)
    sy_evidence = set()
    for c in concepts:
        if c["id"].startswith("CPT-SY-"):
            sy_evidence.update(c["evidence_atom_ids"])
    kept_real = [aid for aid in sy_evidence if aid in new and TOPIC in (new[aid].get("topics") or []) and not aid.startswith(PREFIXES)]

    rows = []
    def add(aid, label, strength, why):
        a = old[aid]
        rows.append({
            "id": f"TP-{len(rows)+1:04d}", "kind": "topic_reclass", "strength": strength,
            "input": {"atom_id": aid, "atom_type": a.get("type"), "source_type": a.get("source_type"),
                      "original_topics": a.get("topics"), "atom_text": clip(a["knowledge"]),
                      "question": f"这条原子是否应保留 '{TOPIC}' 标签"},
            "expected": {"label": label},
            "source": why,
            "repo_check": {"type": "topic_present" if label == "keep" else "topic_absent", "atom_id": aid, "topic": TOPIC},
        })
    # 按前缀分层抽 24 条 remove
    by_pre = defaultdict(list)
    for aid in removed:
        by_pre[next(p for p in PREFIXES if aid.startswith(p))].append(aid)
    for p in PREFIXES:
        for aid in rng.sample(sorted(by_pre[p]), min(6, len(by_pre[p]))):
            add(aid, "remove", "strong", "HANDOFF-1 任务1：判定为通用商业管理内容机械缀话题词，已改标")
    for aid in sorted(kept_prefix):
        add(aid, "keep", "strong", "HANDOFF-1 任务1：同前缀批次里被逐条核实保留的真私域内容（最难的负例）")
    for aid in rng.sample(sorted(kept_real), 12):
        add(aid, "keep", "strong", "非清理批次、且是私域概念节点的证据原子")
    return rows


def build_contradicts(atoms):
    by = {a["id"]: a for a in atoms}
    def pair(a, b, label, strength, why, check=None):
        return {"id": None, "kind": "contradicts", "strength": strength,
                "input": {"a": {"id": a, "text": clip(by[a]["knowledge"])}, "b": {"id": b, "text": clip(by[b]["knowledge"])},
                          "question": "两条是否构成同一决策维度上的直接对立"},
                "expected": {"label": label}, "source": why, "repo_check": check}
    rows = [
        pair("IPP-031", "XY-DY-053", "contradicts", "strong", "concepts-schema.md 真实案例1：同一决策维度（一转定价高低）方向相反，各自条件不同",
             {"type": "related_rel", "a": "IPP-031", "b": "XY-DY-053", "rel": "contradicts"}),
        pair("XY-DY-190", "XY-DY-089", "contradicts", "strong", "concepts-schema.md 真实案例2：同一场景（个人IP知识付费一转）精确反向建议",
             {"type": "related_rel", "a": "XY-DY-190", "b": "XY-DY-089", "rel": "contradicts"}),
        pair("XY-DY-190", "IPP-031", "different_scene", "strong", "案例2排查记录：品类与价格带都不同，勉强关联属于硬凑，未标注"),
        pair("XY-DY-190", "XY-DY-183", "same_direction", "strong", "案例2排查记录：高度同向重复（同样反对9.9元引流课），不构成矛盾"),
        pair("XY-MB-030", "XY-MB-296", "same_direction", "strong", "ontology-schema.md 迁移状态：抽查中发现的近似重复内容，分属不同 type 但观点一致"),
    ]
    for i, r in enumerate(rows, 1):
        r["id"] = f"CD-{i:04d}"
    return rows


def build_dedup(concepts):
    by = {c["id"]: c for c in concepts}
    def pair(a, b, label, strength, why, check=None):
        return {"id": None, "kind": "dedup", "strength": strength,
                "input": {"a": {"id": a, "title": by[a]["title"], "summary": by[a]["summary"]},
                          "b": {"id": b, "title": by[b]["title"], "summary": by[b]["summary"]},
                          "question": "两个概念节点应合并、A细化B（refines）、还是各自独立"},
                "expected": {"label": label}, "source": why, "repo_check": check}
    refines = [("CPT-SY-003", "CPT-SY-008"), ("CPT-SY-006", "CPT-SY-005"), ("CPT-SY-015", "CPT-SY-014"), ("CPT-SY-024", "CPT-SY-015"),
               ("CPT-COMP-013", "CPT-SY-015"), ("CPT-TEAM-001", "CPT-SY-001"), ("CPT-TEAM-002", "CPT-SY-008"),
               ("CPT-CLOSE-001", "CPT-SY-002"), ("CPT-CLOSE-002", "CPT-SY-004"), ("CPT-CONT-001", "CPT-SY-006")]
    rows = [pair(a, b, "refines", "strong", "阶段2/跨topic梳理：possible_parent 或重叠内容转为正式 refines，未合并",
                 {"type": "concept_rel", "a": a, "b": b, "rel": "refines"}) for a, b in refines]
    separate = [("CPT-SY-004", "CPT-SY-020"), ("CPT-SY-005", "CPT-SY-007"), ("CPT-SY-012", "CPT-SY-014"), ("CPT-SY-013", "CPT-SY-018"), ("CPT-SY-017", "CPT-SY-021")]
    rows += [pair(a, b, "keep_separate", "strong", "阶段2 逐对复核：标题有共同关键词但未建关系、未合并（related≠same）",
                  {"type": "concept_no_rel", "a": a, "b": b}) for a, b in separate]
    for i, r in enumerate(rows, 1):
        r["id"] = f"DD-{i:04d}"
    return rows


# 一次真实生产代码库（600+模块的交易系统）六步法实操里做过的判断，已匿名化：
# 不含公司名、类名、模块路径、任何数字或业务参数。角色描述保留到能做判断的最小粒度。
NAME_COLLISION = [
    ("判决", "判定层的三值枚举：丢弃 / 升级 / 紧急", "参数扫描里一次(事件×参数组)的评分结果记录", "distinct_concept", "同名三处，第三处是研究网格里单个格子的判决与依据；三者语义层级与用途都不同"),
    ("K线", "生产信号层：一根已收的K线，含开高低收量与时间桶边界", "回测撮合层：一个只含收盘时刻/收盘价/成交量的轻量元组", "layered_variant", "同一概念的详略两版，详略差异是分层刻意为之，不是命名混乱"),
    ("往返交易", "回测引擎：一笔完整往返，冗余保留决策价、触发原因等追溯字段", "研究回放：精简记录，只留计算收益需要的字段", "layered_variant", "生产/研究两版，研究版故意不带追溯字段"),
    ("决策", "一条事件走完判定→意图→风控全程的不可变完整记录", "一条外发消息的准入裁决：是否放行 + 理由", "distinct_concept", "同名但一个是顶层聚合对象、一个是局部裁决结果，正式本体里必须分开命名"),
    ("事件类型", "按语义分：并购/指引/回购/稀释/监管等，决定方向先验", "按来源通道分：新闻/申报/行情/信号，决定进入哪条判定通路", "distinct_concept", "两个不同的分类轴共用一个名字，是真歧义，本体里应是两个维度"),
    ("证据", "统计检验结果：谓词×时间窗的信号数、样本数等", "告警卡片上的验证状态 + 一句人读结论", "distinct_concept", "一个是数据记录，一个是展示状态；曾因状态枚举混淆导致'测过是负'被显示成'未测'"),
    ("闸裁决", "以合约张数计的放行量，为0即拦下", "以名义金额计的放行量，为0即拦下", "same_concept_variant", "同一概念、同一结构、不同计量单位，本体里是一个实体的两种取值单位"),
    ("源", "行情常驻进程：连接、缓存、只读查询", "RSS 源的静态定义：名称、层级、信任度", "distinct_concept", "同名不同物"),
    ("测试夹具", "多个测试文件各自定义的同名夹具类", "同上", "not_an_entity", "同名类里约一半是测试夹具复用名，六步法'抽实体'阶段应直接排除，不进入判断"),
]


def build_code_cases():
    rows = []
    for i, (name, a, b, label, why) in enumerate(NAME_COLLISION, 1):
        rows.append({"id": f"NC-{i:04d}", "kind": "name_collision", "strength": "strong",
                     "input": {"name": name, "a": a, "b": b,
                               "question": "同名的两处是同一概念的变体、刻意分层的详略两版、还是不同概念"},
                     "expected": {"label": label}, "source": "真实代码库六步法实操（匿名化）", "rationale": why})
    rows.append({"id": "AG-0001", "kind": "aggregate_gap", "strength": "strong",
                 "input": {"layers": ["规则粗判", "模型分流", "策略产出意图", "风控裁决", "下单执行", "决策日志"],
                           "hint": "有一个模块的说明写着'把各层串成一条线的那根线'，其中一个类名很普通（与另一模块的类撞名），记录一条事件走完全程的每一步中间产物",
                           "question": "候选实体清单里没有顶层聚合对象，该怎么判断"},
                 "expected": {"label": "aggregate_present_named_generically",
                              "notes": ["该模块本身就是顶层聚合，不是分散在多个模块里", "聚合覆盖判定→意图→风控，执行在聚合之外，不要把执行写进聚合",
                                        "第一轮漏掉的原因是类名普通且撞名，被当成普通记录类"]},
                 "source": "真实代码库六步法实操（匿名化）"})
    rows.append({"id": "AG-0002", "kind": "aggregate_gap", "strength": "strong",
                 "input": {"situation": "候选草稿依据的材料与核实用的代码快照不是同一时间点，期间系统新增了大量模块",
                           "question": "核实阶段怎么处理"},
                 "expected": {"label": "split_verifiable", "notes": ["先对齐版本；对不齐就把'能核实/不能核实'分开列，不能核实的明说这轮看不到"]},
                 "source": "真实代码库六步法实操（匿名化）"})
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-commit", default="83c8508", help="topics 改标之前的 atoms.jsonl 版本")
    ap.add_argument("--seed", type=int, default=20260918)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    atoms = load_jsonl(os.path.join(KN, "atoms.jsonl"))
    concepts = load_jsonl(os.path.join(KN, "concepts.jsonl"))
    atoms_old = git_show_jsonl(args.base_commit, "knowledge/atoms.jsonl")
    write("evidence_link.jsonl", build_evidence(atoms, concepts, rng))
    write("topic_reclass.jsonl", build_topic(atoms_old, atoms, concepts, rng))
    write("contradicts.jsonl", build_contradicts(atoms))
    write("dedup.jsonl", build_dedup(concepts))
    write("code_ontology.jsonl", build_code_cases())
