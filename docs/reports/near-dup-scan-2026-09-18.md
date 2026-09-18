# 全库近似重复原子扫描报告

生成：2026-09-18 15:43 · `scripts/atoms-near-dup-scan.py` · 原子 28057 条 · 概念节点 309 个 · 只出报告不改数据

| 档 | 对数 | 含义 |
|---|---|---|
| A | 3 | 合并候选（措辞基本相同） |
| B | 0 | 疑似细化（短条被长条高度包含） |
| C | 57 | 高重叠（0.35 ≤ J < 0.60） |
| D | 120 | 弱重叠（0.25 ≤ J < 0.35，只列前 120） |
| N | 63 | 同一概念节点内证据对，J ≥ 0.18 |

## 先说结论

- 字符相似度只能抓'同一段话被收录两次'。已知的两组'同观点不同措辞'重复，2-gram 重合只有 0.14–0.22，跟噪音分不开——**这类重复靠文本相似度找不出来**，这一点跟 concepts-schema.md 里两级漏斗的校准结论一致。
- 找'同观点不同措辞'唯一靠谱的路是 N 档：先由概念节点给出'这几条支撑同一个判断'的先验，再在节点内比措辞。N 档的建议处理方式是按节点逐个人工读。
- 平台规则库/条文库类节点的证据天然共用句式（'微信平台规定……'），节点内阈值单独抬到 0.35，否则全是套话重合。
- 全部档位都是候选，**没有任何一条会被自动合并或删除**。

## 已知遗留案例

- XY-BK3-0073 / XY-BK3-0114：✗ 未命中（2-gram J=0.13，低于阈值，且不在同一概念节点下）
- XY-MB-030 / XY-MB-296：✗ 未命中（2-gram J=0.22，低于阈值，且不在同一概念节点下）

## A · 合并候选（3 对）

| # | 原子对 | J | 包含 | type | 来源 | 建议 |
|---|---|---|---|---|---|---|
| 1 | `XY-MC-0050` / `XY-MC-0055` | 1.00 | 1.00 | insight / definition | offline_course_ppt / offline_course_ppt | 合并候选：留表述更完整/来源更硬的一条，另一条并入其 original 或删除；type 不同，合并前先定 type |
| 2 | `XY-MC-0072` / `XY-MC-0093` | 0.77 | 0.92 | method / method | offline_course_ppt / offline_course_ppt | 合并候选：留表述更完整/来源更硬的一条，另一条并入其 original 或删除 |
| 3 | `XY-ZB-3466` / `XY-ZB-3726` | 0.60 | 0.77 | method / method | external_adapted / external_adapted | 合并候选：留表述更完整/来源更硬的一条，另一条并入其 original 或删除 |

### A 档原文对照（前 3 对）

**A-1** `XY-MC-0050`：Chatbot（聊天机器人）的本质是“对话”，而Agent（智能体）的本质是“行动”。

`XY-MC-0055`：Chatbot（聊天机器人）的本质是“对话”，而Agent（智能体）的本质是“行动”。

**A-2** `XY-MC-0072`：在进行AI素材收集时，建议遵循先进行广度研究（wide research）再进行深度研究（deep research）的顺序。

`XY-MC-0093`：在进行AI研究时，建议遵循先进行广度研究（wide research）再进行深度研究（deep research）的顺序。

**A-3** `XY-ZB-3466`：通过“目标自报+奖金挂钩”的模式激励团队。让员工根据自身能力设定KPI，老板根据达成的KPI设定奖金，以激发员工的积极性与挑战欲。

`XY-ZB-3726`：激励团队的最佳模式是“目标自定，奖金由老板定”。让员工根据自身能力设定KPI，老板根据达成的KPI设定奖金，以激发员工的积极性与挑战欲。

## B · 疑似细化（0 对）

（无）

## C · 高重叠（57 对）

