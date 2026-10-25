---
name: metadata
description: Lathe metadata.json 完整结构、字段语义、continuity 摘要规范与自愈协议（账本规范见 knowledge-ledger.md）
---

# metadata.json 规范

本文件是 `metadata.json` **完整结构与自愈协议**的单一事实源；知识点账本 `syllabus.json` 的规范在 `knowledge-ledger.md`。SKILL.md 只保留字段速查与 status 状态机。

**何时读取本文件：**

| 场景 | 是否需要 |
|------|----------|
| 新建 metadata 与账本（**生成**） | ❌ **不读**——`generate.md`"写完之后"已内联 JSON 骨架与字段表 |
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
      "supersedes": ["<被本变更作废的旧检查点，如 part-01.md#3>"],
      "part": "part-NN.md"
    }
  ],
  "knowledge_backlog": [
    {
      "id": "<原文编号，如 3a>",
      "text": "<归一化后的知识点，≤60 字>",
      "from": "<来源，如 user-list-2026-10-23>",
      "plan_ref": 3,
      "priority": "core",
      "merged_ids": []
    }
  ],
  "part_versions": {
    "part-01.md": "0.6.0",
    "part-02.md": "0.6.0"
  },
  "syllabus_ids": ["<syllabus.json 中出现过的全部 id，按字母序>"],
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
    "exercise_carry": {"integrated": [], "chapter": [], "deferred": []},
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
| `changed_interfaces` | 生成时初始化/写入；续写时维护 | 跨部分活跃接口变更清单；按符号记录，最多 8 条；字段 `file` / `symbol` / `from` / `to` / `call_sites` / `supersedes` / `part`；超出或同符号被替代时归档到 `research.md`。无变化时为空数组 |
| `knowledge_backlog` | 生成时初始化；续写时维护 | 账本 `queued` 条目的投影（以 `syllabus.json` 为准）：已承诺要讲、被名额挤出的知识点队列。每项 `{id, text, from, plan_ref, priority, merged_ids}`；最多 14 条（闸门选 ① 时按新增 Part 上调）、`text` ≤60 字、`priority` 固定 `core`（自学条目只在 `research.md`）、`merged_ids` 可省略。先进先出，讲完从数组移除（账本里记 `taught`）。无内容写 `[]`；旧数据里 `priority: "self-study"` 的条目下次写回时迁到 `## Self-study Backlog`。来源、闸门、去重规则见 knowledge-ledger.md |
| `part_versions` | 每次写一个部分时更新 | **逐部分的写入版本**：键是 `part-NN.md`，值是当时写它用的技能版本（如 `0.5.5` / `0.6.0`）。旧教程被新版本续写一次后，教程级 `lathe_version` 会升到新版、丢掉「哪部分是旧的」这个信息；`part_lint.py` / `ledger_check.py` 靠它把「0.6.0 之后新增的约束」对历史部分自动降级（历史部分也不参与交付自检）。缺失时回落到 `lathe_version`；不要求回填旧数据 |
| `syllabus_ids` | 生成时初始化；每次写账本时同步 | 账本 ID 镜像：`syllabus.json` 出现过的全部 `id`，按字母序、只增不删，用来发现被整条删掉的账本条目（knowledge-ledger.md 不变量 6）。旧教程在建账本那次写回补上 |
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
| `covered_concepts` | 已讲透的概念清单——续写据此避免重复教学，也是 `[!RECALL]` 的取材池。**只追加、不合并、不删除**，每项 ≤40 字，**索引里只留最近 24 条**（更旧的归档，仍算已讲） |
| `open_threads` | 已提出但尚未展开的问题/伏笔（**最多 8 条**，每条 ≤80 字）——续写优先回收；已解决/溢出时移到 `research.md` 的 `## Open Threads Archive`，不删除 |
| `exercise_carry` | 本部分练习的承接分流结果（0.6.0 新增）：`{integrated: [], chapter: [], deferred: []}`，各 ≤3 条、每条 ≤40 字。`integrated` = 已融进某条知识点；`chapter` = 已进承接章节；`deferred` = 顺延（同时进 `knowledge_backlog`）。续写读它决定下一部分怎么接；讲透后从对应数组移除并追加进 `covered_concepts` |
| `next_hook` | 最后一部分"接下来"指向的方向——这就是下次续写的默认任务（≤200 字） |
| `part_titles` | 文件名 → 一级标题映射。让 list、复习、收尾无需打开文件即可获得标题 |
| `updated_through` | 摘要覆盖到哪个部分——新鲜度判定依据 |
| `updated_at` | 最后一次写回 continuity 的时间；也用于 part mtime 的手工编辑检测。必须在所有 part 写入之后刷新；verify 只改状态横幅时也会刷新，正文修改时不刷新 |

