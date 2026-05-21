| Skill | 主要用途 | 典型触发说法 |
|---|---|---|
| `nature-academic-search` | 多源文献检索、PubMed/CrossRef/arXiv、MeSH 检索、DOI/PMID 验证、BibTeX/RIS/nbib 转换 | “帮我查文献”“检索 APSIM 小麦校准论文”“验证这些 DOI”“导出 RIS/BibTeX” |
| `nature-citation` | 给论文段落自动匹配 Nature/CNS/Cell/Science 系列引用，生成 EndNote/RIS/Zotero 文件 | “给这段话找 Nature 系列引用”“自动补引用”“分段引用”“找 CNS 支撑文献” |
| `nature-data` | 写 Nature 风格 Data Availability，数据仓库、DOI、FAIR 元数据、受限数据说明 | “帮我写数据可用性声明”“Data Availability 怎么写”“数据放哪个仓库” |
| `nature-figure` | 做或优化 Nature/高水平期刊风格图，支持 Python 或 R，输出 SVG/PDF/TIFF | “做一张 Nature 风格图”“润色 SCI 图”“多面板论文图”“用 Python/R 画出版图” |
| `nature-paper2ppt` | 把论文/PDF/摘要/笔记做成中文学术 PPTX，适合组会、文献汇报 | “把这篇论文做成 PPT”“组会汇报 PPT”“paper sharing slides” |
| `nature-polishing` | 学术英文润色、中文学术草稿转 Nature 风格英文，偏“已有文本的打磨” | “润色这段英文”“把摘要改成 Nature 风格”“中文翻译成论文英文” |
| `nature-reader` | 把论文做成完整中英对照 Markdown 阅读版，带图表、页码、来源锚点 | “全文翻译”“中英对照读论文”“原文对照”“提取图表并放到对应位置” |
| `nature-response` | 审稿意见逐条回复、rebuttal letter、大修/小修回复 | “帮我回复审稿人”“审稿意见逐条回复”“major revision response” |
| `nature-writing` | 从结果、图表、实验笔记出发写论文段落，偏“重建/起草论文逻辑” | “帮我写 Introduction”“根据这些结果写 Discussion”“重写摘要结构” |



使用 Superpowers 的流程，自动选择合适的 skills。不要跳过设计、测试、review 和验证。




| Skill                              | 最适合什么时候用                                                                                                                                          | Codex 里可以这样说                                                                              |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| **using-superpowers**              | 每次新会话/新任务开始时，让 agent 先判断该用哪个 skill。它的规则是：只要有一点可能适用，就先加载相关 skill；用户明确指令优先级最高。([GitHub][1])                                                         | `使用 superpowers 的流程处理这个任务，先判断该用哪些 skills。`                                                |
| **brainstorming**                  | 任何“创造性/设计型”工作开始前：新功能、改交互、加组件、改行为、设计架构。它要求先理解项目、逐个提问、提出 2–3 个方案、得到设计确认，再写 spec；不允许直接写代码。([GitHub][2])                                              | `用 brainstorming 帮我设计这个功能，先不要写代码。功能是……`                                                   |
| **writing-plans**                  | 已经有 spec / 需求后，把它变成非常细的实现计划。适合多步骤功能、重构、迁移、复杂 bug 修复。计划会包含文件路径、测试、实现步骤、验证命令和 commit 步骤。([GitHub][3])                                               | `根据刚才的 spec，用 writing-plans 写一个可执行 implementation plan。`                                  |
| **using-git-worktrees**            | 开始真正改代码前，需要隔离当前分支，避免污染主工作区。适合新功能、实验性改动、大型重构、执行实现计划前。它会先检测是否已经在隔离环境，再优先使用平台原生 worktree，最后才 fallback 到 git worktree。([GitHub][4])                   | `在实现前用 using-git-worktrees 建一个隔离工作区。`                                                     |
| **subagent-driven-development**    | 已经有 implementation plan，而且任务可以相对独立时。它会每个任务派 fresh subagent，并且每个任务后做两轮 review：先看是否符合 spec，再看代码质量。适合 Codex/Claude 这类支持子 agent 的环境。([GitHub][5])     | `用 subagent-driven-development 执行这个 plan，每个 task 完成后做 spec review 和 code quality review。` |
| **executing-plans**                | 已经有 written plan，但不使用 subagent 或者要在单独 session 中按计划执行。它会先审查计划，再逐项执行，遇到 blocker 停下来，不猜。([GitHub][6])                                                | `用 executing-plans 按这个 plan 一步步实现，遇到不明确的地方先停。`                                            |
| **test-driven-development**        | 实现任何新功能、bugfix、重构、行为变更时。它的铁律是：没有先失败的测试，就不写生产代码；流程是 RED → GREEN → REFACTOR。例外通常只有一次性原型、生成代码、配置文件，而且还要先问用户。([GitHub][7])                            | `严格使用 test-driven-development：先写失败测试，确认失败，再写最小实现。`                                        |
| **systematic-debugging**           | 遇到 bug、测试失败、构建失败、性能问题、集成问题、异常行为时。重点是先复现、读错误、查最近变化、收集证据、形成单一假设，再修根因；不允许“猜一个 fix 试试”。([GitHub][8])                                                  | `用 systematic-debugging 修这个失败测试。不要猜，先找 root cause。`                                       |
| **dispatching-parallel-agents**    | 有多个相互独立的问题可以并行调查时，例如 3 个不同测试文件失败、多个子系统独立报错。不要用于同一个根因导致的连锁问题，也不要用于会编辑同一批文件的任务。([GitHub][9])                                                        | `这几个 failing tests 看起来在不同模块，用 dispatching-parallel-agents 分别调查。`                          |
| **requesting-code-review**         | 完成一个 task、一个大功能、复杂 bugfix，或者准备 merge/PR 前。它会让 reviewer subagent 基于 git diff、需求和上下文做审查；在 subagent-driven-development 里每个 task 后都应该用。([GitHub][10]) | `实现完成后用 requesting-code-review 审查这次改动，重点看是否符合需求和有没有隐藏问题。`                                 |
| **receiving-code-review**          | 收到 review 意见后，不要盲目接受，也不要表演式赞同。适合处理人类 reviewer、AI reviewer、外部审查建议。它要求先读懂、复述/澄清、验证是否适合当前代码库，再逐项实现。([GitHub][11])                                    | `用 receiving-code-review 处理这些 review comments，先判断哪些真的需要改。`                                |
| **verification-before-completion** | 准备说“完成了”“测试通过了”“bug 修好了”“可以 merge 了”之前。它要求新鲜运行完整验证命令，读输出和 exit code，有证据再声明完成。([GitHub][12])                                                       | `在宣布完成前用 verification-before-completion 跑完整验证，不要只说 should pass。`                          |
| **finishing-a-development-branch** | 实现完成、测试通过后，决定怎么处理分支：本地 merge、push 并创建 PR、保留分支、丢弃 work。它会先跑测试，再检测当前环境，然后给结构化选项。([GitHub][13])                                                      | `用 finishing-a-development-branch 收尾这个分支，先验证测试，再给我 merge/PR/保留/丢弃选项。`                     |
| **writing-skills**                 | 你想自己创建、修改、验证 Superpowers skill 时。它把“写 skill”当成 TDD：先设计压力场景，看 agent 没有 skill 时怎么失败，再写 skill，让 agent 通过，再迭代堵漏洞。([GitHub][14])                       | `用 writing-skills 帮我写一个新的 skill，用来规范我们项目里的数据库迁移流程。`                                       |
