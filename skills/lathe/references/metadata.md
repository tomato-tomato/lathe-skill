---
name: metadata
description: Lathe metadata.json 完整结构、字段语义、continuity 摘要规范与自愈协议
---

# metadata.json 规范

本文件是 `metadata.json` **完整结构与自愈协议**的单一事实源。SKILL.md 只保留字段速查与 status 状态机。

**何时读取本文件：**

| 场景 | 是否需要 |
|------|----------|
| 新建 metadata（**生成**） | ❌ **不读**——`generate.md`"写完之后"已内联 JSON 骨架与字段表 |
| 新建 metadata（扫描登记、自愈重建） | ✅ 必读 |
| 写入 `continuity` 摘要、`course_plan` 或 `changed_interfaces`（续写、收尾） | ✅ 必读 |
| 只读取几个已知字段（提问、列表、验证、标签） | ❌ 按字段名直接读 JSON 即可 |

---

## 完整结构

```json
{
  "_warning": "⚠️ 本文件是该教程的索引文件，请勿删除。误删后 lathe 将无法识别此教程；可运行 /lathe 标签 <slug> 或任一写入型操作触发自愈重建。",
  "_needs_backfill": [],
  "lathe_version": "<当前技能版本，如 0.5.4>",
  "slug": "<kebab-case 短名称>",
  "title": "<教程标题>",
  "topic": "<用户的原始主题描述>",
  "goal": "<学习目标：生成时与用户确认；旧教程缺失时由首次续写推断补上>",
  "created": "<ISO 8601 时间戳>",
  "status": "unverified",
  "tags": ["<标签1>", "<标签2>"],
  "parts": ["part-01.md"],
  "language": "<教程正文语言，如 zh-CN、en>",
  "experience_level": "beginner | familiar | experienced",
  "topic_novelty": "new | adjacent | familiar",
  "course_plan": [
    {"part": 1, "title": "<部分标题>", "goal": "<该部分的一句话目标>", "prerequisites": ["<前置概念/工具>"]}
  ],
  "changed_interfaces": [
    {
      "file": "<文件路径>",
      "symbol": "<文件内符号>",
      "from": "<旧签名/旧契约>",
      "to": "<新签名/新契约>",
      "call_sites": ["<需要更新的调用点>"],
      "part": "part-NN.md"
    }
  ],
  "style_anchor": "<主锚点作者 id，如 nystrom>",
  "repo": "<远程 URL 或空>",
  "repo_branch": "<分支或空>",
  "local_project_path": "<本地项目路径或空>",
  "tools": [{"name": "<工具>", "version": "<版本>"}],
  "sources": ["<url1>", "<url2>"],
  "voice": "plainspoken",
  "model": "<AI 模型名称，如 QoderWork>",
  "continuity": {
    "controlling_example": "<贯穿全课程的控制性示例，一句话>",
    "fixed_numbers": {"<名称>": "<值>"},
    "metaphor": "<控制性隐喻，无则空字符串>",
    "metaphor_retired": false,
    "covered_concepts": ["<已讲透的概念1>", "<概念2>"],
    "open_threads": ["<已提出但未展开的问题/伏笔>"],
    "next_hook": "<最后一个部分 ## 接下来 指向的方向，一到两句>",
    "part_titles": {"part-01.md": "<一级标题>"},
    "updated_at": "<ISO 8601 时间戳>",
    "updated_through": "part-NN.md"
  },
  "verify_workspace": {
    "path": ".lathe-verify/",
    "note": "📦 教程验证工作区：/lathe 验证 在此目录中执行教程代码，并在再次验证时增量复用（不重新生成已有代码）。可以安全删除，下次验证会自动重建。"
  }
}
```

---

## 字段说明

