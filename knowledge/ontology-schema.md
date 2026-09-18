# XY 知识原子本体（Ontology Schema）v1

给 `atoms.jsonl` 定义的最小可用本体：Class（类型语义）+ Relation（关系语义）+ Action（可执行动作）+ 校验规则。
不引入新依赖，纯 JSON 字段约定，供 `scripts/ontology-lint.py` 校验、`scripts/atoms-search.py` 检索时使用。

## 边界声明

本体管辖范围：`knowledge/atoms.jsonl`（27,966 条知识原子，2026-09-18 去重后；后续以 `wc -l` 为准）本身的结构与语义，以及围绕它的检索/校验/维护脚本（`scripts/atoms-search.py`、`scripts/ontology-lint.py`、`scripts/upgrade-related-v1.py`）。

**明确不管**：
- 各`skills/xy-*/SKILL.md`里的对话流程与教练式交互逻辑——那是本体之上的应用层，不是本体本身
- `knowledge/_internal/`下的原始素材/蒸馏中转文件——那是本体的"数据源"，本体管的是蒸馏完成后进入`atoms.jsonl`的结构化结果，不管蒸馏前的原始文本
- 具体某条原子的`knowledge`文本内容对不对（这是内容质量问题，不是本体结构问题，本体只管"这条原子的type/topics/related字段是否符合规则"）

## 参考案例

方法论在一个真实客户项目（量化交易系统，600+模块规模）上的完整六步法实操记录，匿名化版本见`knowledge/_internal/incoming/客户案例叙事-匿名版.md`（仅内部可见）。本文档是同一套方法论在XY自己原子库上的应用。

## Class（`type` 字段，8个标准值）

| type | 语义角色 | 校验期望 |
|---|---|---|
| `principle` | 底层公理，不可辩驳的判断 | 通常应有 `method`/`case` 支撑，孤立存在是警号 |
| `method` | 可执行步骤/流程 | 理想情况下有 `case` 佐证过有效 |
| `case` | 具体实证案例 | 应能追溯 `source_type`，不接受编造 |
| `anti-pattern` | 反例/警示 | 与之相对的 `principle` 或 `method` 最好能互相 `contradicts` 关联 |
| `definition` | 术语/概念的界定 | 全库应保持定义唯一，不允许同一术语两条互相矛盾的 definition 未被标注 |
| `number` | 可引用的具体数字/比例/阈值 | 必须有 `source_type` 可查，不接受无来源数字 |
| `insight` | 观察/洞察，弱于 principle 的判断 | 允许孤立存在，但大量孤立 insight 是内容质量信号 |
| `risk` | 风险提示（目前库内仅1条，暂不拆独立规则，并入 anti-pattern 校验逻辑） | 同 anti-pattern |

> 历史遗留：`anti_pattern`（下划线）为拼写错误，已于 v1 定稿时全部合并进 `anti-pattern`（连字符）。以后新增数据只允许连字符写法。

## Relation（`related` 字段结构升级）

**旧格式**（无语义，只是ID列表）：
```json
"related": ["XY-KB-162"]
```

**新格式**（v1 起，`ontology-lint.py` 校验只接受这个结构）：
```json
"related": [{"id": "XY-KB-162", "rel": "supports"}]
```

### 关系类型枚举（5种，够用不过度设计）

| rel | 含义 | 典型场景 |
|---|---|---|
| `supports` | 目标原子是本原子的佐证/证据 | principle ← case，method ← case |
| `contradicts` | 目标原子与本原子观点冲突 | principle ↔ anti-pattern |
| `example_of` | 本原子是目标原子（更抽象判断）的具体案例 | case → principle/method |
| `prerequisite_of` | 本原子是理解目标原子的前置知识 | definition → principle |
| `refines` | 目标原子是对本原子的细化/补充，同一层级 | method → method，insight → insight |

- 关系不强制对称：A→B 是 `example_of`，B→A 应标 `supports`，不是自动镜像同一个值。人工/LLM标注时按各自方向判断。
- 允许一个原子有多条不同 `rel` 的 `related`。

### topics 枚举（15个固定值，权威来源是 `knowledge/profile.json`）

商业案例与实战复盘 / 团队与模式设计 / 认知与心态 / 私域运营 / 流量获取 / AI与工具 / 成交与话术 /
选品逻辑 / 内容创作与平台 / IP人设 / 合规与风控 / 新人起步方法论 / 中国市场与下沉 / **通用商业管理（2026-09-18 新增）** / **本体论与FDE方法论（2026-09-18 新增，204 条，`XY-ONT-` 前缀，供免费层 `xy-ontology` 使用）**

`通用商业管理`新增背景：私域运营topic下重新核实发现2289条原子（占该topic全部3616条的63.3%，集中在`XY-CE`/`XY-CS`/`XY-CF`/`XY-BK3`四个前缀）实际内容是第三方通识商业管理/咨询案例/行为经济学蒸馏（如HIS系统对接、DMP建设、供应商分级管理、组织变革理论、认知负荷/心理账户等心理学效应命名），每条机械缀一句"在私域运营中……"就被打上私域运营标签，跟私域实操脱节。核实前先确认已有13个topic是否够用：`商业案例与实战复盘`看似接近但语义不同（该topic指XY自己/学员的真实实战复盘，不是第三方通识理论转译），故新增独立值而非复用。

