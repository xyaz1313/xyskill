# XY 知识原子本体（Ontology Schema）v1

给 `atoms.jsonl` 定义的最小可用本体：Class（类型语义）+ Relation（关系语义）+ Action（可执行动作）+ 校验规则。
不引入新依赖，纯 JSON 字段约定，供 `scripts/ontology-lint.py` 校验、`scripts/atoms-search.py` 检索时使用。

## 边界声明

本体管辖范围：`knowledge/atoms.jsonl`（27,853+条知识原子）本身的结构与语义，以及围绕它的检索/校验/维护脚本（`scripts/atoms-search.py`、`scripts/ontology-lint.py`、`scripts/upgrade-related-v1.py`）。

**明确不管**：
- 各`skills/xy-*/SKILL.md`里的对话流程与教练式交互逻辑——那是本体之上的应用层，不是本体本身
- `knowledge/_internal/`下的原始素材/蒸馏中转文件——那是本体的"数据源"，本体管的是蒸馏完成后进入`atoms.jsonl`的结构化结果，不管蒸馏前的原始文本
- 具体某条原子的`knowledge`文本内容对不对（这是内容质量问题，不是本体结构问题，本体只管"这条原子的type/topics/related字段是否符合规则"）

## 参考案例

方法论在真实场景（REDACTED交易系统，N+模块）的完整六步法实操记录，见Obsidian wiki `[内部文档路径已移除]`。本文档是同一套方法论在XY自己原子库上的应用。

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

## 校验规则（`ontology-lint.py` 强制项）

1. `type` 必须在上表8个枚举值内
2. `topics` 每个值必须在13个固定话题内（现有值，不新增前先过一遍已有13个够不够用）
3. `id` 必须匹配现有前缀命名规则（如 `XY-KB-`、`RZP-` 等，脚本里维护正则白名单）
4. `related` 若存在，必须是 `[{"id":..., "rel":...}]` 结构，`rel` 必须在5种枚举内
5. `related[].id` 指向的原子必须真实存在于库中（不允许死链）
6. `case`/`number` 类型的原子，`source_type` 不能为空

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