| 字段 | 写入方 | 说明 |
|------|--------|------|
| `_warning` | 所有写入方保留 | 给用户的防误删提醒；技能读取时忽略其内容。JSON 不支持注释，故用此字段承载。旧教程缺少时在下次写回补上 |
| `_needs_backfill` | 自愈/旧教程写回时 | 无法可靠推断、需要人工补的字段名数组（如 `changed_interfaces`、`open_threads_archive`）；补上后从数组移除。生成时写 `[]` |
| `lathe_version` | 每次写回时更新为当前技能版本 | 生成/续写该教程时所用的 Lathe 版本，便于排查版本相关差异 |
| `goal` | 生成时确认 | 可评估的一句话学习目标。是"目标达成回顾"与收尾完结的判定基准 |
| `experience_level` | 生成时询问 | 三档枚举，驱动"概念锚定"的类比深度（见 writing-core.md）。**续写读取，不重新询问** |
| `topic_novelty` | 生成时确认（可按 `experience_level` 推断） | 三档枚举，驱动配额矩阵（检索预算、地基章节、标注、概念锚定）。**续写读取，不重新询问**；缺失时按 `sources` / `covered_concepts` 覆盖度推断，默认 `adjacent` |
| `course_plan` | 生成时初始化；续写时维护 | 3-12 项课程路线图，每项 `{part, title, goal, prerequisites}`。part-01 完成第 1 项；续写优先按下一项推进，用户指导可覆盖。**它是 metadata 字段，不是 `index.md`** |
| `changed_interfaces` | 生成时初始化/写入；续写时维护 | 跨部分活跃接口变更清单；按符号记录，最多 8 条；字段 `file` / `symbol` / `from` / `to` / `call_sites` / `part`；超出或同符号被替代时归档到 `research.md`。无变化时为空数组 |
| `style_anchor` | 生成时选定 | 风格标杆主锚点 id。续写沿用，避免重复加载 style-benchmarks.md |
| `continuity` | 续写/收尾每次更新 | **续写连续性摘要**，见下方专节 |
| `local_project_path` | 续写时填写 | 已有值时续写只做确认，不从零询问 |
| `verify_workspace` | verify 首次创建工作区时 | 向用户说明 `.lathe-verify/` 的作用 |

> 旧教程的 metadata 可能含有已废弃的 `pending_part` 字段——读取时忽略，写回时不必保留。

**向后兼容原则：** 所有字段缺失都必须可降级运行，绝不因缺字段而中止操作。缺失字段按各自规则推断，并在**本次写回时补上**（一次补齐，不反复询问用户）。

---

## continuity 摘要（续写的上下文来源）

`continuity` 存在的唯一目的：让续写**不必重读全部历史部分**。教程越长收益越大。

**读取契约（续写/收尾/复习）：**

- `continuity` 存在且 `updated_through` 等于当前最后一个常规部分 → **可信**。只需读它 + 最后 1 个部分全文即可动笔。
- **信任前先做手工编辑检测：** 用文件 mtime 扫描所有 part；任何 part 的 mtime 晚于 `continuity.updated_at`，视为手工改动，按“重建”处理。该检测只取 mtime，不读正文；文件被复制导致 mtime 变新时宁可重建一次。
- **每 3 个常规部分做一次全读审计：** 当本次要写的部分编号是 3 的倍数（part-03 / part-06 / part-09…）时，即使 continuity 可信，也读取全部常规部分，核对并重建 continuity。长课程不能只靠摘要连续漂移。
- `continuity` 缺失、或 `updated_through` 落后于实际最后部分（说明中途有过手工编辑或跨版本） → **重建**：读取全部部分并重新提炼，本次写回时补上。
- 用户明确表示改过旧部分内容 → 同样重建。
- 若 `changed_interfaces` 非空，续写涉及接口/调用点的旧 part 时必须读取对应旧 part；若 `open_threads` 提到旧 part，也读取该 part 的相关小节。

**字段语义：**

