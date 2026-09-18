# G6 迭代机制：AI Native 自迭代怎么落地（已实做）

> 对应架构提案第 3 节。这份是实做说明，不重复论证。脚本在 `enterprise-engine/scripts/`：`ledger.py`、`consolidate.py`、`apply.py`，零依赖，全部离线。

## 一句话

**提案自动生成，采纳由人决定，人的决定变成判例。** 系统不自己改本体；它把客户真实使用里长出来的信号变成闸门包，人拍板后脚本落盘，拍板本身回写成下一轮提案的依据。

## 三个脚本各管一段

```
客户用本体回答问题 ──► ledger.py log ──► knowledge/usage_ledger.jsonl
                                              │
                         （≥50 条新原子 或 ≥7 天，先到为准）
                                              ▼
                                    consolidate.py ──► ontology/gates/G6-<ts>.md（闸门包）
                                                    └► ontology/gates/G6-<ts>-proposals.jsonl
                                              │
                                  人在闸门包 §6 写决定 → decisions.jsonl
                                              ▼
                                       apply.py ──► concepts.jsonl（version+1）
                                                 ├► knowledge/concepts_revisions.jsonl（每次改动一条，ledger_ref 指回提案）
                                                 └► ontology/rules/precedents.jsonl（采纳与驳回都记）
```

### ledger.py —— 三种信号

| kind | 谁写 | 记什么 | 变成什么提案 |
|---|---|---|---|
| `implicit` | 检索路径（每次 `atoms-search --via-concepts` 后记一行） | query、命中的节点/原子；**无命中也记** | 覆盖缺口、共现节点对 |
| `explicit` | 用户标 `ok / wrong / missing`，可附新案例文本 | 标记 + 节点 + 备注 | 证据追加、摘要失真、新案例 |
| `conflict` | 入库时发现新原子与节点既有证据方向相反 | 新原子、节点、对立原子 | G3 矛盾候选 |

### consolidate.py —— 只产提案，绝不在请求路径上跑

| 提案类型 | 触发条件 | 默认 | 自动白名单 |
|---|---|---|---|
| `evidence_add` | ok 标记引用的原子不在该节点证据里 | 应用 | **是**（apply 时再复核"同向"） |
| `coverage_gap` | 同一关键词的无命中 query ≥ 3 次 | 不做 | 否 |
| `co_retrieval` | 两节点同时命中 ≥ 3 次且无关系 | 不做（G4：宁可留重复） | 否 |
| `summary_stale` | 同一节点被标 wrong ≥ 2 次 | 不做 | 否 |
| `contradiction` | conflict 记录 | 不做（G3 三步人工） | 否 |
| `new_case` | missing + 文本 | 走 G1 抽取 | 否 |

阈值（50 条 / 7 天 / 3 次 / 2 次）全是拍的，第一个客户跑三个月后按 ledger 实测定。

### apply.py —— 落盘、留痕、回写判例

- 白名单自动应用前再做一次**同向复核**：原子的 `related` 里若有指向节点既有证据的 `contradicts`，降级人闸。这一条来自两天里"自动推断 contradicts 误判"的教训。
- 合并（`merge`）永远不由脚本执行；`contradicts` 落在 atoms 的 `related`，按 `rules/contradicts.md` 三步人工标。
- 每次改动写 `concepts_revisions.jsonl`：`edit_source` 用 schema 里既有的三值（pipeline / llm_judge / human），加 `ledger_ref`。
- **驳回也记判例**。判例的价值一半在"为什么不"。

## 飞轮在哪

判例（`precedents.jsonl`）是运行环境的模型下一次生成/评估提案时要读的东西。同类情况见过三次人的决定，第四次的提案就更准，人要看的就更少。**驱动力是客户自己的使用和拍板，XY 不需要出现**。审核档客户的闸门包经过 XY，XY 只带走判例形态，不带走数据——这条要写进合同。

## 自测记录（2026-09-18，scratch 工作区）

用私域运营 4 个节点 + 11 条台账跑通：
- 第一次 consolidate 产出 4 类提案（evidence_add / co_retrieval / summary_stale / contradiction）；`coverage_gap` 没出来——关键词切分漏了四字词（"会员积分"切不出"积分"），改成与 atoms-search 同一套切法后从 3 条"积分"query 聚出 1 条。`new_case` 未在自测里触发（没记带文本的 missing）。
- `apply --auto --dry-run` 只放行 `evidence_add`；contradiction 无决定则不动
- 人决定 2 条（accept co_retrieval→refines、reject summary_stale）后：concepts 版本号 +1、revisions 2 条、precedents 3 条（含 1 条驳回）
- 再跑 consolidate：报"未到触发点"

## 没做的（如实）

- `atoms-search.py --via-concepts` 命中后自动写 `implicit` 台账：还没接。企业版检索脚本加一行调用即可，但 XY 自用版的 31 份副本不动（它们默认打云端）。
- 合并器里没有任何 LLM 调用；"模型建议"一栏留给运行环境的模型在闸门包里填。这是有意的，跟整套架构一致。
- 季度全量重跑（阶段 2/4/5 重放）没写脚本，因为阶段 2/4/5 本身就还是"模型在会话里跑"，不是脚本。
