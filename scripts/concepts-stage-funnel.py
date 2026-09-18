#!/usr/bin/env python3
"""概念节点两级漏斗 - 第一级粗筛（零依赖，零LLM调用）。
用法：
  python3 concepts-stage-funnel.py --atoms <原子txt/jsonl> --candidates <候选jsonl> [--threshold 0.12] [--calibrate <已知正例jsonl>]

设计参考 WeKnora consolidate.go 的两级漏斗思路（第一级算法零成本粗筛，第二级候选对才送LLM判断），
但阈值不能直接照搬它的词级Jaccard 0.55——那是英文/分词语言的数字，中文没有天然词边界，
这里用字符2-gram Jaccard，量级完全不同，必须本地校准。

--calibrate 模式：拿私域运营试点已确认的273条真实匹配（atom_id, concept_title）当标注数据，
扫一遍不同阈值下的召回率（漏掉多少条真匹配）和压缩率（省掉多少条不用送LLM的原子），
帮助选一个"几乎不漏真匹配、但能甩掉大部分噪音"的阈值，不是拍脑袋定数字。
"""
import json, re, argparse, sys
from collections import defaultdict

def bigrams(text):
    text = re.sub(r"[^一-鿿0-9a-zA-Z]", "", text)
    if len(text) < 2:
        return {text} if text else set()
    return {text[i:i+2] for i in range(len(text)-1)}

def jaccard(a, b):
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0

def load_atoms_txt(path):
    """格式 [原子ID][type] 内容 —— 跟 stage0/stage1 fork 用的中转txt一致"""
    out = []
    pat = re.compile(r"^\[(.+?)\]\[(.+?)\]\s*(.*)$")
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line:
            continue
        m = pat.match(line)
        if m:
            out.append({"id": m.group(1), "type": m.group(2), "knowledge": m.group(3)})
    return out

def load_atoms_jsonl(path):
    out = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        out.append({"id": d["id"], "type": d.get("type", ""), "knowledge": d.get("knowledge", "")})
    return out

def load_candidates(path):
    out = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        title = d.get("candidate_title") or d.get("title")
        summary = d.get("summary", "")
        out.append({"title": title, "text": title + " " + summary})
    return out

def run_funnel(atoms, candidates, threshold):
    cand_bg = [(c["title"], bigrams(c["text"])) for c in candidates]
    pairs = []
    for atom in atoms:
        abg = bigrams(atom["knowledge"])
        for title, cbg in cand_bg:
            score = jaccard(abg, cbg)
            if score >= threshold:
                pairs.append((atom["id"], title, round(score, 4)))
    return pairs

def calibrate(atoms, candidates, known_positive_pairs):
    """known_positive_pairs: set of (atom_id, concept_title) confirmed真匹配"""
    cand_bg = {c["title"]: bigrams(c["text"]) for c in candidates}
    atom_bg = {a["id"]: bigrams(a["knowledge"]) for a in atoms}
    scores_pos = []
    scores_neg_sample = []
    for atom_id, title in known_positive_pairs:
        if atom_id in atom_bg and title in cand_bg:
            scores_pos.append(jaccard(atom_bg[atom_id], cand_bg[title]))
    # 负样本：随机抽样组合（非标注正例的 atom×candidate 对），控制量级避免 O(n*m) 太大
    import random
    random.seed(42)
    all_atom_ids = list(atom_bg.keys())
    all_titles = list(cand_bg.keys())
    neg_sample_n = min(5000, len(all_atom_ids) * len(all_titles))
    tried = 0
    while len(scores_neg_sample) < neg_sample_n and tried < neg_sample_n * 3:
        tried += 1
        aid = random.choice(all_atom_ids)
        t = random.choice(all_titles)
        if (aid, t) in known_positive_pairs:
            continue
        scores_neg_sample.append(jaccard(atom_bg[aid], cand_bg[t]))

    print(f"正例样本数: {len(scores_pos)}  负例采样数: {len(scores_neg_sample)}")
    print(f"{'阈值':>6} | {'召回率(正例≥阈值占比)':>20} | {'负例通过率(噪音占比)':>18}")
    for thr in [0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.15, 0.18, 0.22, 0.28, 0.35]:
        recall = sum(1 for s in scores_pos if s >= thr) / len(scores_pos) if scores_pos else 0
        neg_pass = sum(1 for s in scores_neg_sample if s >= thr) / len(scores_neg_sample) if scores_neg_sample else 0
        print(f"{thr:>6} | {recall:>19.1%} | {neg_pass:>17.1%}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--atoms", required=True, help="原子文件(.txt格式[id][type]内容 或 .jsonl)")
    ap.add_argument("--candidates", required=True, help="候选概念节点jsonl")
    ap.add_argument("--threshold", type=float, default=0.12)
    ap.add_argument("--calibrate", help="已知真实匹配jsonl，每行{\"atom_id\":..,\"concept_title\":..}，跑校准模式不输出候选对")
    a = ap.parse_args()

    atoms = load_atoms_jsonl(a.atoms) if a.atoms.endswith(".jsonl") else load_atoms_txt(a.atoms)
    candidates = load_candidates(a.candidates)
    print(f"原子数: {len(atoms)}  候选节点数: {len(candidates)}", file=sys.stderr)

    if a.calibrate:
        known = set()
        for line in open(a.calibrate, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            known.add((d["atom_id"], d["concept_title"]))
        calibrate(atoms, candidates, known)
    else:
        pairs = run_funnel(atoms, candidates, a.threshold)
        print(f"粗筛通过候选对: {len(pairs)} / {len(atoms)*len(candidates)} 全量组合（压缩比 {1-len(pairs)/(len(atoms)*len(candidates)):.1%}）", file=sys.stderr)
        for atom_id, title, score in pairs:
            print(json.dumps({"atom_id": atom_id, "concept_title": title, "jaccard": score}, ensure_ascii=False))