| # | 原子对 | J | 包含 | type | 来源 | 建议 |
|---|---|---|---|---|---|---|
| 1 | `XY-ZB-3217` / `XY-ZB-3935` | 0.58 | 0.76 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 2 | `XY-MC-0098` / `XY-MC-0100` | 0.53 | 0.74 | insight / principle | offline_course_ppt / offline_course_ppt | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 3 | `XY-MC-0014` / `XY-MC-0015` | 0.52 | 0.86 | insight / principle | offline_course_ppt / offline_course_ppt | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 4 | `XY-MA-1310` / `XY-MA-1398` | 0.51 | 0.77 | definition / definition | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 5 | `XY-CF-0007` / `XY-CS-0295` | 0.49 | 0.75 | principle / principle | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 6 | `XY-ZB-3535` / `XY-ZB-3809` | 0.48 | 0.67 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 7 | `XY-MC-0057` / `XY-MC-0058` | 0.47 | 0.76 | definition / definition | offline_course_ppt / offline_course_ppt | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 8 | `XY-ZB-3463` / `XY-ZB-3721` | 0.47 | 0.66 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 9 | `XY-ZB-3482` / `XY-ZB-3757` | 0.47 | 0.70 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 10 | `XY-ZB-3432` / `XY-ZB-3729` | 0.46 | 0.72 | definition / definition | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 11 | `XY-MA-228` / `XY-MA-1084` | 0.46 | 0.72 | anti-pattern / anti-pattern | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 12 | `XY-MSK-045` / `XY-CE-7353` | 0.45 | 0.66 | principle / insight | book_distilled / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 13 | `XY-CS-2424` / `XY-CS-2438` | 0.44 | 0.64 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 14 | `XY-CF-0009` / `XY-CS-0297` | 0.44 | 0.66 | insight / insight | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 15 | `XY-ZB-3446` / `XY-ZB-3739` | 0.44 | 0.75 | definition / definition | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 16 | `XY-ZB-3095` / `XY-ZB-3691` | 0.43 | 0.65 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 17 | `XY-CS-1478` / `XY-CS-1525` | 0.43 | 0.65 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 18 | `XY-BK3-4390` / `XY-BK3-4457` | 0.43 | 0.66 | principle / principle | book_distilled / book_distilled | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 19 | `XY-ZB-3016` / `XY-ZB-3356` | 0.43 | 0.61 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 20 | `XY-MC-0277` / `XY-MC-0281` | 0.42 | 0.76 | method / principle | offline_course_ppt / offline_course_ppt | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 21 | `XY-CS-3249` / `XY-CS-3904` | 0.42 | 0.61 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 22 | `XY-ZB-3598` / `XY-ZB-3968` | 0.42 | 0.66 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 23 | `XY-MSK-034` / `XY-CE-7342` | 0.42 | 0.60 | principle / principle | book_distilled / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 24 | `XY-BK3-4368` / `XY-BK3-4419` | 0.41 | 0.60 | principle / principle | book_distilled / book_distilled | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 25 | `XY-ZB-3981` / `XY-ZB-3022` | 0.40 | 0.59 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 26 | `XY-CE-2641` / `XY-CE-6341` | 0.40 | 0.71 | insight / insight | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 27 | `XY-ZB-3246` / `XY-ZB-3967` | 0.40 | 0.61 | anti-pattern / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 28 | `XY-MA-340` / `XY-MA-1482` | 0.39 | 0.63 | method / principle | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 29 | `XY-ZB-3159` / `XY-ZB-3691` | 0.39 | 0.61 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 30 | `XY-ZB-3371` / `XY-ZB-3981` | 0.39 | 0.56 | anti-pattern / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 31 | `XY-ZB-3480` / `XY-ZB-3755` | 0.39 | 0.61 | principle / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 32 | `XY-CF-2165` / `XY-CF-2341` | 0.38 | 0.58 | case / case | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 33 | `XY-ZB-3095` / `XY-ZB-3159` | 0.38 | 0.65 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 34 | `XY-MA-316` / `XY-MA-1417` | 0.38 | 0.65 | case / case | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 35 | `XY-BK3-4370` / `XY-BK3-4390` | 0.38 | 0.55 | insight / principle | book_distilled / book_distilled | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 36 | `XY-BK3-4396` / `XY-BK3-4457` | 0.38 | 0.56 | principle / principle | book_distilled / book_distilled | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 37 | `XY-ZB-3371` / `XY-ZB-3022` | 0.38 | 0.56 | anti-pattern / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 38 | `XY-ZB-3588` / `XY-ZB-3836` | 0.37 | 0.62 | principle / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 39 | `XY-CF-0006` / `XY-CS-0294` | 0.37 | 0.56 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 40 | `XY-MSK-032` / `XY-CE-7340` | 0.37 | 0.57 | principle / principle | book_distilled / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 41 | `XY-BK3-4361` / `XY-BK3-4418` | 0.37 | 0.56 | principle / principle | book_distilled / book_distilled | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 42 | `XY-MA-1097` / `XY-MA-1521` | 0.36 | 0.56 | principle / definition | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 43 | `XY-BK3-4368` / `XY-BK3-4412` | 0.36 | 0.55 | principle / principle | book_distilled / book_distilled | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 44 | `XY-UZB-055` / `XY-UZB-056` | 0.36 | 0.56 | anti-pattern / anti-pattern | user_import / user_import | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 45 | `XY-ZB-3558` / `XY-ZB-3559` | 0.36 | 0.53 | anti-pattern / anti-pattern | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 46 | `XY-CS-2209` / `XY-CS-2236` | 0.36 | 0.55 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 47 | `XY-ONT-717` / `XY-ONT-817` | 0.36 | 0.58 | insight / principle | user_import / user_import | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 48 | `XY-MA-325` / `XY-MA-1423` | 0.36 | 0.56 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 49 | `XY-CE-1621` / `XY-CE-5717` | 0.36 | 0.59 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 50 | `XY-ONT-719` / `XY-ONT-819` | 0.36 | 0.60 | method / method | user_import / user_import | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 51 | `XY-ZB-3038` / `XY-ZB-3410` | 0.36 | 0.56 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 52 | `XY-MA-219` / `XY-MA-1194` | 0.35 | 0.60 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 53 | `XY-CE-1632` / `XY-CE-1637` | 0.35 | 0.60 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 54 | `XY-ZB-3495` / `XY-ZB-3559` | 0.35 | 0.60 | anti-pattern / anti-pattern | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 55 | `XY-MSK-044` / `XY-CE-7351` | 0.35 | 0.52 | anti-pattern / anti-pattern | book_distilled / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 56 | `XY-ZB-3454` / `XY-ZB-3743` | 0.35 | 0.54 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 57 | `XY-MA-106` / `XY-MA-1244` | 0.35 | 0.55 | definition / principle | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |

### C 档原文对照（前 30 对）

**C-1** `XY-ZB-3217`：通过专业参数（如克重、支数）与生活化对比（如“抹布与丝绸的区别”）相结合，将抽象的面料术语转化为用户可感知的品质差异。

`XY-ZB-3935`：通过“面料参数（如克重、支数）+ 场景化对比（如抹布与丝绸的区别）”的公式，将抽象的专业参数转化为用户可感知的品质差异。

**C-2** `XY-MC-0098`：获取“第一桶金”的核心在于身份转换：从消费者、学习者或旁观者的身份，转变为“要为他人承担结果的人”。身份转变后，决策标准将从“个人喜好”转向“如何建立可信度”。

`XY-MC-0100`：获取第一桶金的关键不在于执行力，而在于身份的转换：从消费者、学习者或旁观者，转变为“要为他人承担结果的人”。这种身份转变会使决策标准从“个人喜好”转向“建立外部信任”。

**C-3** `XY-MC-0014`：语言考古学揭示了人类认知的本质：人类并非直接把握客观现实，而是通过一个经过压缩、符号化的“中间层”（语言/概念）来感知和理解现实。

`XY-MC-0015`：人类并非直接把握现实，而是通过一个经过压缩的中间层（语言/概念）来感知和构建现实。