**写入契约：** 每次写入新部分后**增量更新**——追加本部分新增的概念与数字、更新 `open_threads`、**覆盖 `exercise_carry` 为本部分练习的分流结果**（**收尾例外**：总结部分没有练习，`exercise_carry` / `covered_concepts` / `fixed_numbers` 一律原样保留，覆盖会把仅存的承诺记录清空——见 extend.md 收尾步骤 5）、覆盖 `next_hook`、更新 `part_titles`、`updated_through`、`updated_at`。不要重写已有条目（除非确实变更）。**预算必须是可达的**（0.6.0 修正）：旧写法只给「1200 软 / 2000 硬」的总量加「每条 ≤N 字」的单条上限，**却没有限制条数**——而 `covered_concepts` 只增不删，三门课实测就 1969 字、六门课必然越界，等于写了一条不可能遵守的规则（真越界时的风险是回头压缩正文）。现在**先定条数上限，总量等于它们之和**：

| 字段 | 条数上限 | 单条上限 | 超了怎么办 |
|---|---|---|---|
| `covered_concepts` | 索引里留最近 **24 条** | ≤40 字 | 更旧的移到 `research.md` 的 `## Covered Concepts Archive`（**仍算已讲**，不删不合并） |
| `open_threads` | **8 条** | ≤80 字 | 已解决的移到 `## Open Threads Archive` |
| `fixed_numbers` | **18 项** | ≤40 字 | 后续部分不再复用的移到 `## Covered Concepts Archive` 一行说明或直接留在 `research.md` |
| `part_titles` | 最近 **8 个部分** | ≤60 字 | 更早的标题不留（`/lathe 列表` 与复习按 `grep -m1 '^# '` 现取，成本一行命令） |
| `exercise_carry` | 三个数组各 ≤3（合计 9） | ≤40 字 | 已讲透的移除并追加进 `covered_concepts` |
| `controlling_example` / `next_hook` / `metaphor` | 各 1 | ≤200 字 | 精简表述，不缩短正文 |

**总量：软上限 2200 字 / 硬上限 3000 字**（= 上表之和的最大值），这是**索引预算，不是正文预算**。写回 `metadata.json` 后跑 `ledger_check.py <教程目录> --continuity`：它按上表逐字段实测并给出该归档哪几条。**超条数或超软上限都不是失败**（不阻塞交付），超硬上限才必须归档；**两种情况都不得用压缩正文解决**。**宁可多存 200 字，也不要让下次续写重读全部部分**——它是索引，不是缩写版教程。

**`knowledge_backlog` 与 `continuity` 的分工：** `continuity` 是**已发生事实的摘要**（讲透了什么、留了什么伏笔），受 3000 字硬上限约束（且须先守住上面的条数上限）；`knowledge_backlog` 是**尚未发生事项的队列**（还没讲的条目），放顶层、不受 `continuity` 预算约束。**不要把清单塞进 `continuity`**——12 条清单约 500 字，会直接把索引挤爆。

`open_threads` 超过 10 条，或某个线程已经解决/不再需要跟进时，移动到 `research.md` 的 `## Open Threads Archive`；归档条目写清楚：问题、提出部分、状态（resolved / deferred / superseded）、解决部分（如有）、备注/来源。**归档不是删除**；续写/复习/收尾在需要时可读取相关小节。

---

## changed_interfaces（跨部分接口变更）

`changed_interfaces` 是跨部分活跃接口变更清单，不是课程正文，也不是 API 文档的替代品。

