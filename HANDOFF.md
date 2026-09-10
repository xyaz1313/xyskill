# 交接说明 · 给接手这个项目的 Claude Code

写给下一台机器上接手这个项目的你。这份文档假设你对这个项目一无所知，从头讲清楚。

## 一、这是什么项目

**风物执守 · XY 操盘系统**（对外英文/GitHub 名 **XY Skill**）——一套装进 Claude Code / Codex / 豆包等 Agent 里的商业与私域操盘顾问。作者是商业博主"小爷"，本人有二十年、多次从 0 到过亿的私域操盘经验。这个项目把他的实战判断沉淀成 **43 个可直接调用的 Skill** 和 **26,895 条知识原子**，每个判断都带原子编号可查。

- **公开仓库**：https://github.com/xyaz1313/xyskill （main 分支，CC BY-NC 4.0 授权）
- **当前版本**：v2.7.0
- **用户身份**：项目作者本人（不是第三方开发者），你在跟他直接对话
- **用户的邮箱**：ivandierra10@gmail.com（用于识别身份，不要用于任何对外请求）

## 二、这个压缩包里有什么

解压后你会看到这个仓库的**完整本地状态**，比公开 GitHub 仓库多两个目录（这两个目录被 `.gitignore` 排除，从没推上 GitHub，只存在本地）：

- **`知识库/`**（86 个文件）—— 这次蒸馏第三方咨询库（麦肯锡/贝恩/BCG 风格内容）时，每个技能每条信条的中间产出草稿。留着当审计留痕，不必读，除非你要复核某条引用当初是怎么蒸馏出来的。
- **`docs/decisions/`**（1 个文件，`2026-08-25-技能盘点与麦肯锡蒸馏.md`）—— **这个建议你读一遍**，是这几天工作的完整决策记录，按时间顺序记了技能盘点、蒸馏计划、执行结果、发现的问题和修复过程，11 个编号章节。比这份交接文档细得多，遇到"为什么当初这么做"的问题，先查这份。

其余内容（`skills/`、`knowledge/atoms.jsonl`、`_shared/`、`docs/` 其他文件、`scripts/`、`.claude-plugin/`）跟 GitHub 上 `main` 分支完全一致——已经逐字节核对过（commit hash 一致）。`.git` 目录也带着，历史是干净的单条 commit（`0e4b30a` → 后续两条小修），你可以直接在这个文件夹里 `git push` 到远端，不用重新配置 remote。

**这个包里没有任何 API key、密码或这台机器的本机路径**——打包前用四种方式扫描过（全仓库 grep、完整 git 历史、通用 key 格式、`.env`/credential 类文件），确认干净。

## 三、原子库怎么用（两层机制，不是只有检索）

`knowledge/atoms.jsonl`：26,895 条，每条一个 JSON 对象，字段是 `{id, type, knowledge, original, confidence, topics, skills, source_type, source_label, chapter, section, q}`。**26,895 个 id 全部唯一，零重复，打包前核实过。**

知识怎么用在两层：

1. **写死在 SKILL.md 正文里**（主路径，零延迟）：高频判断直接以中文段落写进每个技能自己的 `### 信条N` 章节，句末括号标原子编号（如"参考 XY-DY-073"）。技能文件一加载就能用，不用调用任何工具。
2. **`scripts/atoms-search.py` 检索兜底**（长尾路径）：正文没覆盖到的边角问题，技能会调用这个零依赖的 Python 脚本去全库检索。用法：`python3 scripts/atoms-search.py "<关键词>" --skill <xy-name> -k 5`。评分逻辑见脚本本身的注释（IDF 加权、教学信号加分、自有实战优先、第三方咨询库降噪）。

`source_type` 字段区分原子来源：`third_party_ip`（14,435 条，麦肯锡/贝恩/BCG 风格咨询方法论，**重写后正文绝不点名具体是哪家公司**）、`book_distilled`（6,139 条，书籍蒸馏）、`external_adapted`、`course`（自己课程，792+ 条视具体统计）、`user_import`、`account_video`（自己账号内容）、`benchmark_account_video`、`offline_course_ppt`。**自有实战类（course/user_import/account_video）在检索里享有加分优先权**，第三方咨询类在 20 个高占比技能里被降噪。

## 四、这几天做了什么（浓缩版，细节看 docs/decisions/）