判断标准（用于区分"通用商业管理"与真私域方法论）：核心机制是否依赖企业级基础设施/组织架构/多部门协同（如HIS系统、DMP、供应商分级、connect跨渠道会员体系、组织变革），且私域/微信只是句末强行安上的类比 → 通用商业管理；核心机制本身就是个人号/朋友圈/社群/加好友/一对一signal等私域原生动作 → 保留私域运营。已交叉核对`concepts.jsonl`证据链（真正私域方法论的273次证据匹配几乎全部来自非这4个前缀），一致。

## 校验规则（`ontology-lint.py` 强制项）

1. `type` 必须在上表8个枚举值内（不变核，写死在脚本里）
2. `topics` 每个值必须在 `knowledge/profile.json` 的 `topics` 枚举内（2026-09-18 起从画像文件读，不再硬编码；不新增前先过一遍已有的够不够用）
3. `id` 必须匹配现有前缀命名规则（如 `XY-KB-`、`RZP-` 等，脚本里维护正则白名单）
4. `related` 若存在，必须是 `[{"id":..., "rel":...}]` 结构，`rel` 必须在5种枚举内
5. `related[].id` 指向的原子必须真实存在于库中（不允许死链）
6. `case`/`number` 类型的原子，`source_type` 不能为空
7. （2026-09-18 起，可选）`profile.json` 里 `blocklist_file` 指向的来源名单（一行一个名字/笔名/账号名，文件本身在 .gitignore 里）——`knowledge`/`original` 命中即违规；另有 `--sources-dir <第三方素材目录>` 开关，原子与素材有 ≥24 字连续重合即判"原文照搬"。这是"重塑不照搬"的机器检查，补的是 `xy-atomize` 里一直写着"还没建"的那道防线

## Action层（本体上的可执行动作）

区分"本体自身的动作"（操作atoms.jsonl这个本体本身）和"应用层动作"（某个具体skill用检索结果做出的下游产出，如xy-close生成建议）——后者不算本体的Action，是建在本体之上的应用。

| Action | 触发者 | 输入 | 输出/效果 | 前置条件 |
|---|---|---|---|---|
| 检索（query） | 任意`xy-*` skill的对话流程 | 关键词/query | 命中原子列表，可选沿`supports`/`example_of`带出关联原子 | 无（`atoms-search.py`，支持`--expand-related`） |
| 写入/入库（ingest） | `xy-atomize`流程 | 新素材（对话/文档/转述） | 追加进`atoms.jsonl`的新原子（带`id`/`type`/`topics`） | 素材需先过3层内容政策判断（官方/第三方仅参考/自有经验），第三方素材禁止逐字复制 |
| 结构校验（validate） | 人工触发，`ontology-lint.py` | 全量`atoms.jsonl` | 违规清单（type非法/topics越界/id格式错/related结构错/死链/case无source_type） | 无，随时可跑，只读不改数据 |
| 关系迁移（migrate） | 人工触发，一次性脚本如`upgrade-related-v1.py` | 旧格式`related`字段 | 新格式`{"id":..., "rel":...}`结构，按type组合启发式推断`rel`值 | 仅用于结构版本升级，不做`contradicts`这类需要语义判断的自动推断 |
| 路由分发（route） | 主`xy` skill入口 | 用户提问 | 分发给对应子skill处理（如问本体论/FDE方法论 → 走新增的xy-ontology） | 需在主skill的路由表里显式登记子skill覆盖的topics |

## 迁移状态

- [x] type 拼写统一（v1，已完成，1条修复：XY-CE-6310）
- [x] `related` 从纯ID列表升级为带 `rel` 的结构（v1，已完成，见 `scripts/upgrade-related-v1.py`）
  - 5739条边全部转换：refines 3079 / supports 2537 / prerequisite_of 120 / example_of 3
  - **`contradicts` 未做自动推断**：抽查anti-pattern↔principle/method发现相当比例是近似重复内容(同一观点被不同来源重复收录，分属不同type)或弱相关噪音，规则粒度不足以可靠判断"真矛盾"，统一归入`supports`兜底。`contradicts`留给未来人工二次标注或更细的语义模型
  - 副产品发现：抽查中看到多组疑似近似重复原子（如 XY-MB-030/XY-MB-296，XY-BK3-0114/XY-BK3-0073），是后续单独做去重清理的线索，不在本次范围内处理
- [x] 检索脚本升级：`atoms-search.py` 新增 `--expand-related`，命中结果沿supports/example_of优先带出关联原子，已同步全部31处副本
- [ ] 新原子入库（`xy-atomize`）流程要求产出时直接带 `rel`，不再事后补——这条还没动，下次改 xy-atomize 时一起做
- [ ] `contradicts` 关系的人工/精细化标注——留待后续，不阻塞当前使用