**C-4** `XY-MA-1310`：用户心智转化路径分四个阶段：A“不觉得自己需要”→B“有点感兴趣”→C“被打动、深入了解”→D“付费购买”，不同阶段有不同卡点。新IP拍视频应根据目标用户所处心理状态定位内容，用一环扣一环的内容引导用户付费。

`XY-MA-1398`：用户心智转化路径的四个阶段：A“不觉得自己需要”→ B“有点感兴趣”→ C“被打动、深入了解”→ D“付费购买”。不同阶段有不同卡点，内容策略要针对所处赛道的关键卡点设计。

**C-5** `XY-CF-0007`：业务导向的数字化转型原则：数字化转型不应被视为单纯的技术升级问题，而应被定义为一个“业务机会”。成功的关键在于让业务领袖和一线人员深度参与并进行技能升级，使数字化能力真正嵌入到日常的文化与行为中。这意味着技术团队应作为赋能者，而非单纯的指令中心。

`XY-CS-0295`：业务驱动的数字化原则：数字化转型不应被视为一个纯技术问题，而应被定义为一个业务机会。成功的关键在于让业务领袖和一线人员深度参与并进行技能升级，使数字化能力真正嵌入到日常的文化与行为中。技术团队应扮演“创新骨干”而非“指挥中心”，通过提供平台（如数据湖、治理标准）来赋能一线业务部门进行自主创新。

**C-6** `XY-ZB-3535`：通过“极端售后承诺”（如要求销毁产品后拍照）来展示对品质的绝对信心，制造强烈的信任冲击。

`XY-ZB-3809`：通过极端化的售后承诺（如要求用户销毁产品并拍照）来展示对品质的绝对信心，从而消除消费者的售后顾虑。

**C-7** `XY-MC-0057`：元提示词（Meta Prompt）是指能够驱动AI自动生成或优化提示词的提示词技术。

`XY-MC-0058`：元提示词（Meta Prompt）是指能够让AI生成或优化提示词的提示词，用于构建更高级的指令框架。

**C-8** `XY-ZB-3463`：通过对标学习应遵循“先抄再超”的路径。通过拆解场景、爆款、话术、主图、文案、配方和模式等维度进行复刻，在积累行业敏感度后再寻求超越。

`XY-ZB-3721`：在行业起步阶段，应采取“先抄再超”的策略。通过拆解并模仿对标账号的场景、爆款、话术、主图、文案、配方和模式，在积累行业敏感度后再寻求超越。

**C-9** `XY-ZB-3482`：根据镜头景别切换话术：近景用于控场和强调细节（如“看着我的眼睛”）；中景用于发放福利；远景用于展示产品整体版型。

`XY-ZB-3757`：根据镜头景别切换话术重点：近景用于控场与细节重点，中景用于展示福利，远景用于展示产品整体版型/效果。

**C-10** `XY-ZB-3432`：话术逻辑是指主播在直播过程中采用的一套有条理、有逻辑的语言表达方式和思维框架，旨在使直播内容清晰易懂，有效传达信息。其包含的环节包括：开场、拉新、互动、塑品、憋单、逼单、上车等。

`XY-ZB-3729`：直播间话术逻辑的定义：指主播在直播过程中采用的一套有条理、有逻辑的语言表达方式和思维框架，旨在使内容清晰易懂，有效引导用户停留、转化与下单。

**C-11** `XY-MA-228`：做IP定位最大的误区之一是把“定位”等同于“选赛道”——任何赛道都同时存在赚钱和不赚钱的人，赛道只能决定内容的大致范围，决定不了内容方向、内容质量，更决定不了获客变现能力；同一个赛道也可能吸引到大量不付费甚至负面的流量。

`XY-MA-1084`：把定位等同于选赛道是最大的误区。赛道只能决定内容的大致范围，决定不了内容方向与质量，更决定不了你能吸引谁、谁会付费以及生意规模；任何赛道都同时存在赚钱和不赚钱的人。

**C-12** `XY-MSK-045`：递归效应（重量/成本累积）：在复杂系统中，增加一个变量（如产品重量、业务复杂度）会产生连锁反应。例如在火箭中，增加1吨重量可能需要额外2吨燃料来抵消；在业务中，增加一个环节也可能导致后续所有流程的复杂度呈指数级上升。

`XY-CE-7353`：递归效应（重量/成本累积）：在复杂系统中，增加一个变量往往会带来连锁反应。例如增加1吨重量可能需要额外2吨燃料来承载，这在业务逻辑中表现为：增加一个环节可能导致后续所有环节的复杂度呈指数级增长。因此，必须在系统设计初期就进行极限减法。

**C-13** `XY-CS-2424`：试点先行与分阶段迭代法。在复杂业务（如医药电商）落地时，不采取全量铺开策略，而是通过“地理区域（如青岛、宁波）+特定场景（如DTP药房、云医院）”进行小规模试点。通过建立“版本号管理（如pv1.0/dv1.0）”和“功能边界划分”，在验证核心流程（如购药、处方流转）后再进行规模化扩张。这能有效降低系

`XY-CS-2438`：“试点先行+分阶段迭代”法。在大型复杂业务（如医药电商）落地时，不采取全量铺开模式，而是通过“地理区域（如青岛、宁波）+特定场景（如云医院、DTP药房）”进行小范围试点。通过版本号管理（如pv1.0/dv1.0）控制功能边界，先跑通最基本流程（如购药、处方上传），再逐步增加增值功能。这种方法能有效降

**C-14** `XY-CF-0009`：数据驱动的根因分析逻辑：利用机器学习和自然语言处理（NLP）技术，从海量的生产记录、设备参数及历史偏差案例中提取特征。通过对非结构化文本（如质量报告）的解析，可以实现从“事后调查”向“事前预测/实时建议”的转变，自动识别导致生产故障或质量偏差的关键驱动因素（Drivers）。

`XY-CS-0297`：数据驱动的根因预测逻辑：利用机器学习和自然语言处理（NLP）技术，从海量的历史偏差数据、设备状态观察及工艺订单中提取特征。通过对非结构化文本（如质量报告）的解析，可以实现从“事后调查”向“事前预判”的转型。例如，通过分析历史故障模式与设备参数的关系，可以为操作员提供最佳设置建议，从而大幅降低生产偏差

