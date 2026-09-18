# XY 概念节点层 Schema（concepts.jsonl）v0

设计参考：Tencent/WeKnora（MIT License，https://github.com/Tencent/WeKnora）的wiki_pages数据模型与生成流水线。
不是代码移植（技术栈不对等：它是Go+Postgres+多LLM厂商+向量库，我们是zero-dependency纯Python脚本），
是直接照搬它的具体字段设计/算法阈值/流水线步骤顺序，翻译成我们自己的JSONL实现。MIT协议明确允许此类复用。

## 证据归属规则（2026-09-18 收官审查后写成明文）

节点的 `evidence_atom_ids` **允许跨 topic**：一条原子只要实质性支撑该节点的判断就能当证据，不要求原子的 `topics` 字段包含节点的 `category`。私域运营试点与其余 12 个 topic 都是这么做的（截至收官审查有 13 条这类证据）。反过来不成立：不能因为原子挂在某 topic 下就默认它是该 topic 所有节点的证据。`ontology-lint.py --concepts` 只查证据是否存在，不查 topic 一致性，这是有意的。

## 索引怎么维护

`concepts-index.md` 由 `scripts/concepts-build-index.py` 从 `concepts.jsonl` 生成，**不手工编辑**；改完节点重跑一次，`--check` 可在提交前核对索引没过期。

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
| `summary` | 页面正文 | 一段话说清这个概念是什么，从证据原子归纳，≤200 字（`ontology-lint.py --concepts` 超 200 报软警告、超 450 报违规）。2026-09-18 收官审查曾有 182 个节点超长，已全部精修，原文在 `concepts_revisions.jsonl` |
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

### 真实校准结果（2026-09-18，`scripts/concepts-stage-funnel.py`）——纠正上面的设想

写了字符2-gram Jaccard的粗筛脚本，用私域运营试点已确认的273条真实匹配（atom_id↔concept_title）做标注数据校准，**结论是：纯文字相似度不能当"要不要送LLM判断"的过滤器**：
- 阈值放到能接住78%真匹配时，同时放进来10.7%的不相关内容；阈值稍微调高，召回率断崖式下跌（0.06阈值只能接住36.3%真匹配）
- 对"这条原子是不是该topic下的已知垃圾内容"（63.3%错标问题）过滤效果也差：阈值0.02时，已知垃圾内容（`XY-CE`/`XY-CS`/`XY-CF`前缀）里70.3%照样通过
- 原因：很多真实证据关系是"内容支撑同一个道理"而不是"用词相同"，字面相似度抓不住这种深层语义关联，中文又没有天然分词边界，2-gram字符级Jaccard比WeKnora原本的词级Jaccard噪声更大

漏斗唯一真正有用的地方：把"一条原子该测哪几个候选节点"这件事的组合数砍掉88.8%（不是决定"要不要测这条原子"，是决定"测的时候该比对谁"）。

**推广到其余12个topics的正确做法，改为**：先用今天已经验证有效的**规则级过滤**（原子id前缀/`source_type`/关键词模式，就是今天发现XY-CE/CS/CF/BK3前缀大量是错标内容用的同一套方法）筛掉大概率无关内容，剩下的原子再送LLM判断——不是指望一个通用算法漏斗自动解决语义匹配问题。两级漏斗的"第一级"应该理解成"规则粗筛"而不是"相似度算法"，这是本次校准后的修正，脚本本身保留（对"该比对谁"仍有用），但不再是唯一或主要的省成本手段。

## contradicts关系判断（延续9-17早些时候已确认的"入库时判断"结论，现在有节点层后更好落地）

范围从"全库27853条"缩小到"该节点下的几十条证据原子"：`xy-atomize`写入新原子时，先用第一级词汇重合度筛出"跟哪个概念节点相关"，再问LLM"这条跟节点下已有证据矛盾吗"——判断成本从全库降到节点内，可行性大幅提升。

### 真实案例（2026-09-18，第一次正式标注）

两组`contradicts`已在`atoms.jsonl`里落地（`related`字段互相加了对方，`rel: contradicts`）：

1. **`IPP-031` ↔ `XY-DY-053`**：`IPP-031`主张"产品类一转门槛不能定太高，建议100元以内，门槛越低成交率越高"；`XY-DY-053`是化妆品私域案例，一转直接定880元用来过滤客户。两条都是`high confidence`、来源不同（课程 vs 账号实战案例），构成同一决策维度（一转定价高低）上的直接对立，且都不是错误——`XY-DY-053`本身给出了不同的适用条件（SKU多、有常态化促销活动可以后续激活留下的低意向客户，880元筛选反而更划算）。这是"同一原则在不同业务条件下成立方向相反"的典型矛盾，不是谁对谁错，标注价值在于：任何应用场景要先判断自己的业务条件（是否SKU多/是否有常态化促销）落在哪一边，再决定跟哪条走。

