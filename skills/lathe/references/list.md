# 列出教程

列出所有已存储的教程，或查看单个教程的详细状态。用户忘记 slug、想了解整体进度、或想确认某教程验证结果时使用。

本操作**完全只读**：不写入、不修改任何文件。

## 协议

### 无参数：`/lathe list` 或 `/lathe 列表`

1. **多路径枚举教程目录。** 解析 `~/.lathe/config.json`，取所有基础目录的并集（`tutorial_paths` 各值 + `tutorials_base_path`，去重）；只看每个基础目录的下一层子目录。子目录满足以下任一条件即是候选教程：根目录有 `metadata.json`、有 `_lathe/metadata.json`、或有至少一个根目录 `part-*.md`。跳过 `voices/`、`_lathe/`、以 `.` 开头的隐藏目录以及教程内部的嵌套目录；`_lathe/` 只是课程内部辅助目录，绝不把它单独列成教程。同一 slug 出现在多个目录时全部列出并在位置列标注，提醒用户存在副本。

2. **一次性判定布局并读取当前布局文件。** 先检查候选课程根目录的两处 metadata：

   | 布局 | 判定 | metadata | canonical ledger | verify result |
   |---|---|---|---|---|
   | 0.6.1 新课程 | 仅 `_lathe/metadata.json` 存在 | `_lathe/metadata.json` | `_lathe/knowledge-points.md` | `_lathe/verify-result.json` |
   | legacy 课程 | 仅根 `metadata.json` 存在 | `metadata.json` | `syllabus.json` | `verify-result.json` |

   两处 metadata 同时存在，或已判定布局后发现另一布局的辅助文件混入，标为 **⚠️ 混合布局冲突**，列出冲突路径；只报告，不跨布局回退或拼接。仅有 part 而 metadata 缺失的候选按第 6 步处理。布局正常时只读取该布局的 metadata、canonical ledger 和 verify result；新布局缺 `_lathe/knowledge-points.md` 是 **错误**，不得从 metadata 或 research 猜知识点状态；legacy 缺 `syllabus.json` 可显示 `知识表：未建立`。

   > **内容变更检测：** 若某 part 在当前布局 verify result 中为 `passed`，但该 part 文件的修改时间晚于 `checked_at`，在列表中标记为 **“内容已变更，需重新验证”**，不要继续显示 `passed`。只取文件 mtime，不读正文；`-review` 复习材料不参与；“增量复用跳过”（`skipped_reuse`）同样按此判断。`checked_at` 缺失时跳过本检测。若 verify result 的 `changed_interfaces_snapshot` 与当前 metadata 的 `changed_interfaces` 不一致，也标记 **“接口已变更，需重新验证”**。

   > **成本约束（重要）：本操作绝不读取 `part-NN.md` 的全文。** 一个多课程目录的正文动辄数十万字符，而列表只需要每个部分的一级标题。按以下优先级取标题：
   > 1. **当前布局 metadata 的 `continuity.part_titles`** —— 已有映射则直接用，零文件读取；**它按索引瘦身规则只保留最近 8 个部分，更早的部分在这里缺标题是正常状态**（不是数据损坏），缺的那些走第 2 档；
   > 2. 映射缺失或不完整时，用 shell **只取标题行**：`grep -m1 '^# ' <文件>`（或 `head -n 1`），单次可对整个目录批量执行：`grep -m1 -H '^# ' <目录>/part-*.md`；
   > 3. **不要**用文件读取工具打开 part 文件来找标题。
3. **识别每个教程的编程语言**（用于分组）：
   - 优先取 `tags` 中的语言/运行时标签（`<SKILL_DIR>/references/tag.md` 约定的第一类标签，如 `rust`、`zig`、`go`）；
   - `tags` 中没有语言标签时，从 `tools`（工具链名称）或 `topic` 推断；
   - 仍无法判断的归入 **其他** 组。
4. **分组展示**：
   - 教程涉及 **多于 1 门编程语言** → 按语言分大类，每个语言一个 `### <语言>` 小节，语言内列出该语言的所有课程；
   - 只有 **1 门语言** → 不分组，直接列出课程。