**C-15** `XY-ZB-3446`：引流款（钩子款）的作用是吸引流量、增加停留并建立新粉丝对主播的初步信任。

`XY-ZB-3739`：引流款（钩子款）的核心作用是吸引流量进入直播间、增加用户停留时长，并利用低价/高价值感建立新粉丝对主播及直播间的初步信任。

**C-16** `XY-ZB-3095`：通过“限时、限量、不返场”的组合拳，制造紧迫感，促使犹豫用户快速下单。

`XY-ZB-3691`：通过“限时、限量、即将下播”等话术制造紧迫感，促使犹豫用户立即下单。

**C-17** `XY-CS-1478`：端到端交付时间优化法：通过缩短从采购、生产到销售的全链路环节（如减少等待生产时间、优化运输路径），实现交付速度的提升。在快消品等高频交易场景中，交付时间每缩短1%，可辅助销售额提升约0.1%。这不仅是服务能力的体现，更是通过快速迭代产品设计和提高物流响应速度来直接驱动营收增长的手段。

`XY-CS-1525`：端到端交付时间优化法：通过压缩从采购、生产到销售的全链路环节（如缩短等待生产时间、优化运输路径），实现交付速度的提升。在消费品生意场景中，交付时间每缩短1%，可辅助销售额提升约0.1%。这不仅能通过快速迭代应对多变需求，还能显著提升资金周转率和现金流。

**C-18** `XY-BK3-4390`：组织韧性原则：在动荡与快速变化的经济环境中，管理者的首要任务是确保组织的生存能力。这要求组织必须具备坚实的结构和稳固的底层逻辑，使其能够承受突发打击、快速适应环境改变，并能敏锐捕捉新出现的市场机会。对于中小生意人而言，在扩张前必须先建立抗风险的组织能力。

`XY-BK3-4457`：组织生存韧性原则。在动荡或快速变化的经济、社会与科技环境中，管理层的首要任务不是预测未来，而是确保组织的生存能力。这要求组织必须具备坚实的结构和稳固的能力，能够承受突然的打击、适应突发的改变，并能敏锐地捕捉并利用新出现的市场机会。对于中小生意人而言，这意味着在扩张期也要保持现金流与组织结构的冗余度。

**C-19** `XY-ZB-3016`：通过“不强制关注/点灯牌”的表态，降低新进用户的防御心理，建立“利他”的人设，为后续通过规则筛选精准用户做铺垫。

`XY-ZB-3356`：通过“不强制关注/灯牌”的表态来降低用户的防御心理，建立“利他”的人设，实则为后续的控场和转化做铺垫。

**C-20** `XY-MC-0277`：在Agent设计中，Shell/Bash/CLI接口具有极高的权限广度，且由于命令生成准确率高，与大模型的对接效果极佳。

`XY-MC-0281`：在操作系统层面，Shell/Bash/CLI 接口具有极高的权限与能力广度，能够控制几乎整个操作系统，且由于命令结构化程度高，与大模型的对接效果与命令生成准确率也最为出色。

**C-21** `XY-CS-3249`：产品生命周期策略（PLC Strategy）：根据市场接受度和销售增长情况，将产品分为导入期、成长期、成熟期和衰退期。处于成长期的产品应加大市场投入以抢占份额；成熟期产品应侧重巩固地位；衰退期产品则应停止投入，转而采取“榨取利润”的策略。

`XY-CS-3904`：产品生命周期动态配置法：根据产品所处的导入期、成长期、成熟期或衰退期，采取差异化经营策略。成长期的产品应加大市场投入以抢占份额；成熟期产品应侧重巩固地位；衰退期产品则应停止投入，转而通过“榨取利润”来获取剩余价值。

**C-22** `XY-ZB-3598`：拉新/测款万能框架：通过“提价值（对比市场价）+降价格（给出合理理由/钩子）+互动（筛选意向用户）+库存（制造紧迫感）+上车（引导动作）”的闭环逻辑进行快速过款。

`XY-ZB-3968`：万能拉新/快速过款框架：提价值（对比价格/痛点） → 降价格（给出合理理由/钩子） → 互动（筛选用户） → 库存/上车（刺激紧迫感）。

**C-23** `XY-MSK-034`：反馈脱敏原则：在管理中，沟通应遵循“坏消息大声说、反复说，好消息小声说一遍”的原则。反馈应聚焦于“行为”而非“个人”，通过不留情面的事实纠偏来建立高效的反馈循环。领导者应避免为了维持“同事情谊”而对错误视而不见，因为过度照顾个人感受会掩盖业务风险，最终损害整体利益。

`XY-CE-7342`：反馈脱敏原则：在管理中，应遵循“坏消息大声说、反复说，好消息小声说一遍”的原则。反馈应聚焦于“行为”而非“个人”，通过不留情面的真实反馈来建立高效的改进循环。领导者的职责是确保事情做成，而非追求让每个成员都喜欢自己；过度照顾员工感受会导致管理软弱和效率低下。

**C-24** `XY-BK3-4368`：管理本质上是一种实践，其验证标准不在于逻辑推演的严密性，而在于最终产出的成果。对于生意人而言，这意味着不要陷入“过度规划”的陷阱，所有的战略和动作都必须以实际的市场反馈（如转化率、复购率、GMV）作为唯一检验标准，通过“行动-反馈-调整”的闭环来迭代。

`XY-BK3-4419`：管理本质上是一种实践，其验证标准不在于逻辑推演的严密性，而在于最终产生的“成果”。对于私域或小生意操盘手而言，这意味着不要陷入过度追求理论完美的陷阱，所有的营销策略、话术设计和运营动作都必须以“转化率”、“复购率”等实实在在的经营结果为唯一检验标准。

**C-25** `XY-ZB-3981`：这是制造稀缺/紧迫感/信任错觉的话术套路。通过设定极低的中奖概率（如100人抢10件）来制造抢购氛围。