2. **`XY-DY-190` ↔ `XY-DY-089`**：`XY-DY-190`（"9.9元的课卖得越多，你的IP就越不值钱"）主张个人独立运营的知识付费IP（没有成熟转化团队）应直接卖199/399/699元核心课，不要挂低价引流课；`XY-DY-089`明确把"知识付费/IP创作者"列为私域三类适用人群之一，建议路径是"用低价课（5-9.9元级别）导流到私域再卖高价陪跑/私董会/线下课"。两条针对同一场景（个人IP知识付费产品的一转设计）给出直接相反的建议，且都是`account_video`来源、`high confidence`。**排查过程记录**：一开始怀疑的对立面是`IPP-031`（100元以内低门槛一转原则），但`IPP-031`讨论的是"产品类"变现，价格带（100元）、载体（实物/服务）都跟`XY-DY-190`讨论的"知识付费课程"不是同一件事，勉强关联属于"硬凑"，故未采用；改为在全库搜索"引流课/9.9/低价课"相关原子后，找到`XY-DY-089`这条在同一场景（知识付费IP的一转设计）下给出精确反向建议的原子，才是真矛盾。另发现`XY-DY-183`跟`XY-DY-190`高度同向重复（同样反对9.9元引流课），不构成矛盾，未标注。

这两个案例也印证了"入库时判断"要设计成"先定位同场景/同决策维度的原子，再判断建议方向是否相反"，而不是看到关键词相近就标`contradicts`——很多表面相似的原子其实是`refines`（同方向补充细化）而非`contradicts`。

## 检索层改造（对应WeKnora `internal/handler/wiki_page.go` GetGraph + `ComputeGraphSubset`，ego-network+截断）

`atoms-search.py --expand-related`升级成两层：先命中概念节点，再展开节点下`evidence_atom_ids`+`related_concepts`，depth 1-2，设总节点数上限（如50）防止一展开就是几百条——直接照搬它"以某节点为中心做depth 1-2 ego-network展开+按链接数截断"的具体做法。

## 实施顺序（不是一次性处理27853条）

试点topic：**私域运营**（3616条原子，其中principle/definition类507+97=604条，量适中且用户熟悉）。
跑通阶段0-4全流程，人工验收效果，再决定要不要推广到其余12个topics。当前进度：阶段0（候选节点提取）执行中。

### 交接文档2：其余12个topic全部完成（2026-09-18）

按`docs/superpowers/specs/HANDOFF-2-remaining-topics-2026-09-18.md`要求，对私域运营之外的12个topic逐个跑完数据质量粗查+候选提取+精判证据+去重+分类+摘要+索引全流程，每完成一个topic立刻commit+push。最终`knowledge/concepts.jsonl`共**309个概念节点**（私域运营24个试点 + 其余12个topic合计285个）。各topic关键数字：

| topic | 原始原子数 | 四前缀占比 | 改标到通用商业管理 | principle/definition候选数 | 概念节点数 |
|---|---|---|---|---|---|
| 私域运营（试点） | 3616 | 63.3% | 2289 | 604 | 24 |
| 新人起步方法论 | 394 | 31.2%（仅XY-CS） | 123 | 76 | 20 |
| 选品逻辑 | 1658 | 70.1% | 1163 | 155 | 24 |
| 合规与风控 | 1043 | 47.3% | 493 | 196 | 24 |
| 团队与模式设计 | 7373 | 85.1% | 6277 | 327 | 29 |
| IP人设 | 1282 | 12.9% | 165 | 398 | 34 |
| 商业案例与实战复盘 | 8049 | 84.8% | 6829 | 289 | 26 |
| AI与工具 | 1894 | 21.3% | 404 | 379 | 23 |
| 认知与心态 | 6155 | 75.3% | 4634 | 588 | 30 |
| 成交与话术 | 1861 | 17.0% | 316 | 274 | 29 |
| 流量获取 | 2898 | 45.5% | 1319 | 410 | 28 |
| 内容创作与平台 | 1623 | 0%（无需清理） | 0 | 410 | 18 |
| 中国市场与下沉 | 8 | 0% | 0（评估后跳过完整流程） | — | 0 |
| 本体论与FDE方法论（2026-09-18 收官补跑） | 204 | —（官方/学术材料，无此问题） | 0 | 59 | 25 |
| **合计**¹ | **38058** | — | **23812**（含试点2289） | **4165** | **333**（收官审查合并 1 个重复节点后） |

