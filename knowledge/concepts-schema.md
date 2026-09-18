# XY 概念节点层 Schema（concepts.jsonl）v0

设计参考：Tencent/WeKnora（MIT License，https://github.com/Tencent/WeKnora）的wiki_pages数据模型与生成流水线。
不是代码移植（技术栈不对等：它是Go+Postgres+多LLM厂商+向量库，我们是zero-dependency纯Python脚本），
是直接照搬它的具体字段设计/算法阈值/流水线步骤顺序，翻译成我们自己的JSONL实现。MIT协议明确允许此类复用。

## 为什么需要这一层

`atoms.jsonl`27853条原子直接两两建relation是C(27853,2)≈3.9亿组合，不可能也不该做。之前只有5739条边、
大部分原子孤立，问题不是"没做完"，是原子粒度太细，不该原子对原子连。

解法：加一层中间聚合节点。原子只挂到节点上当证据，节点与节点之间才建立关系图。
关系数量从"原子×原子"降到"原子×节点 + 节点×节点"，可控。

## concepts.jsonl 字段（直接对应WeKnora wiki_pages表字段）

| 字段 | 对应WeKnora字段 | 说明 |
|---|---|---|
| `id` | `slug` | 节点唯一id，格式`CPT-<topic缩写>-<序号>`，如`CPT-SY-001`（私域运营） |
| `title` | `slug`（人类可读部分） | 节点标题，要具体可操作，不要口号化 |
| `aliases` | `aliases` | 同一概念的别名/近义表达，供去重判断用 |
| `summary` | 页面正文 | 一段话说清这个概念是什么，从证据原子归纳，不超过200字 |
| `evidence_atom_ids` | `source_refs`/`chunk_refs` | 支撑这个节点的原子id列表，这是节点与原子之间的边 |
| `related_concepts` | `in_links`/`out_links` | 节点与节点之间的边，结构复用atoms.jsonl已有的`related`格式：`[{"id":..., "rel":...}]`，5种rel枚举不变（我们这块已经比WeKnora的无类型链接更细，不需要改） |
| `category` | `parent_slug`+目录层级 | 归属的topic（13个固定值之一），以及可选的`possible_parent`（疑似更大概念节点的id，留给人工/后续确认，不强制建父子关系） |
| `version` | `version` | 从1开始，每次summary或evidence_atom_ids变更+1 |
| `source_type` | — | 固定`derived`，标注这是从原子聚合推导出的节点，不是原始素材 |

## concepts_revisions.jsonl（新增，对应WeKnora wiki_page_revisions表）

我们现有`atoms.jsonl`完全没有版本历史概念，这是读WeKnora схема时发现的真实缺口，先在concepts层补上（范围小，验证价值后再考虑要不要给atoms也加）。

每次concepts.jsonl里某条记录的`summary`或`evidence_atom_ids`发生变化，写入一条不可变快照：

```json
{"concept_id": "CPT-SY-001", "version": 2, "timestamp": "2026-09-17T...", "edit_source": "pipeline|llm_judge|human", "prev_summary": "...", "prev_evidence_atom_ids": [...], "reason": "一句话说明这次改动原因"}
```

`edit_source`三个值直接对应WeKnora的`edit_source`字段用途：`pipeline`=候选提取阶段自动生成，`llm_judge`=去重/矛盾判断阶段的LLM修订，`human`=人工复核修改。

## 生成流水线（6阶段，直接对应WeKnora prompts_wiki.go的6个prompt，1:1翻译成脚本）

| 阶段 | 对应WeKnora prompt | 脚本（待写） | 输入 | 输出 |
|---|---|---|---|---|
| 0 | `WikiCandidateSlugPrompt` | `scripts/concepts-stage0-candidates.py` | 某topic下全部`type=principle/definition`的原子（轻量，只看抽象判断类，不看case/method） | 候选节点名单，只有`candidate_title`+`summary`+粗略`likely_evidence_atom_ids`，不做精细核验 |
| 1 | `WikiChunkCitationPrompt` | `scripts/concepts-stage1-evidence.py` | 候选名单 × 该topic全部原子（分批跑，按topic分片，不一次性塞全部27853条） | 精判后的`evidence_atom_ids`，逐条原子判断"是否实质性支撑这个候选节点" |
| 2 | `WikiDeduplicationPrompt` | `scripts/concepts-stage2-dedup.py` | 候选节点两两相似对（见下方两级漏斗） | 去重后的节点集，原则"related≠same，宁可留重复不错合并" |
| 3 | `WikiTaxonomyPlanPrompt` | `scripts/concepts-stage3-taxonomy.py` | 一批新节点 | 批量分配`category`，复用已有13个topics，不新造 |
| 4 | `WikiPageModifySystemPrompt` | `scripts/concepts-stage4-summary.py` | 节点+其evidence原子 | 写/更新`summary`；新证据与已有summary明确矛盾→更新+写revision记录原因；模糊→不覆盖，只在revision里追加说明 |
| 5 | `WikiIndexIntroPrompt` | `scripts/concepts-stage5-index.py` | 全部节点 | 维护顶层`concepts-index.md`，增量更新不是每次重写 |