5. **每门课程一个紧凑条目**，多部分课程必须逐部分体现：

   ```
   **<slug>** — <标题>
   状态：<status> ｜ 最近验证：<verify status + checked_at，无则 —> ｜ 标签：<tags> ｜ 正文语言：<language> ｜ 位置：<所在目录，与默认目录相同时可省略>
   进度：taught <a> / 计划内 <d>（<p>%）
   六态：planned <n1> · queued <n2> · taught <n3> · self-study <n4> · dropped_by_user <n5> · duplicate <n6>
   部分（<N>）：
   1. part-01.md — <该部分的一级标题>
   2. part-02.md — <该部分的一级标题>
   3. part-03.md — <该部分的一级标题>
   ```

   - 进度与六态只从当前布局 canonical ledger 的数据行重建：`计划内 = taught + planned + queued`，`进度 = taught / 计划内`，百分比四舍五入为整数，计划内为 0 时显示 0%。`self-study`、`dropped_by_user`、`duplicate` 不进分母；六态始终全部展示，包括 0。
   - legacy 课程没有 `syllabus.json` 时，以 `知识表：未建立` 代替进度与六态；新布局缺 `_lathe/knowledge-points.md` 时显示明确错误。不要读取或依赖 metadata 中的任何废弃点级字段，也不要用 research 的历史镜像补数。
   - 部分列表来自当前布局 metadata 的 `parts` 数组，各部分标题按第 2 步的取标题优先级获得。文件名含 `-review` 后缀的在标题后标注 *（复习）*。
   - 若验证结果含逐部分明细（`parts` 数组，**每条按 `part` 字段匹配文件名、按 `status` 字段取状态**），在对应部分后按下表标注：

     | `status` | 显示 |
     |---|---|
     | `passed` | `✅ passed` |
     | `failed` | `❌ failed`（附 `failed_step`） |
     | `skipped` | `⏭️ skipped`（附 `reason`） |
     | `not_run` | `⏭️ not_run` |
     | `not_applicable` | `—（复习材料不参与验证）`，不算未验证 |

     若该部分为 `passed` 但内容已变更（part mtime 晚于 `checked_at`），改标 `⚠️ 内容已变更，需重新验证`。
     **条目里带 `historical_steps` 时另加一句**：`其中 N 组检查点已按 changed_interfaces.supersedes 记为历史预期`（如 `part-01.md#3`）——被登记作废的检查点组是「跳过的」而不是「跑过的」，不显示出来读者会以为整部分干净通过。`fixes` 非空时附一句「验证中做过 N 处修正」。
   - `status` 为 `completed` 的课程，在状态列显示 `⭐ completed（已完结）`。
   - **验证中断检测：** 当前布局 verify result 的 `status` 为 `verifying` 且 `checked_at` 超过 **6 小时**前，说明上次验证中途中断。标注为 `⚠️ 验证可能中断（停留于 <checked_at>）` 并提示重新运行 `/lathe 验证 <slug>` 即可复位（增量复用会从断点继续）。
6. **metadata 缺失的教程**单独列为一组，逐条标注 *⚠️ metadata 缺失*（附目录位置与发现的根目录 part 文件数）。只读操作不猜布局、不重建；提示运行 `/lathe 标签 <slug>` 或任一写入型操作，按 `<SKILL_DIR>/references/metadata.md` 的布局线索与自愈协议确认重建位置。**混合布局冲突另列一组**，展示冲突路径并提示先人工确认应保留的布局；本操作不移动、迁移或删除任何辅助文件。

7. **悬空与未登记提示。** 枚举时附带检查两类异常，各用一句话告知（**只提示，不写入**）：
   - `tutorial_paths` 中有条目指向的 `<目录>/<slug>/` 已不存在 → *⚠️ config 中有 N 个悬空条目*；
   - 某目录下发现了教程但它不在 `tutorial_paths` 中（仅因落在 `tutorials_base_path` 而被看到）→ *⚠️ N 个教程尚未登记*。

   两者都提示：运行 `/lathe 扫描` 可以登记、校正路径并清理悬空条目。**尤其当用户报告“有教程没显示出来”时，首先建议 `/lathe 扫描`**——教程被手工拷贝、克隆或移动后就处于这种不可见状态，而本操作无权修复它。