- **何时写入：** 修改现有公开 API/签名、导出类型、数据库 schema、配置契约，或任何跨文件接口时。
- **粒度：** 按符号一条；同一文件多个符号就多条。
- **字段：** `file`、`symbol`、`from`、`to`、`call_sites`、`part`。`from`/`to` 用一行签名或短契约描述；`call_sites` 列出需要跟着改的文件/符号，已确认无需外部改动时写 `[]`，并在 part 的改动面表说明理由。
- **`supersedes`（作废旧检查点）：** 可选数组，元素是 `"<part 文件>#<检查点组号>"`（如 `"part-01.md#3"` 指 Part 1 的**检查点 ③**，按正文里加粗的 ①②③ 组号计）。当本次变更会让某个**较早部分**的检查点输出字面失配（返回体形状、状态码、字段增删、错误结构等）时，必须登记；只写不受影响的检查点不要登记。没有影响时省略或写 `[]`。
  - 它只覆盖**检查点命令的预期输出**，不覆盖 `runnable` 代码块。`runnable` 的旧签名由 `verify.md` 的 2b 检查负责，且**只对「变更引入之后」的部分生效**——更早部分的旧签名是历史正确状态，不算失败。
  - 组号必须按正文的加粗序号写（不是 `runnable` 的步骤号）；部分被重排/改号后要复核这些引用。
  - 验证会跳过被登记的检查点组并记为 `historical`（见 `verify.md`），**不算失败**；该部分的既有 `passed` 不被推翻。
- **上限：** 活跃 8 条。超过时，优先归档已解决/被替代的条目；仍有活跃溢出时，归档最早条目，并在 `research.md` 标记 `active (overflow)`；续写/验证涉及该符号时读取归档。
- **替代关系：** 同一符号只保留最新一条活跃条目；旧条目归档，并注明 `superseded by <part>`。
- **读取：** 续写写之前读活跃条目；若本部分涉及已归档接口，读 `research.md` 的相关小节。验证把活跃条目当检查表，逐条核对调用点；不做自动签名推断。
- **无变化：** 写 `[]`。旧教程缺失视为空，不强行回填。

### research.md（可选归档文件）

当 `changed_interfaces` 超出活跃上限、同一符号被替代、`open_threads` 已解决/溢出、`covered_concepts` 接近索引上限、有知识点被降级为自学，或提问（ask）确认了一条勘误时，在教程目录创建或追加 `research.md`。**固定小节共五个，按需出现、顺序如下**（没有内容的小节不必写出）：

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

## Covered Concepts Archive

- <概念>（讲于 `part-NN`，<日期> 从 continuity 归档）

## Self-study Backlog

- **<id>** <知识点>（来自 <part-NN> 的用户清单 / 练习，<日期> 降级；原因：<闸门选 ② / 收尾门禁>）

## Errata

- <日期> `part-NN` §<章节>：<原文要点> → <修正后>（原因：<一句话>；处理：原地修正 / 只记勘误，见 part-MM 回指；影响面：<file:行 逗号分隔，含 -review 材料、interview.md、syllabus.json 的 at>）
```

**`## Covered Concepts Archive` 的语义：** `covered_concepts` 接近索引硬上限时，把不再被 `[!RECALL]` / 续写引用的旧概念移到这里；**它们仍算已讲**，复习、收尾、去重都要读这一节。

**`## Self-study Backlog` 的语义（0.6.0 新增）：** 只有用户在闸门里**显式选 ②**、或收尾门禁里显式选择降级的条目才放这里，**必须保留原 ID**（复习与收尾按 ID 列出）。**教程不承诺讲它们**，但内容留档；用户想捡回来时说「把自学清单里的 X、Y 讲掉」即可按原 ID 重新入队。它不是 `knowledge_backlog` 的副本——同一条只能出现在一边。

**归档条目的写法规范（0.6.0 第二批）——这四条是硬要求，因为复习与收尾要把这些节当「覆盖核对」的输入：**

- **一条一个条目，禁止合写。** `## Open Threads Archive` 里每条独占一个 `### <简短标题>` 块，`提出于` / `解决于` **各自只能写一个具体部分**（`part-NN`）。像「解决于 part-02（前两条）/ part-03（后三条）」「同上」这种**按列表位置或合写的指代一律不允许**——条目顺序一变就完全无法定位，也无法判断某条到底解没解决。
- **状态与解决部分必须同时存在。** `状态：resolved` 就必须有 `解决于：part-NN`；`deferred` / `superseded` 就写 `解决于：—` 并在 `备注/来源` 说明去向。
- **`## Covered Concepts Archive` 只收概念名。** 一行一个：`- <概念>（讲于 part-NN，<日期> 从 continuity 归档）`。**未决线索、带状态的改造项、边界讨论不得混进这一节**（它们属于 `## Open Threads Archive`）——这一节是「讲过什么」的证据池，混进去会让复习把未讲的东西算成已覆盖。
- **读旧格式要容错。** 复习、收尾读到不符合上述写法的归档（合写、缺 `解决于`、概念节里有状态），**不采信它的解决结论**：改读 `continuity.open_threads` 与各部分正文的「本部分不覆盖」，并在结果里一句提示「归档条目无法定位，按正文重建结论」。旧归档不要求迁移，也不得为了「修好它」去改写旧部分。

