# 最终收官审查任务书 — 写给 Fable 5.1

自包含。这是这轮工作的最后一份任务书——一次真正的通盘审查，不是再加功能，是**挑毛病+补两个真实缺口**。审查标准：这套东西要拿出去跟同行PK，得扛得住真的挑刺，不是自己人互相点头。

## 一、通盘审查（把下面这些当一个整体来看，不是分块看）

- `skills/xy-ontology/`（免费层skill）
- `enterprise-engine/`（付费引擎骨架：scripts/gates/rules）
- `regression/`（回归测试集）
- `knowledge/atoms.jsonl`里新增的"本体论与FDE方法论"topic（204条）
- `knowledge/concepts.jsonl`（309个概念节点）

审查要回答：
1. 这几块东西拼在一起，是不是一个连贯的产品，还是各自为战、互相不知道对方存在？（比如`xy-ontology`的免费问答会不会跟`enterprise-engine`的付费方法论打架、说法不一致？）
2. 有没有明显的断点——用户从"免费层问完'是什么'"到"想深入用付费引擎"，中间这条路径顺不顺，还是断的？
3. `enterprise-engine`里那几个脚本（`ledger.py`/`consolidate.py`/`apply.py`/`atoms-search.py`/`ontology-lint.py`）真的能跑通一次完整的G0-G6流程吗？拿一个假想的小规模场景（不用真实客户数据，编几条假数据）自己跑一遍，跑不通的地方如实报告，不要只看代码"看起来对"。
4. `regression/run.py`的`check`/`emit`/`score`三个子命令是不是都真的能用，还是只有`check`测过？

## 二、两个真实缺口——这两件事不在你的任务范围内，原始文件在XY主会话本机磁盘上，你没有访问权限，由主会话自己处理，你不用管。只需要知道：审查报告交回来后，主会话会把处理结果同步进仓库，届时如果涉及改动`enterprise-engine/rules/`等你负责的文件，会另外通知你。

（缺口1：一本个人作者写的FDE指南书从未处理；缺口2：早期评估过的nano-ontoprompt"四层模型"架构思路从未真正对照应用——这两件事的处理结果不影响你这次审查任务的范围，专心做第一节的通盘审查即可。）

## 三、明确不需要你做的事

- `~/Desktop/fde本体论/semantica-main.zip`和`dsh-ontology-main.zip`——这两个早期已经完成了它们的作用（是"要不要做这件事"的决策参考），不需要重新挖架构细节
- `~/Desktop/fde本体论/loop-engineering-main.zip`——这跟本体论/FDE项目完全无关，是另一个独立话题（循环工程），混在同一个文件夹里但不要碰
- 不要重新设计已经拍板的架构（gated pipeline/三档服务/本地优先/G6迭代机制）

## 四、输出

一份审查报告，结构：
1. 通盘审查发现的问题清单（哪怕很小也如实列，这是"扛打"的关键）
2. 缺口1处理结果（吸收了什么/没有增量）
3. 缺口2处理结果（缺不缺Logic-Rule层，明确判断）
4. 如果发现任何critical级别的问题（比如企业引擎流程实测跑不通），优先修复，其余记录留给用户决定要不要处理

commit + push回`https://github.com/xyaz1313/xyskill.git`。