8. **结尾给出总览一句话**：共几门语言、几门课程、几个部分，多少课程尚未验证，以及多少教程 metadata 缺失、多少混合布局冲突（如有）。末尾附上一行 **技能版本：`v<SKILL.md frontmatter 的 version>`**，方便用户确认当前运行的是哪个 Lathe 版本。

9. **目录为空或不存在时**：告诉用户还没有教程，提示用 `/lathe <主题>` 生成第一个；若用户认为应该有教程，提示 `/lathe 扫描 <目录>` 去找回来。

### 带 slug：`/lathe list <slug>` 或 `/lathe 列表 <slug>`

1. **定位、判定布局并读取。** 按 `<SKILL_DIR>/SKILL.md`“教程位置与双布局”找到该教程根目录，先按无参数分支第 2 步检查两处 metadata 与混放辅助文件；布局正常时只读取当前布局的 metadata、canonical ledger 和 verify result。slug 不存在时列出 config 中已知的全部 slug 及其位置供用户选择，并提示 `/lathe 扫描` 可登记未被识别的教程。**metadata 缺失但目录存在时**，按 `<SKILL_DIR>/references/metadata.md` 的自愈规则只展示布局线索与可推断信息并建议重建；混合布局只报告冲突，不跨布局读取。同样**不读取 part 全文**，取标题按无参数分支第 2 步的优先级。
2. **展示详细状态**：
   - 标题、主题、编程语言、创建时间、正文语言、voice、模型、所在目录；
   - 学习目标（`goal`）、读者水平（`experience_level`）、风格锚点（`style_anchor`）、生成版本（`lathe_version`）——字段存在时展示，缺失则省略（不推断、不写入）；
   - `parts` 列表（逐个文件名，附各部分的一级标题和逐部分验证结果；逐部分状态按无参数分支第 2 步的“内容变更检测”规则展示）；
   - 标签、来源数量；
   - 仓库/分支/本地项目路径/锁定工具版本（如有）；
   - 验证结果：状态、时间，若失败则给出失败的部分、步骤和错误信息；若为陈旧的 `verifying` 按无参数分支第 5 步标注中断；
   - `continuity` 存在时，用一行说明连续性摘要的新鲜度（`updated_through` 是否跟上最后一个常规部分）——落后时提醒：下次续写会先重建摘要（一次性成本）。
   - 展示活跃 `changed_interfaces` 数量、`continuity.open_threads` 数量；当前布局 research 存在时只注明“有归档”，不把其中旧的点级镜像当状态来源。
   - **知识点与进度**：从当前布局 canonical ledger 的数据行计算并显示 `进度：taught a / 计划内 d（p%）` 与 `六态：planned · queued · taught · self-study · dropped_by_user · duplicate（共 n 条）`。新布局缺 `_lathe/knowledge-points.md` 显示错误；legacy 缺 `syllabus.json` 显示 `知识表：未建立`。不得从 metadata 点级废弃字段或 research 历史小节补齐、对账或推断。
3. **给出下一步建议**：根据状态提示可用操作（如 `unverified` → 提示可 `/lathe 验证 <slug>`；canonical ledger 有到期承诺、`queued` 或当前 `planned` → 提示可 `/lathe 续写 <slug>`；久未学习 → 提示可 `/lathe 复习 <slug>`；目标已达成 → 提示可 `/lathe 续写 收尾 <slug>` 完结；`completed` → 说明已完结，续写可重新开放）。续写优先级只引用 canonical ledger。

## 边界

- **不写入任何文件。** 纯展示操作——包括对 metadata 缺失的教程、悬空条目和未登记教程：只标注和建议，实际修复由用户发起 `/lathe 扫描` 或其他写入型操作时执行。
- 不修改任一布局的 metadata、canonical ledger、research、verify result、`~/.lathe/config.json` 或任何部分文件。
- **不读取 `part-NN.md` 全文**——只取一级标题（优先用当前布局 metadata 的 `continuity.part_titles`，否则 `grep -m1 '^# '`）。
- 展示后保持会话，用户往往接着发起续写/验证等操作。