`XY-ZB-3022`：这是制造稀缺/紧迫感/信任错觉的话术套路。通过设定“关注/灯牌用户”与“非关注用户”的价格差，利用规则差异制造抢购氛围。

**C-26** `XY-CE-2641`：价格敏感度非对称性：在物流或标准化服务场景中，客户对“降价”带来的货量增长敏感度，往往高于对“加价”导致的货量流失敏感度。这意味着通过精准降价获取市场份额的效率，可能高于单纯提价带来的利润增量。

`XY-CE-6341`：价格敏感度非对称性原理：在物流或标准化服务领域，客户对“降价”带来的货量增长敏感度，通常远高于对“加价”导致的货量流失敏感度。例如，同样是10%的价格变动，降价可能带来100%的货量增长，而加价仅导致50%的货量减少。在生意场景中，这意味着通过适度降价获取市场份额（规模效应）的效率，往往高于单纯维持

**C-27** `XY-ZB-3246`：这是制造稀缺/紧迫感/信任错觉的话术套路：通过宣称“库存有限”、“名额有限”或“踢掉未付款订单”来制造抢购氛围，促使犹豫用户快速下单。

`XY-ZB-3967`：这是制造稀缺/紧迫感/信任错觉的话术套路。通过指责用户“占了别人库存”或“不付款”来制造竞争感，促使犹豫用户快速下单。

**C-28** `XY-MA-340`：最精准的用户定位往往不是找到用户"想要什么单一需求",而是找到用户同时想要两件看似冲突的事,并同时回应矛盾的两端才能形成真正的差异化。例如年轻家长群体反对应试式"鸡娃"、强调孩子自我,但又渴望孩子在竞争中拥有优势,只有内容同时满足"反鸡娃"和"渴望牛娃"两端,才能真正锁定这类用户,这个思路可迁移到任

`XY-MA-1482`：定位用户的意识形态矛盾而非单一需求：最精准的定位不是找到用户想要什么，而是找到用户同时想要的两件看似冲突的事（如反对鸡娃但渴望牛娃、强调自我但不放弃成绩），只有同时回应矛盾的两端才能真正锁定这类人。此思路可迁移到任何服务持矛盾心理用户的赛道。

**C-29** `XY-ZB-3159`：通过“限时限量/倒计时/最后几单”等话术制造紧迫感，促使犹豫的观众快速下单。

`XY-ZB-3691`：通过“限时、限量、即将下播”等话术制造紧迫感，促使犹豫用户立即下单。

**C-30** `XY-ZB-3371`：这是制造稀缺/紧迫感/信任错觉的话术套路。通过声称‘经销商全部拿走’或‘库存不多了’来制造抢购氛围。

`XY-ZB-3981`：这是制造稀缺/紧迫感/信任错觉的话术套路。通过设定极低的中奖概率（如100人抢10件）来制造抢购氛围。

## D · 弱重叠（120 对）