## 规模控制：两级漏斗（对应WeKnora `internal/application/service/memory/consolidate.go`的记忆合并算法，本次读源码挖到的最有价值的一条）

避免"27853条原子两两判断"变成天文数字LLM调用的关键：

- **第一级，纯算法零LLM调用**：用现成的`atoms-search.py`关键词/IDF打分机制，算原子与候选节点、候选节点与候选节点之间的表面重合度，只留分数够高的候选对。起始阈值直接照搬WeKnora给的两个具体数字作为起点（后续按实测效果调）：
  - 词汇Jaccard重合度 ≥ 0.55 → 候选对
  - 若已有向量/embedding可用，余弦相似度 ≥ 0.86 → 候选对（我们目前没有embedding基础设施，先只用Jaccard，这条先记录，不立即实现）
- **第二级，只有过了第一级筛选的候选对，才花一次LLM调用**去真正判断"是否该合并/是否是有效证据/是否矛盾"
- **全程离线批跑**，不在检索请求路径上跑（这点直接照搬，WeKnora代码注释明确写"never runs on the request path"），每次处理一小批，看效果再继续，不追求一次性跑完

## contradicts关系判断（延续9-17早些时候已确认的"入库时判断"结论，现在有节点层后更好落地）

范围从"全库27853条"缩小到"该节点下的几十条证据原子"：`xy-atomize`写入新原子时，先用第一级词汇重合度筛出"跟哪个概念节点相关"，再问LLM"这条跟节点下已有证据矛盾吗"——判断成本从全库降到节点内，可行性大幅提升。

## 检索层改造（对应WeKnora `internal/handler/wiki_page.go` GetGraph + `ComputeGraphSubset`，ego-network+截断）

`atoms-search.py --expand-related`升级成两层：先命中概念节点，再展开节点下`evidence_atom_ids`+`related_concepts`，depth 1-2，设总节点数上限（如50）防止一展开就是几百条——直接照搬它"以某节点为中心做depth 1-2 ego-network展开+按链接数截断"的具体做法。

## 实施顺序（不是一次性处理27853条）

试点topic：**私域运营**（3616条原子，其中principle/definition类507+97=604条，量适中且用户熟悉）。
跑通阶段0-4全流程，人工验收效果，再决定要不要推广到其余12个topics。当前进度：阶段0（候选节点提取）执行中。

## 迁移状态

- [x] 阶段0：私域运营topic候选节点提取——完成，23个候选（`knowledge/_internal/concepts-staging/siyu-stage0-candidates.jsonl`）
- [x] 阶段1：精判证据——完成，全部3616条原子分5批并行精判，273次匹配（含重复计数288，一条原子可挂多个节点），23个候选全部收到至少1条证据，已合并写入`knowledge/concepts.jsonl`（正式产物，v1）
- [ ] 阶段2：去重——概念节点标题目前彼此区分度较高，暂不需要大规模去重，但"拓锁留升四字诀"已标注`possible_parent`指向"私域五大板块/2+5运营框架"，待人工确认层级
- [ ] 阶段3-5（分类/写摘要/建索引）——待续
- [ ] 两级漏斗的Jaccard脚本化——待写，复用`atoms-search.py`现有IDF机制改造
- [ ] `concepts_revisions.jsonl`——待建立（v1版本尚未发生过修订，暂不需要）
- [ ] `ontology-lint.py`要不要扩展校验concepts.jsonl——待概念层稳定后评估

### 阶段1真实发现（重要，影响后续规模化）

1. **私域运营topic数据质量问题被量化坐实**：3616条里约44%（batch2/3/4大部分+batch1约30%）是通用商业管理/行为经济学内容（德鲁克管理学蒸馏、医疗/零售/供应链咨询案例等），只是被机械地缀了一句"在私域运营中……"就打上私域运营标签，跟23个候选节点全部零匹配，不属于私域方法论本身。**这不是筛选过严，是原始topic标注质量的结构性问题**，会持续污染试点效果，需要用户决定处理方式（重新归类到独立topic / 保留但标记为低相关 / 暂不处理），再推广到其余12个topics前必须先有结论，否则规模化后会浪费大量精判成本在无效内容上。
2. **发现原23候选之外的新独立知识簇**："微信账号安全运营手册"（老号收购/分时段加人/话术规避风控，约15条原子，`XY-KB-021`~`039`附近），密度不低，建议补为第24个候选节点。
3. **顺带挖出2处真实`contradicts`候选**（`xy-atomize`入库时判断机制的第一批真实测试素材）：
   - `IPP-031`（一转门槛不能定太高，建议100元以内）vs `XY-DY-053`（化妆品一转直接定880元用于过滤客户）
   - `XY-DY-190`（"9.9元课卖越多IP越不值钱"）vs 主流低门槛一转设计原则