| 字段 | 含义 |
|------|------|
| `controlling_example` | 贯穿全课程的具体产物（如"名为 `pebble` 的键值存储，能在 `kill -9` 后存活"）。续写必须精确复用，不得替换 |
| `fixed_numbers` | 已锁定的领域数字（采样率、缓冲区大小、端口、超时等）。续写引用同一数字，不得漂移 |
| `metaphor` / `metaphor_retired` | 控制性隐喻及是否已明确告别。已告别则续写不再重启该隐喻 |
| `covered_concepts` | 已讲透的概念清单——续写据此避免重复教学，也是 `[!RECALL]` 的取材池。**只追加、不合并、不删除**，每项 ≤40 字 |
| `open_threads` | 已提出但尚未展开的问题/伏笔（最多 10 条，每条 ≤80 字）——续写优先回收；已解决/溢出时移到 `research.md` 的 `## Open Threads Archive`，不删除 |
| `next_hook` | 最后一部分"接下来"指向的方向——这就是下次续写的默认任务（≤200 字） |
| `part_titles` | 文件名 → 一级标题映射。让 list、复习、收尾无需打开文件即可获得标题 |
| `updated_through` | 摘要覆盖到哪个部分——新鲜度判定依据 |
| `updated_at` | 最后一次写回 continuity 的时间；也用于 part mtime 的手工编辑检测。必须在所有 part 写入之后刷新；verify 只改状态横幅时也会刷新，正文修改时不刷新 |

**写入契约：** 每次写入新部分后**增量更新**——追加本部分新增的概念与数字、更新 `open_threads`、覆盖 `next_hook`、更新 `part_titles`、`updated_through`、`updated_at`。不要重写已有条目（除非确实变更）。摘要总量控制在 **1200 字软上限 / 2000 字硬上限**；分字段上限：`controlling_example` ≤200 字、`next_hook` ≤200 字、`covered_concepts` 每项 ≤40 字、`fixed_numbers` 每个值 ≤40 字、`open_threads` 每条 ≤80 字。**宁可多存 200 字，也不要让下次续写重读全部部分。** 若 `covered_concepts` 本身已接近硬上限，优先把不再被 `[!RECALL]` / 续写引用的旧概念归档到可选 `research.md`，而不是删除或合并它们。它是索引，不是缩写版教程。

`open_threads` 超过 10 条，或某个线程已经解决/不再需要跟进时，移动到 `research.md` 的 `## Open Threads Archive`；归档条目写清楚：问题、提出部分、状态（resolved / deferred / superseded）、解决部分（如有）、备注/来源。**归档不是删除**；续写/复习/收尾在需要时可读取相关小节。

---

## changed_interfaces（跨部分接口变更）

`changed_interfaces` 是跨部分活跃接口变更清单，不是课程正文，也不是 API 文档的替代品。

- **何时写入：** 修改现有公开 API/签名、导出类型、数据库 schema、配置契约，或任何跨文件接口时。
- **粒度：** 按符号一条；同一文件多个符号就多条。
- **字段：** `file`、`symbol`、`from`、`to`、`call_sites`、`part`。`from`/`to` 用一行签名或短契约描述；`call_sites` 列出需要跟着改的文件/符号，已确认无需外部改动时写 `[]`，并在 part 的改动面表说明理由。
- **上限：** 活跃 8 条。超过时，优先归档已解决/被替代的条目；仍有活跃溢出时，归档最早条目，并在 `research.md` 标记 `active (overflow)`；续写/验证涉及该符号时读取归档。
- **替代关系：** 同一符号只保留最新一条活跃条目；旧条目归档，并注明 `superseded by <part>`。
- **读取：** 续写写之前读活跃条目；若本部分涉及已归档接口，读 `research.md` 的相关小节。验证把活跃条目当检查表，逐条核对调用点；不做自动签名推断。
- **无变化：** 写 `[]`。旧教程缺失视为空，不强行回填。

### research.md（可选归档文件）

当 `changed_interfaces` 超出活跃上限、同一符号被替代，或 `open_threads` 已解决/溢出时，在教程目录创建或追加 `research.md`，使用两个固定小节：

