# G-1回归套件校准修复：题面缺判断口径+单一阈值混判

来源：Kimi Code在添行健项目实操中跑出的三轮实测（本地26B裸考/注规则、DeepSeek注规则），完整报告见`~/Desktop/G1回归套件问题报告-给ClaudeCode-2026-09-20.md`（不在仓库里，用户本地留档）。

## 发生了什么

两个完全独立、不同厂商的模型（gemma-4-26b本地、DeepSeek v4-pro）跑G-1校准，强标签一致率都卡在73.8%，过不了80%阈值。失分高度集中在同一种题、同一种错法（topic_reclass该remove判keep，各错14-15次）。两个独立模型犯一样的错，大概率不是模型的错，是题的标尺有问题。

## 根因（已逐条核实，不是只信报告）

1. **topic_reclass的标准答案编码了XY内部口径，题面没写**。抽查`TP-0001`（原子`XY-CE-2962`）：题面只有原子正文+"是否应保留私域运营标签"，标准答案`remove`，依据是`source`字段里的"HANDOFF-1任务1：判定为通用商业管理内容机械缀话题词，已改标"——这句话从未出现在题面里。模型看到"高净值会员非标权益设计"判"该保留"完全合理，因为它不知道XY有"机械缀话题词不算私域核心场景"这条暗规矩。这考的是信息差，不是判断力。
2. **单一80%阈值把不同性质的题混在一起判生死**。`evidence_link`（84%+，两个模型都在线）和`topic_reclass`（口径未知的重灾区）共用一个阈值，导致够用的模型被有争议的题拖死。
3. dedup的挂科有真有假：`refines→merge`是真错误；`refines↔keep_separate`边界本身有主观性。

## 修复（`regression/run.py`）

- 新增`CRITERIA`字典：`emit`时给`topic_reclass`/`dedup`的每道题额外带一个`criteria`字段，把判断口径明文写给作答的模型看，不再让它猜XY的暗规矩。
- 新增`THRESHOLDS`字典：`score`默认改成按kind分别设阈值过闸（`evidence_link`/`dedup`≥80%，`topic_reclass`≥70%，`contradicts`/`name_collision`/`aggregate_gap`题量不足只报告不设闸），不再用一把尺子量所有题。原来的`--min`全局阈值参数保留，显式传入时走旧逻辑，向后兼容。

## 没做的（本轮范围外，需要人工判断）

- **争议题复核**：两个独立模型一致但与标准答案不一致的约20-30题，可能有2-4题该改标或降级成weak——这需要人工逐题看，不是脚本能判断的，留给下一轮。
- **补小样本题量**：`contradicts`(5题)、`aggregate_gap`(2题)样本太小，成绩没有统计意义，建议后续从XY历史改标记录里补到contradicts≥20、aggregate_gap≥10。

## 验收标准

gemma-4-26b和DeepSeek注入口径后重考，`dedup`/`evidence_link strong`应≥80%；若仍不过，那才是模型真不行，按README指引换模型。