| # | 原子对 | J | 包含 | type | 来源 | 建议 |
|---|---|---|---|---|---|---|
| 1 | `XY-MSK-042` / `XY-CE-7349` | 0.35 | 0.55 | principle / principle | book_distilled / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 2 | `XY-CS-2161` / `XY-CS-2285` | 0.35 | 0.54 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 3 | `XY-IPB-0036` / `XY-IPB-0037` | 0.35 | 0.58 | case / principle | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 4 | `XY-CS-2623` / `XY-CS-2639` | 0.35 | 0.52 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 5 | `XY-CS-2243` / `XY-CS-2261` | 0.35 | 0.54 | insight / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 6 | `XY-MC-0119` / `XY-MC-0125` | 0.35 | 0.53 | method / method | offline_course_ppt / offline_course_ppt | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 7 | `XY-ZB-3186` / `XY-ZB-3495` | 0.35 | 0.54 | method / anti-pattern | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 8 | `XY-CE-7189` / `XY-CE-7194` | 0.34 | 0.52 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 9 | `XY-MA-1357` / `XY-MA-1398` | 0.34 | 0.62 | principle / definition | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 10 | `XY-ZB-3159` / `XY-ZB-3889` | 0.34 | 0.60 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 11 | `XY-MA-224` / `XY-MA-1211` | 0.34 | 0.63 | anti-pattern / anti-pattern | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 12 | `XY-CS-1621` / `XY-CS-1748` | 0.34 | 0.58 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 13 | `XY-CF-2071` / `XY-CF-2254` | 0.34 | 0.52 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 14 | `XY-PR-005` / `XY-PR-023` | 0.34 | 0.52 | anti-pattern / anti-pattern | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 15 | `XY-CF-1102` / `XY-CF-1141` | 0.34 | 0.54 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 16 | `XY-PR-027` / `XY-PR-071` | 0.34 | 0.55 | principle / principle | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 17 | `XY-CF-2501` / `XY-CF-2633` | 0.34 | 0.52 | insight / insight | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 18 | `XY-CF-2482` / `XY-CF-2613` | 0.34 | 0.51 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 19 | `XY-ZB-3263` / `XY-ZB-3967` | 0.33 | 0.53 | anti-pattern / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 20 | `XY-ONT-715` / `XY-ONT-815` | 0.33 | 0.58 | method / method | user_import / user_import | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 21 | `XY-PR-035` / `XY-PR-082` | 0.33 | 0.55 | principle / principle | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 22 | `XY-ZB-3095` / `XY-ZB-3889` | 0.33 | 0.50 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 23 | `XY-BK3-0651` / `XY-BK3-0657` | 0.33 | 0.53 | principle / method | book_distilled / book_distilled | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 24 | `XY-CE-4325` / `XY-CE-4354` | 0.33 | 0.53 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 25 | `XY-ZB-3096` / `XY-ZB-3124` | 0.33 | 0.50 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 26 | `XY-ZB-3437` / `XY-ZB-3735` | 0.33 | 0.57 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 27 | `XY-MA-020` / `XY-MA-1073` | 0.33 | 0.72 | principle / principle | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 28 | `XY-ZB-3246` / `XY-ZB-3263` | 0.33 | 0.50 | anti-pattern / anti-pattern | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 29 | `XY-CS-2208` / `XY-CS-2250` | 0.33 | 0.58 | method / principle | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 30 | `XY-ZB-3246` / `XY-ZB-3371` | 0.33 | 0.56 | anti-pattern / anti-pattern | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 31 | `XY-ZB-3186` / `XY-ZB-3263` | 0.33 | 0.54 | method / anti-pattern | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 32 | `XY-ZB-3246` / `XY-ZB-3981` | 0.33 | 0.56 | anti-pattern / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 33 | `XY-ZB-3072` / `XY-ZB-3863` | 0.33 | 0.50 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 34 | `XY-ZB-3186` / `XY-ZB-3967` | 0.33 | 0.51 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 35 | `XY-ZB-3186` / `XY-ZB-3559` | 0.33 | 0.53 | method / anti-pattern | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 36 | `XY-ONT-750` / `XY-ONT-760` | 0.33 | 0.63 | case / case | user_import / user_import | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 37 | `XY-BK3-4390` / `XY-BK3-4396` | 0.33 | 0.55 | principle / principle | book_distilled / book_distilled | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 38 | `XY-MA-321` / `XY-MA-1427` | 0.33 | 0.53 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 39 | `XY-PR-039` / `XY-PR-040` | 0.33 | 0.49 | anti-pattern / anti-pattern | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 40 | `XY-PR-025` / `XY-PR-032` | 0.32 | 0.51 | definition / principle | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 41 | `XY-PR-070` / `XY-PR-071` | 0.32 | 0.54 | definition / principle | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 42 | `XY-ZB-3015` / `XY-ZB-3110` | 0.32 | 0.51 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 43 | `XY-ZB-3861` / `XY-ZB-3022` | 0.32 | 0.56 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 44 | `XY-MA-330` / `XY-MA-1448` | 0.32 | 0.51 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 45 | `XY-PR-080` / `XY-PR-101` | 0.32 | 0.53 | principle / principle | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 46 | `XY-MA-331` / `XY-MA-1447` | 0.32 | 0.67 | method / principle | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 47 | `XY-IPB-0114` / `XY-IPB-0116` | 0.32 | 0.52 | principle / principle | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 48 | `XY-CF-2491` / `XY-CF-2622` | 0.32 | 0.53 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 49 | `XY-BK3-4345` / `XY-BK3-4455` | 0.32 | 0.51 | method / principle | book_distilled / book_distilled | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 50 | `XY-PR-010` / `XY-PR-012` | 0.32 | 0.50 | anti-pattern / anti-pattern | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 51 | `XY-BK3-4378` / `XY-BK3-4431` | 0.32 | 0.52 | principle / principle | book_distilled / book_distilled | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 52 | `XY-MC-0277` / `XY-MC-0340` | 0.32 | 0.68 | method / principle | offline_course_ppt / offline_course_ppt | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 53 | `XY-ZB-3328` / `XY-ZB-3804` | 0.32 | 0.52 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 54 | `XY-ZB-3357` / `XY-ZB-3399` | 0.32 | 0.53 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 55 | `XY-ZB-3246` / `XY-ZB-3022` | 0.32 | 0.56 | anti-pattern / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 56 | `XY-CF-0008` / `XY-CS-0296` | 0.31 | 0.52 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 57 | `XY-CS-2074` / `XY-CS-2517` | 0.31 | 0.50 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 58 | `XY-CS-1670` / `XY-CS-1749` | 0.31 | 0.56 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 59 | `XY-CS-3135` / `XY-CS-3246` | 0.31 | 0.51 | insight / insight | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 60 | `XY-CF-2177` / `XY-CF-2359` | 0.31 | 0.54 | insight / insight | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 61 | `XY-BK3-0652` / `XY-BK3-0658` | 0.31 | 0.48 | method / principle | book_distilled / book_distilled | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 62 | `XY-CS-2399` / `XY-CS-2448` | 0.31 | 0.59 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 63 | `XY-CS-3139` / `XY-CS-3902` | 0.31 | 0.52 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 64 | `XY-MA-129` / `XY-MA-1140` | 0.31 | 0.67 | definition / definition | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 65 | `XY-ZB-3266` / `XY-ZB-3695` | 0.31 | 0.54 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 66 | `XY-MSK-039` / `XY-CE-7346` | 0.31 | 0.47 | principle / principle | book_distilled / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 67 | `XY-CS-2199` / `XY-CS-2209` | 0.31 | 0.56 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 68 | `XY-PR-036` / `XY-PR-040` | 0.31 | 0.50 | anti-pattern / anti-pattern | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 69 | `XY-PR-039` / `XY-PR-042` | 0.31 | 0.50 | anti-pattern / anti-pattern | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 70 | `XY-CE-6587` / `XY-CE-6629` | 0.31 | 0.51 | principle / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 71 | `XY-ZB-3371` / `XY-ZB-3861` | 0.31 | 0.53 | anti-pattern / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 72 | `XY-MA-317` / `XY-MA-1418` | 0.31 | 0.53 | case / case | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 73 | `XY-ZB-3861` / `XY-ZB-3981` | 0.31 | 0.53 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 74 | `XY-ZB-3263` / `XY-ZB-3559` | 0.31 | 0.57 | anti-pattern / anti-pattern | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 75 | `XY-ZB-3120` / `XY-ZB-3930` | 0.31 | 0.49 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 76 | `XY-UZB-599` / `XY-UZB-612` | 0.31 | 0.50 | definition / method | user_import / user_import | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 77 | `XY-CS-2683` / `XY-CS-2691` | 0.31 | 0.48 | principle / insight | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 78 | `XY-UZB-204` / `XY-UZB-205` | 0.31 | 0.53 | principle / principle | user_import / user_import | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 79 | `XY-ZB-3559` / `XY-ZB-3967` | 0.31 | 0.53 | anti-pattern / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 80 | `XY-BK3-4356` / `XY-BK3-4390` | 0.31 | 0.51 | principle / principle | book_distilled / book_distilled | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 81 | `XY-ZB-3263` / `XY-ZB-3495` | 0.31 | 0.49 | anti-pattern / anti-pattern | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 82 | `XY-CE-1954` / `XY-CE-2136` | 0.31 | 0.51 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 83 | `XY-CE-1618` / `XY-CE-5714` | 0.31 | 0.55 | method / principle | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 84 | `XY-ZB-3366` / `XY-ZB-3894` | 0.31 | 0.48 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 85 | `XY-BK3-4434` / `XY-BK3-4542` | 0.31 | 0.47 | insight / insight | book_distilled / book_distilled | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 86 | `XY-PR-006` / `XY-PR-010` | 0.30 | 0.50 | anti-pattern / anti-pattern | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 87 | `XY-BK3-4424` / `XY-BK3-4444` | 0.30 | 0.50 | principle / principle | book_distilled / book_distilled | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 88 | `XY-BM-074` / `XY-BKG-914` | 0.30 | 0.69 | method / method | benchmark_account_video / benchmark_account_video | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 89 | `XY-BK3-0467` / `XY-BK3-0482` | 0.30 | 0.51 | insight / insight | book_distilled / book_distilled | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 90 | `XY-PR-032` / `XY-PR-035` | 0.30 | 0.48 | principle / principle | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 91 | `XY-ZB-3404` / `XY-ZB-3710` | 0.30 | 0.51 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 92 | `XY-ZB-3095` / `XY-ZB-3804` | 0.30 | 0.50 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 93 | `XY-CS-2181` / `XY-CS-2221` | 0.30 | 0.48 | principle / insight | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 94 | `XY-MSK-078` / `XY-CE-7385` | 0.30 | 0.47 | principle / principle | book_distilled / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 95 | `XY-ZB-3057` / `XY-ZB-3695` | 0.30 | 0.58 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 96 | `XY-CF-2446` / `XY-CF-2577` | 0.30 | 0.47 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 97 | `XY-PR-040` / `XY-PR-041` | 0.30 | 0.49 | anti-pattern / anti-pattern | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 98 | `XY-ZB-3186` / `XY-ZB-3246` | 0.30 | 0.51 | method / anti-pattern | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 99 | `XY-ZB-3559` / `XY-ZB-3862` | 0.30 | 0.50 | anti-pattern / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 100 | `XY-ZB-3558` / `XY-ZB-3862` | 0.30 | 0.50 | anti-pattern / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 101 | `XY-MA-1310` / `XY-MA-1357` | 0.30 | 0.49 | definition / principle | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 102 | `XY-MC-0321` / `XY-MC-0323` | 0.30 | 0.46 | principle / principle | offline_course_ppt / offline_course_ppt | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 103 | `XY-ZB-3291` / `XY-ZB-3889` | 0.30 | 0.60 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 104 | `XY-UZB-582` / `XY-UZB-583` | 0.30 | 0.52 | method / method | user_import / user_import | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 105 | `XY-ZB-3186` / `XY-ZB-3558` | 0.30 | 0.50 | method / anti-pattern | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 106 | `XY-PR-024` / `XY-PR-032` | 0.30 | 0.48 | principle / principle | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 107 | `XY-PR-078` / `XY-PR-096` | 0.30 | 0.47 | anti-pattern / anti-pattern | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 108 | `XY-MSK-083` / `XY-CE-7390` | 0.30 | 0.47 | insight / insight | book_distilled / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 109 | `XY-UZB-102` / `XY-UZB-145` | 0.30 | 0.48 | method / method | user_import / user_import | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 110 | `XY-PR-037` / `XY-PR-040` | 0.30 | 0.49 | principle / anti-pattern | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 111 | `XY-BK3-0478` / `XY-BK3-0482` | 0.30 | 0.47 | insight / insight | book_distilled / book_distilled | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 112 | `XY-PR-036` / `XY-PR-039` | 0.30 | 0.48 | anti-pattern / anti-pattern | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 113 | `XY-PR-040` / `XY-PR-042` | 0.30 | 0.48 | anti-pattern / anti-pattern | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 114 | `XY-ZB-3159` / `XY-ZB-3322` | 0.30 | 0.48 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 115 | `XY-CS-0790` / `XY-CS-0984` | 0.29 | 0.52 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 116 | `XY-CS-1472` / `XY-CS-1518` | 0.29 | 0.48 | method / method | third_party_ip / third_party_ip | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 117 | `XY-MA-1295` / `XY-MA-1386` | 0.29 | 0.48 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 118 | `XY-MC-0288` / `XY-MC-0294` | 0.29 | 0.45 | principle / insight | offline_course_ppt / offline_course_ppt | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 119 | `XY-ZB-3038` / `XY-ZB-3656` | 0.29 | 0.53 | method / method | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |
| 120 | `XY-PR-027` / `XY-PR-032` | 0.29 | 0.49 | principle / principle | external_adapted / external_adapted | 保留两条，先人工看是否同观点：是→按 A；只是同题材→无需处理 |

