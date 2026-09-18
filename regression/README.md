# 回归套件（G-1 校准闸门的基础设施）

从仓库里**已经发生过、有记录的判断**生成用例；不新造标注。用途有两个：

1. **数据漂移检测**（不需要模型）：`python3 regression/run.py check` —— 核对当前 `knowledge/` 是否仍与用例标注一致。后续任何人改了 atoms/concepts，先跑这个。
2. **环境校准**（需要模型作答）：`emit` 出答题卷 → 在目标环境（客户的 Claude Code 会话）逐题作答 → `score` 算一致率。开工前低于阈值就先调规则或换模型。

```
python3 regression/build_cases.py          # 重新生成（确定性，seed 固定）
python3 regression/run.py check
python3 regression/run.py emit [--kind evidence_link]
python3 regression/run.py score answers.jsonl --min 0.8
```

## 用例构成（181 题）

| kind | 题数 | 标签 | 来源 | 强弱 |
|---|---|---|---|---|
| evidence_link | 51 + 51 | supports / not_evidence | 私域运营 24 节点的精判证据；负例取"是别的节点证据、不是本节点证据"的真私域原子 | 正例强，负例弱¹ |
| topic_reclass | 24 + 24 | remove / keep | 63.3% 批次改标结果；keep 里 12 条是同批次里逐条核实保留的（最难负例）| 强 |
| contradicts | 5 | contradicts / same_direction / different_scene | concepts-schema.md 两组真实矛盾 + 两组被否掉的配对 + 一组近似重复 | 强 |
| dedup | 15 | refines / keep_separate | 阶段2 与跨 topic 的 10 处 refines；5 对标题有共同词但明确未建关系 | 强 |
| name_collision | 9 | same_concept_variant / layered_variant / distinct_concept / not_an_entity | 一次真实代码库六步法实操，匿名化 | 强 |
| aggregate_gap | 2 | 见用例 | 同上 | 强 |

¹ 精判做的是"列入"判断不是"排除"判断，所以"不在证据里"不等于"确定不支撑"。score 按强弱分开报告，阈值只看强标签。

## 没有的东西（如实）

- `dedup` 里没有 `merge` 正例：两天流水线里一次合并都没发生过，没有真实判例就不造。
- `contradicts` 只有 5 题：全库正式标注的矛盾就两组。以后每个 G3 闸门拍板一组就追加一组。
- 代码库用例全部匿名化：无公司名、类名、模块路径、数字。判断粒度保留到"角色描述"为止。