```markdown
## Changed Interfaces Archive

### <symbol>（<part>）
- 文件：`<file>`
- 变化：`<from>` → `<to>`
- 调用点：`<call sites>`
- 状态：archived / superseded by <part> / active (overflow)

## Open Threads Archive

### <简短标题>
- 提出于：`part-NN`
- 状态：resolved / deferred / superseded
- 解决于：`part-NN`（如已解决）
- 问题：<原问题>
- 备注/来源：<可选>
```

归档文件不是必需的；没有需要归档的内容时不要创建。`research.md` 也不替代 `metadata.json` 的活跃清单。

---

## course_plan（课程路线图）

`course_plan` 是 3-12 项的数组，每项一句话，给生成和续写定边界。结构示例只列 1 项；实际写 **3-12 项**。它**不是 `index.md`**，不产生额外文件。

- **生成时：** 在写 part-01 之前初始化；part-01 完成第 1 项。
- **续写时：** 优先按下一项推进；用户指导可覆盖，此时更新路线图。
- **旧教程缺失时：** 首次续写从 `next_hook` / `part_titles` 补一份 3-12 项路线图，写入本次 metadata。
- **收尾时：** 保留已走路线，不删除；它不是完成度判定依据（`goal` 才是）。

---

## metadata.json 自愈

`metadata.json` 是教程的索引，但教程正文（`part-NN.md`）本身携带了重建它所需的全部信息。任何操作发现某教程目录**有 `part-*.md` 但 `metadata.json` 缺失或损坏**（JSON 解析失败）时：

1. **确定部分范围：** 按文件名列出该目录的 `part-NN.md` → `parts` 数组（含 `-review` 后缀的复习材料）。
2. **逐字段推断：**
   - `slug` → 目录名；`title` → part-01 的一级标题；
   - `language` → 正文实际语言；`tags` → 从标题与正文主题推断 2-5 个（语言/领域/技术）；
   - `tools` → 从前置条件章节与配置代码块（如 `Cargo.toml`、`go.mod`）推断工具名与版本，无法确定的版本标注 `[!UNVERIFIED]`；
   - `sources` → 提取各部分 `## 来源` 小节中的 URL（去重）；
   - `created` → 各部分文件中最早的文件修改时间；
   - `goal` → 从 part-01 的 `## 你将构建什么` 与整体走向提炼一句；
   - `experience_level` → 从正文类比深度推断；`topic_novelty` → 按 `sources` / `covered_concepts` 覆盖度推断，默认 `adjacent`；`style_anchor` → 从写作节奏推断；
   - `course_plan` → 从 `parts`、各部分一级标题与"接下来"提炼 3-12 项；无法提炼时留空数组；
   - `changed_interfaces` → 空数组；旧教程的接口变更无法可靠推断，不强行回填；
   - `_needs_backfill` → 记录 `changed_interfaces`、`open_threads_archive` 等无法可靠推断的字段；用户补上后从数组移除；
   - `continuity` → 按上方字段语义从正文提炼（含 `open_threads`，从各部分"接下来"的未决问题提取；归档内容无法可靠推断，留空）；
   - `voice` → 默认 `plainspoken`（正文不可判定）；`status` → `unverified`；
   - `lathe_version` → 当前技能版本；
   - `repo`、`local_project_path` → 正文有线索则填，否则留空。
3. **确认后写入：** 向用户展示重建结果（明确标注哪些字段为推断值）。对 `changed_interfaces`、`open_threads` 归档等无法可靠推断的字段，写入 `_needs_backfill` 数组并在报告中标注“待人工补”，不要静默当空。用户确认后写入 `metadata.json`（含顶部的 `_warning` 字段），并在 `~/.lathe/config.json` 的 `tutorial_paths` 中登记该教程位置。
4. **只读操作不写入：** `list` 将此类教程标注为 *⚠️ metadata 缺失* 并建议运行修复；`ask` 基于部分文件直接回答并顺带提醒。

用户拒绝重建时，相关写入型操作（续写/验证/打标签）终止并说明原因；不要在没有索引的情况下修改教程文件。

**自愈是唯一允许跨越"仅改本字段"边界的场景**——标签、验证等操作在自愈时可写入完整 metadata，因为不重建索引就无法继续。
