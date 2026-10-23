# 列出教程

列出所有已存储的教程，或查看单个教程的详细状态。用户忘记 slug、想了解整体进度、或想确认某教程验证结果时使用。

本操作**完全只读**：不写入、不修改任何文件。

## 协议

### 无参数：`/lathe list` 或 `/lathe 列表`

1. **多路径枚举教程目录。** 解析 `~/.lathe/config.json`，取所有基础目录的并集（`tutorial_paths` 各值 + `tutorials_base_path`，去重）；在每个目录下列出含 `metadata.json` 的子目录（跳过 `voices/` 等非教程目录；**跳过以 `.` 开头的隐藏目录**——如验证工作区 `.lathe-verify/`）。另将**有 `part-*.md` 但缺 `metadata.json`** 的子目录识别为 metadata 缺失的教程（见第 6 步）。同一 slug 出现在多个目录时全部列出并在位置列标注，提醒用户存在副本。

2. **读取每个教程的 `metadata.json`**，如存在则同时读取 `verify-result.json`。

   > **内容变更检测：** 若某 part 在 `verify-result.json` 中为 `passed`，但该 part 文件的修改时间晚于 `checked_at`，在列表中标记为 **“内容已变更，需重新验证”**，不要继续显示 `passed`。只取文件 mtime，不读正文；`-review` 复习材料不参与；“增量复用跳过”（`skipped_reuse`）同样按此判断。`checked_at` 缺失时跳过本检测。若 `verify-result.json` 的 `changed_interfaces_snapshot` 与当前 `metadata.changed_interfaces` 不一致，也标记 **“接口已变更，需重新验证”**。

   > **成本约束（重要）：本操作绝不读取 `part-NN.md` 的全文。** 一个多课程目录的正文动辄数十万字符，而列表只需要每个部分的一级标题。按以下优先级取标题：
   > 1. **`metadata.json` 的 `continuity.part_titles`** —— 已有映射则直接用，零文件读取；
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
   部分（<N>）：
   1. part-01.md — <该部分的一级标题>
   2. part-02.md — <该部分的一级标题>
   3. part-03.md — <该部分的一级标题>
   ```

   - 部分列表来自 `metadata.json` 的 `parts` 数组，各部分标题按第 2 步的取标题优先级获得。文件名含 `-review` 后缀的在标题后标注 *（复习）*。
   - 若验证结果含逐部分明细（`parts` 数组），在对应部分后标注 `✅ passed` / `❌ failed` / `⏭️ skipped` / `⏭️ not_run`（`-review` 复习材料不参与验证，无标注）。若该部分为 `passed` 但内容已变更（part mtime 晚于 `checked_at`），改标 `⚠️ 内容已变更，需重新验证`。
   - `status` 为 `completed` 的课程，在状态列显示 `⭐ completed（已完结）`。
   - **验证中断检测：** `verify-result.json` 的 `status` 为 `verifying` 且 `checked_at` 超过 **6 小时**前，说明上次验证中途中断。标注为 `⚠️ 验证可能中断（停留于 <checked_at>）` 并提示重新运行 `/lathe 验证 <slug>` 即可复位（增量复用会从断点继续）。
6. **metadata 缺失的教程**单独列为一组，逐条标注 *⚠️ metadata 缺失*（附目录位置与发现的 part 文件数），并提示：运行 `/lathe 标签 <slug>` 或任一写入型操作可按 `<SKILL_DIR>/references/metadata.md`"metadata.json 自愈"重建索引。

7. **悬空与未登记提示。** 枚举时附带检查两类异常，各用一句话告知（**只提示，不写入**）：
   - `tutorial_paths` 中有条目指向的 `<目录>/<slug>/` 已不存在 → *⚠️ config 中有 N 个悬空条目*；
   - 某目录下发现了教程但它不在 `tutorial_paths` 中（仅因落在 `tutorials_base_path` 而被看到）→ *⚠️ N 个教程尚未登记*。

   两者都提示：运行 `/lathe 扫描` 可以登记、校正路径并清理悬空条目。**尤其当用户报告“有教程没显示出来”时，首先建议 `/lathe 扫描`**——教程被手工拷贝、克隆或移动后就处于这种不可见状态，而本操作无权修复它。

8. **结尾给出总览一句话**：共几门语言、几门课程、几个部分，多少课程尚未验证，以及多少教程 metadata 缺失（如有）。末尾附上一行 **技能版本：`v<SKILL.md frontmatter 的 version>`**，方便用户确认当前运行的是哪个 Lathe 版本。

9. **目录为空或不存在时**：告诉用户还没有教程，提示用 `/lathe <主题>` 生成第一个；若用户认为应该有教程，提示 `/lathe 扫描 <目录>` 去找回来。

### 带 slug：`/lathe list <slug>` 或 `/lathe 列表 <slug>`

1. **定位并读取。** 按 `<SKILL_DIR>/SKILL.md`"教程位置解析规则"找到该教程目录，读取 `metadata.json` 和 `verify-result.json`（如存在）。slug 不存在时列出 config 中已知的全部 slug 及其位置供用户选择，并提示 `/lathe 扫描` 可登记未被识别的教程。**metadata 缺失但目录存在时**，按 `<SKILL_DIR>/references/metadata.md`"metadata.json 自愈"展示可推断的信息并建议重建。同样**不读取 part 全文**，取标题按无参数分支第 2 步的优先级。
2. **展示详细状态**：
   - 标题、主题、编程语言、创建时间、正文语言、voice、模型、所在目录；
   - 学习目标（`goal`）、读者水平（`experience_level`）、风格锚点（`style_anchor`）、生成版本（`lathe_version`）——字段存在时展示，缺失则省略（不推断、不写入）；
   - `parts` 列表（逐个文件名，附各部分的一级标题和逐部分验证结果；逐部分状态按无参数分支第 2 步的“内容变更检测”规则展示）；
   - 标签、来源数量；
   - 仓库/分支/本地项目路径/锁定工具版本（如有）；
   - 验证结果：状态、时间，若失败则给出失败的部分、步骤和错误信息；若为陈旧的 `verifying` 按无参数分支第 5 步标注中断；
   - `continuity` 存在时，用一行说明连续性摘要的新鲜度（`updated_through` 是否跟上最后一个常规部分）——落后时提醒：下次续写会先重建摘要（一次性成本）。
   - 展示活跃 `changed_interfaces` 数量、`continuity.open_threads` 数量；教程目录存在 `research.md` 时注明“有归档”（只检查存在性，不读内容）。
3. **给出下一步建议**：根据状态提示可用操作（如 `unverified` → 提示可 `/lathe 验证 <slug>`；上一部分"接下来"有未决问题 → 提示可 `/lathe 续写 <slug>`；久未学习 → 提示可 `/lathe 复习 <slug>`；目标已达成 → 提示可 `/lathe 续写 收尾 <slug>` 完结；`completed` → 说明已完结，续写可重新开放）。

## 边界

- **不写入任何文件。** 纯展示操作——包括对 metadata 缺失的教程、悬空条目和未登记教程：只标注和建议，实际修复由用户发起 `/lathe 扫描` 或其他写入型操作时执行。
- 不修改 `metadata.json`、`verify-result.json`、`~/.lathe/config.json` 或任何部分文件。
- **不读取 `part-NN.md` 全文**——只取一级标题（优先用 `continuity.part_titles`，否则 `grep -m1 '^# '`）。
- 展示后保持会话，用户往往接着发起续写/验证等操作。
