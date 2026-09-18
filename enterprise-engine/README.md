# 企业引擎（enterprise-engine）

XY 本体方法论的企业版执行包。零依赖纯 Python，**默认离线全功能**，判断由运行环境里的模型（客户自己的 Claude Code 会话）完成，脚本只负责校验、检索、出题对答案。

设计依据：`docs/superpowers/specs/2026-09-18-paid-engine-architecture-proposal.md`（闸门式流水线 + 三档服务 + 本地优先）。定位：内部知识 / 运营 / 合规场景，不做获客销售场景。

## 目录

```
enterprise-engine/
  README.md
  profile.example.json      # 客户画像模板：topics、id 格式、来源类型、偏好来源
  scripts/
    ontology-lint.py        # 与仓库根目录同源（改一处要同步另一处）；从 profile.json 读画像、来源名单；--sources-dir 查原文照搬
    atoms-search.py         # 去掉云端默认与 XY 专属降噪；--remote 显式给地址才联网；每次检索默认写一行台账（--no-ledger 关）
    ledger.py               # G6：使用台账（explicit / implicit / conflict 三种信号）
    consolidate.py          # G6：台账 → 迭代闸门包 + 提案 jsonl，离线，只产提案
    apply.py                # G6：人拍板后落盘，写 revisions，判例回写 rules/precedents.jsonl
  gates/
    GATE-TEMPLATE.md        # G0–G6 共用的闸门包模板
  rules/                    # 校准规则骨架：每个工程一份，在闸门上由人拍板后回写
    extraction.md quality.md dedup.md contradicts.md
```

回归套件在仓库根 `regression/`，企业工程用 `python3 <xy仓库>/regression/run.py emit` 出题、在客户环境作答、`score` 算一致率——这是 G-1 校准闸门。**如实说明**：套件里的 170 题来自 XY 自己的私域运营知识库，11 题来自一次真实代码库实操；它测的是"客户环境的模型做这类判断（证据归属/话题归属/矛盾/去重/命名撞车）靠不靠谱"，不是客户领域本身。客户领域的判例要在 G1–G4 闸门上积累进 `rules/`，再回灌成客户自己的回归题。

## 一个客户工作区长什么样

```
<客户工作区>/
  ontology/profile.json     # 从 profile.example.json 起，G0 定稿
  ontology/rules/*.md       # 从本目录 rules/ 复制骨架，逐闸门填
  ontology/gates/G*.md      # 闸门包归档
  knowledge/atoms.jsonl  concepts.jsonl  concepts_revisions.jsonl  usage_ledger.jsonl
  scripts/                  # 从本目录 scripts/ 复制
```

## 六步法 ↔ 闸门序列

免费层 `xy-ontology` 对外讲的是"六步法"（定边界→抽实体→定类型→建层级→抽关系→验证）；引擎内部跑的是闸门序列。两套说法必须能对上，否则客户从免费层走过来会迷路：

| 六步法（对外说法） | 闸门（引擎内部） | 说明 |
|---|---|---|
| 定边界 | G0 | 管什么、不管什么；topics 从数据里抽 |
| 抽实体 | G1 | 3 篇样本定抽取规则，"一个原子一个判断" |
| 定类型 | G1 + G2 | type 归 G1 的规则；批次数据质量归 G2 |
| 建层级 | G4 | 概念节点聚合、refines/父子层级 |
| 抽关系 | G3 + G4 | contradicts 走 G3 人闸；其余关系在 G4 |
| 验证 | G5（+ G-1 校准在开工前） | lint 0 违规、索引、矛盾清单 |
| （持续运营，六步法没这一步） | G6 | 客户反馈驱动的迭代 |

## 闸门序列（不变核，顺序不可改）

| 闸门 | 定什么 | 自助档能否自过 |
|---|---|---|
| G-1 校准 | 当前环境在回归套件上的一致率，低于阈值不开工 | 能 |
| G0 边界 | 管什么、明确不管什么；topics 从数据里抽出来再确认，不预设 | 能 |
| G1 抽取规则 | 3 篇样本 → 人改 → 改法写成 `rules/extraction.md` | 能，必须人点头 |
| G2 批次质量 | 每个批次独立抽样，规则写进 `rules/quality.md`；上游估计只作先验 | 能，附抽样 |
| G3 矛盾候选 | 同场景、同决策维度、方向相反才算；`rules/contradicts.md` | 不能自动应用 |
| G4 去重与层级 | related≠same，宁可留重复；`rules/dedup.md` | 能，默认保留 |
| G5 验收 | lint 0 违规 + 索引 + 矛盾清单 | 能 |
| G6 迭代 | 合并器从 ledger 生成提案，人闸采纳 | 只放行证据追加与别名 |

## 不变核（脚本里写死，profile 改不了）

8 个 type 及其校验语义、5 个 rel、"一个原子一个判断"、原子挂节点 / 节点连节点、`contradicts` 不自动推断、case/number 必须有来源、无死链、枚举封闭。客户领域需要新类型时用 `profile.json` 的 `type_aliases` 映射到 8 个之一，不新增。

## 网络出口（全部可选，默认关）

| 出口 | 默认 | 替代 |
|---|---|---|
| 检索远端 | 关（`--remote` 显式给） | 本地文件 |
| 规则包更新 | 关 | 文件拷贝 |
| 遥测 | 关 | 不开 |
| 闸门包上传 | 关，逐包确认 | 客户脱敏后自行传递 |

许可校验（如需要）用本地签名文件，不联网。