## N · 同一概念节点内证据对（63 对，按节点分组）

### CPT-IP-008 人设定位两维度模型（心理账户×表达姿态）（6 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-MA-238` / `XY-MA-1109` | 0.23 | definition / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-MA-1109` / `XY-MA-1538` | 0.20 | definition / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-MA-241` / `XY-MA-1117` | 0.20 | principle / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-MA-1117` / `XY-MA-1543` | 0.19 | definition / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-MA-241` / `XY-MA-1543` | 0.19 | principle / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-MA-1119` / `XY-MA-1544` | 0.18 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-CLOSE-013 用户心智转化四阶段模型（4 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-MA-1310` / `XY-MA-1398` | 0.51 | definition / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-MA-1357` / `XY-MA-1398` | 0.34 | principle / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-MA-1310` / `XY-MA-1357` | 0.30 | definition / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-MA-1357` / `XY-MA-1397` | 0.26 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-IP-006 定位方法论三代演化（人口统计学→需求→意识形态）（4 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-MA-020` / `XY-MA-1073` | 0.33 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-MA-019` / `XY-MA-1067` | 0.26 | definition / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-MA-021` / `XY-MA-1074` | 0.26 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-MA-019` / `XY-MA-1068` | 0.25 | definition / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-AIT-001 Agent与Chatbot本质区别（4 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-MC-0038` / `XY-MC-0055` | 0.27 | definition / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-MC-0055` / `XY-UZB-113` | 0.27 | definition / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-MC-0038` / `XY-UZB-113` | 0.24 | definition / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-MC-0045` / `XY-MC-0055` | 0.18 | principle / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-AIT-005 RAG/知识图谱/向量化技术原理（4 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-UZB-599` / `XY-UZB-606` | 0.22 | definition / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-UZB-593` / `XY-UZB-599` | 0.19 | definition / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-UZB-593` / `XY-UZB-600` | 0.19 | definition / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-UZB-590` / `XY-UZB-600` | 0.18 | principle / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-TRAF-014 直播间流量机制与节奏控制（3 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-ZB-3446` / `XY-ZB-3739` | 0.44 | definition / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-ZB-3462` / `XY-ZB-3718` | 0.27 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-ZB-3737` / `XY-ZB-3738` | 0.21 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-IP-007 产品-人群定位反推法（从付费动作往回推）（3 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-MA-1097` / `XY-MA-1521` | 0.36 | principle / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-MA-233` / `XY-MA-1096` | 0.29 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-MA-232` / `XY-MA-1093` | 0.21 | principle / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-SY-024 微信账号安全运营手册（3 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-PR-074` / `XY-PR-081` | 0.23 | definition / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-PR-074` / `XY-PR-080` | 0.21 | definition / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-PR-080` / `XY-PR-081` | 0.20 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-AIT-003 System Prompt结构与角色锚定原理（2 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-MC-0057` / `XY-MC-0058` | 0.47 | definition / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-MC-0053` / `XY-MC-0059` | 0.28 | principle / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-CLOSE-025 直播话术体系：环节流程与节奏控制（2 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-ZB-3432` / `XY-ZB-3729` | 0.46 | definition / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-ZB-3446` / `XY-ZB-3739` | 0.44 | definition / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-COMP-015 AI生成内容标识义务（2 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-PR-020` / `XY-PR-120` | 0.26 | principle / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-PR-020` / `XY-PR-046` | 0.22 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-AIT-009 AI辅助创作原则：放大器不是替代品（2 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-MB-119` / `XY-MB-538` | 0.22 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |
| `XY-MB-119` / `XY-MB-212` | 0.20 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-SEL-022 定位由产品反推能赚谁的钱，而非先定「我是谁」（1 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-MA-1097` / `XY-MA-1521` | 0.36 | principle / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-COMP-011 内容审核四大违规逻辑与自查框架（1 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-MA-106` / `XY-MA-1244` | 0.35 | definition / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-CONT-002 选题方法论：中心思想三要素与选题类型（1 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-MA-129` / `XY-MA-1140` | 0.31 | definition / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-AIT-007 AI Agent权限与安全设计原则（1 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-MC-0321` / `XY-MC-0323` | 0.30 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-IP-031 主播播感与控场能力设计（1 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-ZB-3434` / `XY-ZB-3731` | 0.28 | definition / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-COMP-018 AI/数据合规（隐私授权/最小权限/数据不出境/开源版权）（1 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-UZB-412` / `XY-UZB-413` | 0.27 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-COG-025 内容行业认知筛选标准（1 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-MC-0001` / `XY-MC-0015` | 0.26 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-AIT-012 大模型技术原理入门（1 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-UZB-477` / `XY-UZB-478` | 0.25 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-COMP-012 违规处罚梯度与申诉应对策略（1 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-MA-1261` / `XY-MA-1267` | 0.25 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-TEAM-014 商业模式设计核心原则（分钱决定行为/被动收入需要燃料/雇人看ROI）（1 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-MB-104` / `XY-MB-491` | 0.22 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-TRAF-016 高客单价流量策略：精准小而美优于泛流量（1 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-IPB-0121` / `XY-IPB-0120` | 0.22 | principle / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-TRAF-024 商业本质三要素与流量伪命题（1 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-MA-013` / `XY-MA-1039` | 0.21 | principle / definition | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-SEL-013 生产性兴趣与消费性兴趣的分野（1 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-MB-052` / `XY-MB-438` | 0.21 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-AIT-013 本地部署vs云端vs企业版工具选择原则（1 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-UZB-195` / `XY-UZB-196` | 0.20 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-CONT-007 原创vs借鉴辩证：懂得借力的原创者（1 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-MA-028` / `XY-MA-1048` | 0.20 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-COMP-006 私域正规化七要素/合规经营红利原则（1 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-DY-057` / `XY-SY-0005` | 0.20 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-IP-026 高客单价非标服务IP人设策略（生活人设优于纯专业人设）（1 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-IPB-0478` / `XY-IPB-0480` | 0.20 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-AIT-006 企业知识库搭建的可信上下文原则（1 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-UZB-231` / `XY-UZB-232` | 0.20 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-CLOSE-014 评论区/私信引导的自然话术原则（1 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-MA-407` / `XY-MA-1502` | 0.19 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-SEL-018 电商货盘配比与风格聚焦（1 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-MA-307` / `XY-MA-1396` | 0.19 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-AIT-017 AI创业路径与竞争策略（1 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-IPB-0257` / `XY-IPB-0414` | 0.19 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-NEW-010 执行力认知诊断：假装学习vs真实行动（1 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-MB-007` / `XY-MB-518` | 0.18 | anti-pattern / insight | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-SY-011 私域本质是能力而非行业/赛道（1 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `RZP-002` / `XY-DY-081` | 0.18 | insight / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

### CPT-COG-009 悬浮人群与自媒体两种出发点（1 对）

| 原子对 | J | type | 建议 |
|---|---|---|---|
| `XY-MA-011` / `XY-MA-1035` | 0.18 | principle / principle | 同节点证据：人工读一遍，是同观点→按 A 处理（并成一条，节点证据数减 1）；是同题材不同侧面→保留，无需处理 |