¹ 原始原子数按topic逐行相加，一条原子若同时挂多个topic会被重复计入（如XY-UZB系列常见同时挂"团队与模式设计"+"AI与工具"），因此37854大于`atoms.jsonl`实际总量27853，不是去重后的唯一原子数。

方法论延续私域运营试点确认的规则：候选节点只看principle/definition类原子；精判证据阶段允许跨topic语义匹配不强制原子topics字段包含节点所属topic；去重原则"related≠same，宁可留重复不错合并"；`id`前缀延续`CPT-<topic缩写>-序号`格式（NEW/SEL/COMP/TEAM/IP/CASE/AIT/COG/CLOSE/TRAF/CONT）。全部12个topic完成后共标注**7处显式跨topic`related_concepts: refines`关系**，把新topic里发现的、与私域运营试点24个节点或彼此高度重叠的内容链接起来而非重复建节点或强行合并（如成交与话术topic的转化阶梯定价/信任分层节点分别`refines`私域运营topic的`CPT-SY-002`/`CPT-SY-004`）。

**特殊处理：中国市场与下沉topic**（仅8条原子，全部来自"FDE训练营第一期逐字稿"）——核实后发现全部8条都已双标签挂在更实质的topic上（商业案例与实战复盘×3、AI与工具×3、认知与心态×1、合规与风控×1），且内容是"在中国做AI咨询"的泛泛观察而非"下沉市场"的专门方法论，未发现数据质量问题（source_type均为真实的`user_import`）。判断这个topic量太小且语义边界模糊，不建立独立概念节点，topics字段维持原状不做改动，留待未来有更多下沉市场相关内容时再评估是否需要专门节点。

**重要方法论发现（超出原HANDOFF文档预期）**：数据质量粗查环节确认"XY-CE/XY-CS/XY-CF/XY-BK3四前缀=机械缀话题词的通用商业内容"规律在全部11个新处理topic中都成立（抽样30+条/topic独立验证，零例外），但同时发现**不能把"外部方法论·内化改写"这个`source_label`或`source_type in (external_adapted, book_distilled)`当成同一个规则的扩展**——过程中额外发现的`XY-BK2`（尼采/维特根斯坦/福柯哲学蒸馏）、`XY-MB`（执行力心理学蒸馏）、`XY-MSK`（马斯克/YC创业方法论蒸馏）、`XY-MA`（定位方法论/女装电商案例）、`XY-IPB`（教练IP/组织化转型）、`XY-IPD`（内容创作方法论）等批次虽然source_type同样是`external_adapted`/`book_distilled`，但抽样核实内容与所属topic高度吻合、非机械贴标，均**未做重新归类**。这印证了原HANDOFF文档的判断标准（"核心机制是否依赖企业级基础设施/组织架构，topic关键词是否只是句末强行安上的类比"）比"看source_type/source_label"更可靠，规则必须逐批次抽样验证，不能泛化套用。

**未尽事项（留给后续）**：
- `concepts_revisions.jsonl`仍未建立（v1版本节点尚未发生修订）
- 云端`api.xyskill.xyz`接口的`--via-concepts`同步问题（`scripts/atoms-search.py`目前只在本地文件模式生效）——本次会话无权限接触云端代码，现状如实记录，留给有权限的后续会话处理
- 约100+条疑似近似重复原子的全库扫描（如`XY-MB-030`/`XY-MB-296`类型）——过程中未系统性排查，仅记录了已知的历史遗留案例，如`ontology-schema.md`"迁移状态"所述
- 309个概念节点之间的跨topic`related_concepts`目前只标注了少量最明显的重叠（如7处refines），大量内容相近但归属不同topic的节点（例如团队与模式设计的FDE知识库节点、商业案例的中小企业AI落地节点、AI与工具的企业级技术选型节点，三者视角互补但界限有一定模糊性）尚未系统梳理，留给未来做一轮"节点间去重/关联"专项

## 迁移状态

