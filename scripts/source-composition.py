#!/usr/bin/env python3
"""原子库来源构成——两种量法一起算，谁都能跑（零依赖）。

  库存构成：knowledge/atoms.jsonl 按 source_type 数条数（评论区用 AI 扒出来的就是这个）
  答案构成：用户真正拿到的——概念节点的证据来源、典型问题的检索结果来源

两个数字都对，回答的不是同一个问题。库存说"我们读过多少东西"，答案说"我们给你的判断是谁的"。
用法：python3 scripts/source-composition.py [--queries 文件，一行一个问题] [--json]
"""
import json, os, sys, argparse, subprocess, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWN = {"user_import", "account_video", "course", "case_study"}          # 小爷自己的实战、课程、脱敏实操
ADAPTED = {"adapted_consulting", "adapted_book", "adapted_course", "adapted_other",      # 外部方法论，重写后入库（无原文）
           "third_party_ip", "book_distilled", "external_adapted", "offline_course_ppt"}   # 2026-09-19 前的旧名，兼容历史数据
LABEL = {"own": "自家实战/课程", "adapted": "外部方法论改写", "other": "对标账号/平台规则"}
DEFAULT_QUERIES = ["一转 定价", "朋友圈 配比", "客户 不回消息", "复购 激活", "起号 冷启动", "导流 封号", "分佣 合规", "团队 提成",
                   "选品 供应链", "直播 憋单", "标题 小红书", "开头 三秒", "人设 定位", "私域 本质", "新人 第一步", "投流 千川",
                   "客户 标签", "社群 运营", "低价课 引流", "信任 时间"]
SKILLS = ["xy-close", "xy-private-ops", "xy-traffic", "xy-coach"]


def cls(t):
    return "own" if t in OWN else ("adapted" if t in ADAPTED else "other")


def pct(counter):
    n = sum(counter.values()) or 1
    return {LABEL[k]: f"{counter.get(k, 0)} ({counter.get(k, 0) / n:.0%})" for k in ("own", "adapted", "other")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    atoms = {}
    with open(os.path.join(ROOT, "knowledge", "atoms.jsonl"), encoding="utf-8") as f:
        for l in f:
            if l.strip():
                d = json.loads(l); atoms[d["id"]] = d
    # 1. 库存
    stock = collections.Counter(cls(d.get("source_type")) for d in atoms.values())
    by_type = collections.Counter(d.get("source_type") for d in atoms.values())
    # 2. 背景层 vs 核心层
    bg = [d for d in atoms.values() if (d.get("topics") or []) == ["通用商业管理"]]
    core = [d for d in atoms.values() if "通用商业管理" not in (d.get("topics") or [])]
    core_c = collections.Counter(cls(d.get("source_type")) for d in core)
    # 3. 概念节点证据
    ev = collections.Counter()
    cpath = os.path.join(ROOT, "knowledge", "concepts.jsonl")
    n_nodes = 0
    if os.path.isfile(cpath):
        with open(cpath, encoding="utf-8") as f:
            for l in f:
                if l.strip():
                    c = json.loads(l); n_nodes += 1
                    ev.update(cls(atoms[e].get("source_type")) for e in c.get("evidence_atom_ids", []) if e in atoms)
    # 4. 检索结果
    queries = [q.strip() for q in open(a.queries, encoding="utf-8")] if a.queries else DEFAULT_QUERIES
    hits = collections.Counter()
    env = dict(os.environ, XY_ATOMS=os.path.join(ROOT, "knowledge", "atoms.jsonl"))
    for q in queries:
        for sk in SKILLS:
            out = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "atoms-search.py"), q, "--skill", sk, "-k", "5", "--json"],
                                 capture_output=True, text=True, env=env).stdout
            try:
                hits.update(cls(atoms.get(o["id"], {}).get("source_type")) for o in json.loads(out))
            except Exception:
                pass
    result = {
        "库存构成（按条数）": {"总条数": len(atoms), **pct(stock), "细分": dict(by_type.most_common())},
        "分层": {"背景层（只挂'通用商业管理'）": len(bg), "核心库": len(core), "核心库构成": pct(core_c)},
        "概念节点证据构成": {"节点数": n_nodes, **pct(ev)},
        "检索结果构成": {"问题数": len(queries), "skill": SKILLS, "每题取前5": True, **pct(hits)},
    }
    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=1)); return
    print("原子库来源构成 —— 两种量法\n")
    print(f"库存（{len(atoms)} 条按 source_type 数）：", pct(stock))
    print(f"  其中背景层（只挂'通用商业管理'）{len(bg)} 条；核心库 {len(core)} 条 →", pct(core_c))
    print(f"概念节点证据（{n_nodes} 个节点）：", pct(ev))
    print(f"检索结果（{len(queries)} 个典型问题 × {len(SKILLS)} 个 skill，各取前 5）：", pct(hits))
    print("\n两个数字都对：库存说的是读过多少东西，检索结果说的是给你的判断是谁的。")


if __name__ == "__main__":
    main()
