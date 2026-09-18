#!/usr/bin/env python3
"""企业引擎版原子检索（零依赖，默认离线）。用法：
  atoms-search "关键词 关键词2" [--type case,anti-pattern] [--topic 某话题] [-k 5] [--json] [--expand-related] [--via-concepts]
  atoms-search "..." --remote https://host   # 只有显式给 --remote 才会联网，任何情况下都不会自动打外部地址

与 XY 自用版的差异：没有云端默认地址；没有按 XY skill 名做的场景降噪；来源加权从 profile.json 的
preferred_source_types 读（客户自己声明哪类来源更可信），而不是写死 XY 的来源名。
评分：knowledge 命中关键词 IDF 加权 + 首句加权 + 教学信号 + type/confidence/来源偏好。
"""
import json, os, sys, re, argparse


def _find_atoms_local():
    here = os.path.dirname(os.path.realpath(__file__))
    cands = [os.path.join(os.path.dirname(here), "knowledge", "atoms.jsonl"),
             os.path.join(os.getcwd(), "knowledge", "atoms.jsonl")]
    for c in cands:
        if os.path.isfile(c):
            return c
    return cands[0]


def _load_json_next_to(atoms_path, name):
    cand = os.path.join(os.path.dirname(atoms_path), name)
    if os.path.isfile(cand):
        try:
            return json.load(open(cand, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _load_concepts(atoms_path):
    cand = os.path.join(os.path.dirname(atoms_path), "concepts.jsonl")
    out = []
    if os.path.isfile(cand):
        for l in open(cand, encoding="utf-8"):
            l = l.strip()
            if l:
                out.append(json.loads(l))
    return out


def _remote_search(url, query, topic, top_k):
    import urllib.request
    payload = {"query": query, "top_k": top_k}
    if topic:
        payload["topics"] = [topic]
    req = urllib.request.Request(url.rstrip("/") + "/v1/atoms/search", data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read().decode("utf-8")).get("atoms", [])


ap = argparse.ArgumentParser()
ap.add_argument("query"); ap.add_argument("--type"); ap.add_argument("--topic"); ap.add_argument("-k", type=int, default=5)
ap.add_argument("--json", action="store_true"); ap.add_argument("--file", default=os.environ.get("ATOMS_FILE") or _find_atoms_local())
ap.add_argument("--expand-related", action="store_true"); ap.add_argument("--expand-limit", type=int, default=2)
ap.add_argument("--via-concepts", action="store_true"); ap.add_argument("--remote", help="显式指定远端检索地址；不给就永远本地")
a = ap.parse_args()

if a.remote:
    rows = _remote_search(a.remote, a.query, a.topic, a.k)
    if a.json:
        print(json.dumps(rows, ensure_ascii=False)); sys.exit(0)
    for o in rows:
        print(f"- [{o['id']}] ({o.get('confidence')}) {o['knowledge']}")
    if not rows:
        print("（原子库暂无匹配，请明说没有实证）")
    sys.exit(0)

_IDF = _load_json_next_to(a.file, "idf.json")
_PROFILE = _load_json_next_to(a.file, "profile.json") or _load_json_next_to(os.path.join(os.path.dirname(os.path.abspath(a.file)), "..", "ontology", "x"), "profile.json")
_PREFERRED = set(_PROFILE.get("preferred_source_types") or [])

kws = [w for w in re.split(r"[\s,，、/]+", a.query) if w]
_ext = []
for _w in kws:
    if len(_w) > 4:
        _ext += [_w[i:i + 2] for i in range(0, len(_w) - 1, 2)] + [_w[:3], _w[-3:]]
    elif len(_w) == 4:
        _ext += [_w[:2], _w[2:]]
kws = kws + [w for w in dict.fromkeys(_ext) if len(w) >= 2 and w not in kws]
types = set(a.type.split(",")) if a.type else None
rows = []
_by_id = {}
try:
    for l in open(a.file, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        try:
            o = json.loads(l)
        except Exception:
            continue
        if (a.expand_related or a.via_concepts) and o.get("id"):
            _by_id[o["id"]] = o
        if types and o.get("type") not in types:
            continue
        if a.topic and a.topic not in (o.get("topics") or []):
            continue
        k = o.get("knowledge", ""); og = o.get("original", "") or ""
        head = k[:30]
        s = 0.0
        for w in kws:
            c = k.count(w)
            if c == 0:
                if w in og:
                    s += 1
                continue
            _idf = _IDF.get(w)
            base = 0.3 if _idf is None else min(8.0, _idf) * 1.2
            if w in head:
                base += 2.0
            s += base * (1 + 0.4 * min(c - 1, 3))
            if c == 1 and k.rfind(w) > len(k) * 0.7 and w not in head:
                s -= 1.5
        if s <= 0:
            continue
        if re.search(r"\d+ ?[%点元条天倍]|阶梯|梯度|红线|上限|下限|三步|四步|五步|第一步|原则[:：]|标准[:：]|公式|先.{1,6}再|配比|占比", k):
            s += 4
        if re.search(r"怎么设|如何设|设计|判定|判断标准|自查|checklist|清单", k):
            s += 2
        if o.get("type") in ("case", "anti-pattern", "number", "method"):
            s += 2
        if o.get("confidence") == "high":
            s += 2
        if o.get("source_type") in _PREFERRED:
            s += 6
        rows.append((s, o))
except FileNotFoundError:
    print(f"[atoms-search] 找不到原子库：{a.file}", file=sys.stderr); sys.exit(0)
rows.sort(key=lambda x: -x[0]); rows = rows[:a.k]

matched_concept = None
if a.via_concepts:
    _best_score, _best = 0, None
    for c in _load_concepts(a.file):
        hit = sum(1 for w in kws if len(w) >= 2 and w in c.get("title", ""))
        if hit > _best_score:
            _best_score, _best = hit, c
    if _best_score > 0 and _best:
        matched_concept = _best
        shown = {o["id"] for _, o in rows}
        concept_rows = []
        for eid in _best.get("evidence_atom_ids", []):
            if eid in shown:
                continue
            tgt = _by_id.get(eid)
            if tgt:
                concept_rows.append((999.0, tgt)); shown.add(eid)
        rows = (concept_rows + rows)[:a.k]

_REL_PRIORITY = {"supports": 0, "contradicts": 0, "example_of": 1, "prerequisite_of": 2, "refines": 3}
expanded = {}
if a.expand_related and _by_id:
    shown = {o["id"] for _, o in rows}
    for _, o in rows:
        rels = [r for r in (o.get("related") or []) if isinstance(r, dict)]
        rels.sort(key=lambda r: _REL_PRIORITY.get(r.get("rel"), 9))
        picked = []
        for r in rels:
            tgt = _by_id.get(r.get("id"))
            if not tgt or r["id"] in shown:
                continue
            picked.append((r.get("rel"), tgt)); shown.add(r["id"])
            if len(picked) >= a.expand_limit:
                break
        if picked:
            expanded[o["id"]] = picked

if a.json:
    out = []
    for _, o in rows:
        row = dict(o)
        if o["id"] in expanded:
            row["related_expanded"] = [{"rel": rel, **tgt} for rel, tgt in expanded[o["id"]]]
        out.append(row)
    if matched_concept:
        print(json.dumps({"matched_concept": matched_concept.get("title"), "results": out}, ensure_ascii=False)); sys.exit(0)
    print(json.dumps(out, ensure_ascii=False)); sys.exit(0)
if matched_concept:
    print(f"【命中概念节点：{matched_concept.get('title')}】{matched_concept.get('summary', '')}")
for s, o in rows:
    print(f"- [{o['id']}] ({o.get('type')}/{o.get('confidence')}) {o['knowledge']}")
    for rel, tgt in expanded.get(o["id"], []):
        print(f"    ↳ [{rel}] {tgt['id']} ({tgt.get('type')}) {tgt['knowledge'][:60]}")
if not rows:
    print("（原子库暂无匹配，请明说没有实证）")