1. 技能盘点定案：45 个技能砍到 43 个（`xy-live`、`xy-paid-traffic` 归档到 `_archive/`，付费投流诊断能力并入 `xy-biz-scan`）。
2. 麦肯锡/贝恩/BCG 风格咨询库（third_party_ip，14,435 条）蒸馏进 20 个技能正文，1,619+ 条引用，全部核对过零漏引、零来源泄漏。
3. 两轮全量审核（用 Fable 5 模型跑的独立 agent，不是自己审自己）：链式调用行为测试、检索质量真跑分、内容一致性审核、来源脱敏扫描、真实用户体验走查——一共挖出并修复约 30+ 处真实问题（内容矛盾、引用偏差、泄露的第三方来源、过期统计数字、真实的插件 bug）。
4. **发现并修复一个真实的 GitHub 仓库体积问题**：历史里存了 16 份 `atoms.jsonl` 全量拷贝，导致 `.git` 265MB、`git clone` 直接卡死。用 orphan branch 技术把历史压缩成单条 commit，体积降到 20MB 左右。**这个坑以后要避免再犯**——往后每次改动 `knowledge/atoms.jsonl` 这类大文件，正常 commit 就行，但如果发现仓库又开始变得很大，同样的手法可以再用一次（`git checkout --orphan`），前提是先确认没有其他协作者在用这个仓库的旧历史。
5. **发现并修复一个真实的插件安装 bug**：`plugin.json` 里多余声明了 `"hooks": "./hooks/hooks.json"`，跟 Claude Code 的自动加载约定冲突，导致插件装上就报 "Duplicate hooks file" 错误。已删除冗余声明并重新装机验证过。
6. GitHub 仓库改名：`fengwuzhishou` → `xyskill`（对齐产品英文名 "XY Skill"）。
7. README 中英文按项目自己的 `_shared/chinese-writing.md` 写作规范整体重写过一遍——用户明确反馈过早期版本"中文表达有逻辑跳跃、翻译腔"，重写后的版本用户已确认没问题。同时把结构和措辞跟参考项目 dbskill 拉开了距离，避免看起来像直接抄格式。
8. 录了一份真实的插件安装演示（`demo.gif`，用 VHS 工具真实跑了一遍 `marketplace add` → `install` → `plugin list` 全过程，不是截图拼的）。

## 五、已知问题、留着没做的事

- **`tools/` 目录从未存在过**——README 曾经错误地承诺了 `tools/build_atoms.py`、`tools/check_no_attribution` 等脚本，已经改成诚实的手动流程说明，但**真正的自动化工具没有建**。如果要往库里加新的第三方来源材料，目前的防泄漏检查全靠人工 grep，没有自动拦截。如果用户要求继续这块，需要先定规则再写代码，别急着补。
- **这台机器（打包时用的这台）到 GitHub 的网络间歇性不稳定**——`git clone` 有时几秒钟完成，有时直接超时。已确认这是**这台机器当时的代理/网络环境问题，不是仓库本身的问题**（仓库大小、内容完整性都反复验证过）。换一台机器大概率没这个问题，但如果新机器也遇到同样的 clone 超时，可以试 `git config --global http.version HTTP/1.1`（这台机器上这样能解决）。
- **`claude plugin marketplace add owner/repo` 简写形式在没配 SSH key 的机器上会失败**——报错会提示走 SSH 但没有 host key。解决方式是用完整 `https://github.com/xyaz1313/xyskill.git` 地址，README 里已经这样写了。
- 用户如果要求继续"审"这个项目，别只做表面检查——这几天的经验是：每次说"应该没问题了"，用户追问一句就会发现新的真实问题（仓库体积、插件 bug、commit 没推送等）。**养成改完东西立刻验证"真的生效了"的习惯**，包括：改完 GitHub 上能看到的文件，要么直接用 `gh api` 拉取远端内容核对，要么至少确认 `git status` 干净且本地远端 commit hash 一致——这次交接前就因为"改了但忘记 push"被用户当场抓到过一次。

## 六、跟用户协作时的规矩（这几天摸出来的，照着做）

1. **不经用户明确同意，绝不 `git commit`/`git push`/`force push`**——即使看起来是"顺手的小修"也要先说明白在改什么。这条贯穿整个项目，用户反复强调过。
2. **来源脱敏是硬红线**：知识原子重写后可以引用编号，但正文绝对不能点名具体是麦肯锡/贝恩/BCG 或任何第三方公司、书名、账号名。改动前先 grep 一遍确认没有泄露，改完再 grep 一遍确认。
3. **中文表达要过 `_shared/chinese-writing.md` 这份规范**——短句优先、不用 AI 腔套话、破折号冒号一段最多一组、别写"值得注意的是"这类翻译腔。用户对着 AI 味很敏感，会逐句挑。
4. **不要凭印象下结论，要跑真实验证**——检索准不准就真的跑一批查询看命中率；装机能不能装就真的敲命令装一遍；技能里的方法论是不是真按小爷的原子来的，就打开原文件核对关键词。这个项目的用户会一路追问"这是真的测过还是你猜的"，猜的答案迟早被戳穿。
5. **API key 之类的敏感信息只能用环境变量传，绝不写进任何会被 git 跟踪的文件**——如果用户又给你别的服务凭证，处理方式参考这次：`export` 到 shell 里现用现丢，用完后到全仓库+完整 git 历史扫描确认没有泄露再继续。
6. **交付前最后一步，永远是把改动实际推送并核实远端确实生效**——这次犯过一次"改了没推"的错误，别再犯。

## 七、怎么装、怎么验证（正常用户视角）

```bash
# 最简单
npx -y skills add xyaz1313/xyskill -g --all

# 或者 clone 自己跑
git clone https://github.com/xyaz1313/xyskill.git
cd xyskill && bash install.sh

# 或者走 Claude Code 插件市场（一定要用完整 https 地址）
claude plugin marketplace add https://github.com/xyaz1313/xyskill.git
claude plugin install xy@xy-skills
```

装完说 `/xy 新手入门`，或者直接把生意问题描述给它。

---

有问题先查 `docs/decisions/2026-08-25-技能盘点与麦肯锡蒸馏.md`，那份记得比这里细。这份交接文档写完之后，如果又发生了什么这里没提到的事，麻烦你自己在这份文档里续写一段，方便再往下交接。