**`## Errata` 的语义：** 提问（ask）发现教程有误、经用户确认后的处理记录（无论原地修正还是只记勘误）。续写时读它：「只记勘误」的条目要在下一部分的 `> [!RECALL]` 或相关章节用一句话更正。**`影响面` 是必填项**——同一个错误通常同时存在于教学部分正文、`runnable` 代码注释、复习材料与账本 `at`，漏记就会留下互相矛盾的副本。

归档文件不是必需的；没有需要归档的内容时不要创建。`research.md` 也不替代 `metadata.json` 的活跃清单。

---

## course_plan（课程路线图）

`course_plan` 是 3-12 项的数组，每项一句话，给生成和续写定边界。结构示例只列 1 项；实际写 **3-12 项**。它**不是 `index.md`**，不产生额外文件。

- **生成时：** 在写 part-01 之前初始化；part-01 完成第 1 项。
- **续写时：** 优先按下一项推进；写前核对最后一部分的“下一部分起始状态”，确认本部分接得上；用户指导可覆盖，此时更新路线图并说明偏离原因。
- **旧教程缺失时：** 首次续写从 `next_hook` / `part_titles` 补一份 3-12 项路线图，写入本次 metadata。
- **收尾时：** 保留已走路线，不删除；它不是完成度判定依据（`goal` 才是）。

---

## syllabus.json（知识点账本）

结构、书写格式、六种状态、不变量（含 `syllabus_ids` ID 镜像）、读写分工、旧教程回填与损坏恢复，统一见 `<SKILL_DIR>/references/knowledge-ledger.md`「1. 账本」。本文件只负责 `metadata.json` 里与它相关的三个字段：`knowledge_backlog`（`queued` 的投影）、`syllabus_ids`（ID 镜像）与 `part_versions`（逐部分的写入版本）。

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
   - `knowledge_backlog` → **若 `syllabus.json` 存在且可解析，按其中 `status: queued` 的条目重建**（这是账本独立成文件的主要收益）；账本也不存在时写空数组（未讲的知识点无法从正文可靠推断；若某部分「本部分不覆盖」里点名了顺延条目，可作为线索列出并写入 `_needs_backfill`）；
   - `part_versions` → 旧 metadata 不记录版本，无法可靠推断：缺失即回落到教程级 `lathe_version`，**不写进 `_needs_backfill`**；
   - `_needs_backfill` → 记录 `changed_interfaces`、`knowledge_backlog`、`open_threads_archive` 等无法可靠推断的字段；用户补上后从数组移除；
   - `continuity` → 按上方字段语义从正文提炼（含 `open_threads`，从各部分"接下来"的未决问题提取；`exercise_carry` 从最后一部分的「练习承接」行推断，推不出则三个数组都空；归档内容无法可靠推断，留空）；
   - `voice` → 默认 `plainspoken`（正文不可判定）；`status` → `unverified`；
   - `lathe_version` → 当前技能版本；
   - `repo`、`local_project_path` → 正文有线索则填，否则留空。
3. **确认后写入：** 向用户展示重建结果（明确标注哪些字段为推断值）。对 `changed_interfaces`、`open_threads` 归档等无法可靠推断的字段，写入 `_needs_backfill` 数组并在报告中标注“待人工补”，不要静默当空。用户确认后写入 `metadata.json`（含顶部的 `_warning` 字段），并在 `~/.lathe/config.json` 的 `tutorial_paths` 中登记该教程位置。
4. **只读操作不写入：** `list` 将此类教程标注为 *⚠️ metadata 缺失* 并建议运行修复；`ask` 基于部分文件直接回答并顺带提醒。

用户拒绝重建时，相关写入型操作（续写/验证/打标签）终止并说明原因；不要在没有索引的情况下修改教程文件。

**自愈是唯一允许跨越"仅改本字段"边界的场景**——标签、验证等操作在自愈时可写入完整 metadata，因为不重建索引就无法继续。