- [x] 阶段0：私域运营topic候选节点提取——完成，23个候选（`knowledge/_internal/concepts-staging/siyu-stage0-candidates.jsonl`）
- [x] 阶段1：精判证据——完成，全部3616条原子分5批并行精判，273次匹配（含重复计数288，一条原子可挂多个节点），23个候选全部收到至少1条证据，已合并写入`knowledge/concepts.jsonl`（正式产物，v1）
- [x] 阶段2：去重（2026-09-18完成）——逐对复核23-24个候选标题，未发现需要合并的重复节点；3处`possible_parent_note`全部转成正式`related_concepts: refines`关系（拓锁留升四字诀→私域五大板块框架、朋友圈内容分类与配比体系→朋友圈内容五问框架、导流平台风控红线清单→只吸引不骚扰导流原则），不强行合并成同一节点
- [x] 阶段3：分类（2026-09-18完成）——全部24个节点`category`维持"私域运营"，未推广到其余12个topics前细分意义不大
- [x] 阶段4：写摘要（2026-09-18完成）——核对23个既有节点的`evidence_atom_ids`未受任务1（私域运营topic清理2289条改归"通用商业管理"）影响，摘要保持不变；新增`CPT-SY-024`（微信账号安全运营手册）撰写全新摘要
- [x] 阶段5：建索引（2026-09-18完成）——`knowledge/concepts-index.md`，24个节点+一句话摘要+证据数+节点关系，增量维护
- [ ] 两级漏斗的Jaccard脚本化——待写，复用`atoms-search.py`现有IDF机制改造
- [x] `concepts_revisions.jsonl`——写入机制已建（2026-09-18，`enterprise-engine/scripts/apply.py`，每次 summary/evidence/related 变更写一条，带 `ledger_ref`）；XY 自己的库尚未发生修订，文件暂不存在
- [ ] 全库近似重复清理——扫描报告已出（`docs/reports/near-dup-scan-2026-09-18.md`，`scripts/atoms-near-dup-scan.py`），结论：措辞级重复很少；"同观点不同措辞"型靠文本相似度找不出，只能在概念节点内人工看（报告 N 档）。处理待人工
- [ ] `ontology-lint.py`要不要扩展校验concepts.jsonl——待概念层稳定后评估

### 阶段1真实发现（重要，影响后续规模化）

1. **私域运营topic数据质量问题（2026-09-18重新核实，数字与最初估计不同）**：3616条里最初粗估约44%是通用商业管理内容，**独立重新核实后实际为2289条（63.3%），集中在`XY-CE`/`XY-CS`/`XY-CF`/`XY-BK3`四个前缀**（这4个前缀总计2301条，其中仅12条被确认是真正私域方法论）——内容是第三方通识商业管理/行为经济学/医疗零售供应链咨询案例的蒸馏，机械缀一句"在私域运营中……"就被打上私域运营标签，与23个候选节点全部零匹配。真实占比高于最初印象，原因是最初的"44%"来自部分批次的粗略观感，"跟23个候选节点零匹配"本身也不是完美的通用性代理指标（有些零匹配的原子其实是真私域内容，只是23个候选没覆盖到）——重新核实改为直接读原子内容判断"核心机制是否依赖企业级基础设施/组织架构，私域只是句末强行安上的类比"，方法更直接但也承认无法做到100%精确，样本复核约150+条。已在`ontology-schema.md`新增`通用商业管理`topic并完成批量改标，`ontology-lint.py`跑通0违规。
2. **"微信账号安全运营手册"知识簇范围核实**：核心authored区间精确核实为`XY-KB-021`~`XY-KB-039`（连续19条，"约15条"的估计偏少），另在全库排查后找到17条散落但主题高度吻合的原子（`XY-KB-263/385/396/566`、`XY-PR-074/080/081`、`XY-SY-0048/0113/0115/0122/0126`、`XY-SY2-0289/0296/0302`、`SCP-042`），加上1条动机性案例`XY-KB-040`，共36条证据，已补为`CPT-SY-024`。
3. **2处`contradicts`已正式标注（2026-09-18落地）**：
   - `IPP-031`（一转门槛不能定太高，建议100元以内）↔`XY-DY-053`（化妆品一转直接定880元用于过滤客户）——已互标`contradicts`。
   - `XY-DY-190`（"9.9元课卖越多IP越不值钱"）——重新核实后发现直接对立面不是`IPP-031`（品类不同，勉强关联属于硬凑），而是`XY-DY-089`（明确建议知识付费/IP创作者用5-9.9元低价课导流），两者针对同一场景给出精确相反建议，已互标`contradicts`。详见`concepts-schema.md`本文件"contradicts关系判断"章节的真实案例记录。
