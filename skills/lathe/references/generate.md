# 生成教程

按需为任意主题生成动手实践型技术教程的第一部分。

**先读共享文件：** 本操作需要 `<SKILL_DIR>/references/writing-core.md`（教程结构、配额矩阵、标注规则、不变量、研究纪律、预检、写法细节、交付前自检）。本文件只补充生成特有的流程，不重述其中内容。

## 协议

1. **解析配置并确保可用**（见 `<SKILL_DIR>/SKILL.md`"教程存储路径配置"）——config 不存在时先走首次/老用户分支创建它。
2. **一轮分组提问**（见下方）——把保存位置、slug、经验水平、**主题新颖度**、语气（voice）、澄清问题、仓库、工具链版本、学习目标合并为一次询问，避免多轮往返。
3. **确认 slug 可用**（见下方"slug 与目录冲突检查"）——**在写研究和正文之前完成**，避免白写一遍才发现撞名。
4. **确定教程语言**（见 `<SKILL_DIR>/SKILL.md`"教程语言"）——默认跟随对话语言，无需单独提问。
5. **选定风格主锚点**：按 `<SKILL_DIR>/SKILL.md`「风格主锚点速查」表匹配主锚点，记下其 id 待写入 `style_anchor`。**只选 id 时不读 `style-benchmarks.md`**；仅当需要理解该锚点的具体写作手法时才读它的「标杆作者」表。
6. **先研究主题**（见 writing-core.md"先研究"，按 `topic_novelty` 取配额矩阵中的检索预算）——这是确保准确性的最关键步骤。
7. 静默执行**预检**（见 writing-core.md）。不要让用户审批。
8. 撰写第一部分（结构见 writing-core.md"教程结构"）。**动笔前先确定 `course_plan`（3-8 项，每项一句话）**，再写 part-01；part-01 完成路线图的第 1 项。`course_plan` 写入 metadata，不是 `index.md`。本部分主知识点控制在 4-7 个；课程计划中超出本部分范围的知识点写进 `course_plan` / `next_hook`，不要压进同一部分，也不要一次写多个部分。若 part-01 修改了现有 API/签名或跨文件契约，按 metadata.md 的字段规范写入 `changed_interfaces`；没有变化时写空数组。
9. 执行 writing-core.md **"交付前自检"**——尤其核对六项讲透、代码完整性与知识点数量；若本部分有接口变更，核对 `changed_interfaces` 与 part 内的改动面表是否一致。
10. **存储教程**（见下方"写完之后"）。
11. **【条件步骤】同步面试文档** —— **仅当本次触发含独立的 `面试` / `interview` token 时**：在教程（`part-01.md` + `metadata.json`）**落盘完成之后**，按 `<SKILL_DIR>/references/interview.md` 为该课程生成 **Part 1 的面试分段**（含文档创建与头部三表）。**未含该 token 时跳过本步**——本步骤不影响上方 1-10 步的任何规则。

## 始终只写第一部分

每次调用只生成一个**教程部分**：`part-01.md`。绝不写多个部分，也绝不写 `index.md`。读者通过"续写"操作添加更多部分。

> **课程路线图是 metadata 字段，不是 `index.md`。** `course_plan` 只写进 `metadata.json`，用来给本次和后续续写定边界；它不产生额外文件，也不改变"一次只写一个部分"的约束。

> 面试文档（仅在带 `面试` 参数时产出）是**附加产物**，不计入本约束，也**绝不影响** `part-01.md` 的结构与写作规则。

## 一轮分组提问（研究之前）

用**一条消息**分组收集写作前需要的全部信息，不要拆成多轮问答。**除"保存位置"外，其余各项一律先给出建议默认值并标注 `[默认]`——用户回复"可以"即全部采纳；只有用户明确反对某一项时才展开追问。**

1. **保存位置（每次生成都问）：** 展示 config 中的默认目录并确认——*"本教程将保存到 `~/others/lathe_tutorials/`（默认目录），要换个位置吗？"* 用户给出新路径则本教程存到那里，否则用默认值。**这一项必须先问出、拿到回答再动笔**——即使在没有选择框 UI 的终端 Agent（如 Reasonix、Claude Code、Codex）里，也要以纯文本明确问出；用户回车/未指定即视为采用默认目录，但不得直接静默跳过。
2. **教程 slug：** 由主题推导一个 kebab-case 短名称并**展示给用户确认**——*"目录名将是 `todo-cli-rust`，可以吗？"* 这是教程的永久标识和目录名，用户此后靠它调用所有其他操作，所以必须让他知道，不要静默决定。
3. **经验水平：** *"你在这个领域的经验水平如何——初学者、有一定了解、还是在相关领域有经验？"* 三个回答分别对应 `experience_level` 的 `beginner` / `familiar` / `experienced`，写入 metadata 供后续续写沿用。
4. **主题新颖度（topic_novelty）：** *"这个主题对你是**全新领域 / 有相邻经验 / 已经熟悉**？"* 三个回答分别对应 `new` / `adjacent` / `familiar`，写入 metadata；它决定检索预算、地基章节、标注与概念锚定的配额。**默认按经验水平推断**：`beginner → new`、`familiar → adjacent`、`experienced → familiar`；用户可改。未作答即用推断值。
5. **语气（voice）：** 列出可选语气供选择——`plainspoken`（默认，平实精确、不虚构人格）、`companion`（陪伴式）、`craftsman`（工匠式），或用户已创建的自定义 voice。**默认 plainspoken 无需读取 `voice.md`**；仅当用户选了 companion/craftsman/自定义时，才按 writing-core.md"voice 的应用"加载对应规范。未作答即用 plainspoken。
6. **澄清问题（仅在主题确实含糊时加入）：** 语言？规模？嵌入式还是服务端？最多**一个**。
7. **仓库：** 此教程是否针对特定仓库？如果是，记录远程 URL 和分支。独立教程则跳过。
8. **工具链版本：** 确定教程将依赖哪些语言/工具，提议版本——*"我将基于 **Zig 0.13.0** 和 **LLVM 18** 来写——可以吗？"*——根据回答调整。
9. **学习目标（goal）：** 基于主题与经验水平提炼一句可评估的学习目标（如*"掌握用 Rust 构建 CLI 应用的完整流程：参数解析、持久化、测试"*），在同一条消息中展示确认（可与工具链版本合并为一条）。该目标是后续续写时"目标达成回顾"与收尾完结的判定基准。
10. **面试文档保存位置（仅当本次触发含 `面试` token 且面试文档尚不存在时加入）：** 展示按 `interview.md`「路径解析」三档算出的默认路径并确认——*"面试文档将保存到 `<默认路径>`，要换个位置吗？"*。**未带 `面试` token、或该课程的面试文档已存在时，本项不加入**——分组提问仍为 9 项。

锁定的版本是写作约束：引用与版本相关的行为时注明版本，锚定到锁定的版本。用户对某项未作答时采用合理默认值并告知，不再追问。

**各项的建议默认值**（未作答即采用，并在同一条消息里标注为 `[默认]`）：slug = 由主题推导的 kebab-case；经验水平 = `familiar`；主题新颖度 = 按经验水平推断（`beginner → new` / `familiar → adjacent` / `experienced → familiar`）；voice = `plainspoken`；澄清问题 = 不追加；仓库 = 无（独立教程）；工具链版本 = 该生态当前稳定版（写出具体版本号）；goal = 由主题与经验水平提炼的一句。**保存位置没有默认值，必须问出回答。**（第 10 项仅在带 `面试` token 时出现，其默认值 = `interview.md` 三档解析结果。）

## slug 与目录冲突检查（写作之前，必做）

确认 slug 后、开始研究之前，检查**本次保存位置下 `<目录>/<slug>/` 是否已存在**。

- **不存在** → 正常继续。
- **已存在** → **停下来，绝不覆盖。** 读取该目录的 `metadata.json`（或 part 文件）识别它是什么，然后给用户三个选项：

  ```
  `<slug>` 已存在于 `<目录>/`——是「<已有标题>」，共 <N> 个部分，状态 <status>。

  1. 🔤 **换一个 slug** — 我用 `<slug>-2` 或你指定的名称新建
  2. 📝 **改为续写那个教程** — 放弃新建，为已有教程添加下一部分（/lathe 续写 <slug>）
  3. ⛔ **取消** — 什么都不做

  请回复编号。
  ```

- **同时检查 `tutorial_paths`：** 若 slug 已登记在**其他**目录，一并告知用户（可能是他想找的那个教程被移动过），并提示 `/lathe 扫描` 可校正登记。

**绝不静默覆盖已有的 `part-01.md` 或 `metadata.json`。** slug 由主题推导，相近主题（"用 Rust 写 CLI 工具" / "Rust 命令行应用"）极易撞名，覆盖会让已有教程的其余部分变成无索引的孤儿文件。

## 开头

第一句话只有一个任务：证明这不会又是一篇"在本教程中我们将"的页面。选择之一：

- **具体场景。** *"凌晨 3 点，生产环境刚刚飙升，唯一还在攀升的曲线是 p99 延迟。"*
- **值得核实的主张。** *"现代 CPU 从主存读取一个字节的时间里，大约可以执行十亿次算术运算。"*
- **引文。** 一句简短的署名引用。慎用——整个系列最多一次。
- **读者的困惑，作为陈述命名。** *"如果你读过哈希表却仍然不确定'开放寻址'什么时候比链式法更好——这篇就是写给你的。"*

**禁止的首句：** "在本教程中，我们将……" / "这篇文章解释了……" / "你是否想过……" / "欢迎来到……" / "让我们开始吧。"

## 语气选择

教程的语气是可选的 voice，不是硬编码角色。分组提问（协议第 2 步）中已列出可选 voice；用户选定或在指令中指定了 voice 就用它，未选则用 `plainspoken`。在 `metadata.json` 中记录 voice 名称。加载规则见 writing-core.md"voice 的应用"——**默认 plainspoken 不要读取 voice.md**。

自定义 voice 读取 `<TUTORIALS_DIR>/voices/<名称>.md` 获取规范。

## 结尾

结尾结构（接下来/寄语 → 结尾反思 → 练习 → 来源）的定义见 writing-core.md"教程结构"。写法要点：

1. **寄语（或前向钩子）和结尾反思**放在 `## 接下来` 中。反思示例：*"在继续之前：用两句话说明，为什么环形缓冲区在这里优于通道？"* 不要替读者回答。part-01 的前向钩子要命名一个未决问题——它会成为 `continuity.next_hook`，是下次续写的默认任务。
2. **`## 练习`** 必做 3-5 个 + 选做 0-3 个（总 ≤8）；每个具体到 30 秒内可开始。*"在两个振荡器之间添加 FM 调制。"* 而不是*"进一步探索。"* 新主题至少包含一个"照着改"和一个"从零复现/预测-验证"的必做练习。
3. **`## 来源`** 只列*本部分*内联引用过的来源；数量不设上限，>5 条按主题分组。

## 写完之后（存储教程）

在**用户确认的保存位置**下创建 `<目录>/<slug>/`（已通过冲突检查）并写入两个文件：

**1. 写入** `part-01.md` —— 教程内容。

**2. 写入 `metadata.json`** —— 按下方 JSON 骨架与字段表逐项填写。**字段表已足够时不要读 `metadata.md`**；仅当需要 `continuity` / `course_plan` 的详细语义、或触发 metadata 自愈时才读它。逐字段核对：

| 字段 | 取值 |
|------|------|
| `_warning` | 必须保留（原文照抄 metadata.md 中的文案） |
| `lathe_version` | 当前技能版本（见 SKILL.md「版本」节） |
| `slug` / `title` / `topic` | 用户确认的 slug、教程标题、用户原始主题描述 |
| `created` | 当前时间的 ISO 8601 时间戳 |
| `goal` | 分组提问中确认的学习目标（用户未确认时取你提炼的版本并告知） |
| `status` / `parts` | `unverified` / `["part-01.md"]` |
| `tags` | 2-5 个小写标签：语言/运行时、领域、核心技术 |
| `language` | 教程正文语言（见 SKILL.md"教程语言"） |
| `experience_level` | 分组提问第 3 项 → `beginner` / `familiar` / `experienced` |
| `topic_novelty` | 分组提问第 4 项 → `new` / `adjacent` / `familiar`；驱动配额矩阵 |
| `course_plan` | 3-8 项课程路线图：每项 `{part, title, goal, prerequisites}`；part-01 完成第 1 项；写入 metadata，不是 `index.md` |
| `changed_interfaces` | 跨部分接口变更清单：每项 `{file, symbol, from, to, call_sites, part}`；按符号记录，最多 8 条；无变化写 `[]`。详细规则见 `metadata.md` |
| `style_anchor` | 协议第 5 步选定的主锚点 id |
| `repo` / `repo_branch` | 读者确认的仓库与分支，独立教程则为空 |
| `local_project_path` | 生成时通常为空，由续写操作填写 |
| `tools` | 与读者锁定的每个工具链版本一条 |
| `sources` | 研究期间查阅的 URL，无网络访问则为空 |
| `voice` / `model` | 使用的 voice 名称 / 你运行的模型（如 `QoderWork`） |
| `continuity` | **必须初始化**——`controlling_example`、`fixed_numbers`、`metaphor`（无则空串）、`metaphor_retired: false`、`covered_concepts`（本部分讲透的概念，只追加不合并）、`open_threads`（已提出但未展开的问题/伏笔，最多 10 条，每条 ≤80 字）、`next_hook`（`## 接下来` 指向的方向）、`part_titles`（`{"part-01.md": "<一级标题>"}`）、`updated_through: "part-01.md"`、`updated_at`。摘要总量 1200 字软 / 2000 字硬是**索引预算**，不是正文预算；超出时归档，不压缩课程正文。分字段上限见 `metadata.md`。这一步让后续续写无需重读全部历史部分 |

骨架（字段含义与自愈协议见 `metadata.md`）：

```json
{
  "_warning": "⚠️ 本文件是该教程的索引文件，请勿删除。误删后 lathe 将无法识别此教程；可运行 /lathe 标签 <slug> 或任一写入型操作触发自愈重建。",
  "lathe_version": "<当前技能版本>",
  "slug": "<kebab-case 短名称>",
  "title": "<教程标题>",
  "topic": "<用户的原始主题描述>",
  "goal": "<一句可评估的学习目标>",
  "created": "<ISO 8601 时间戳>",
  "status": "unverified",
  "tags": ["<标签1>", "<标签2>"],
  "parts": ["part-01.md"],
  "language": "<如 zh-CN>",
  "experience_level": "beginner | familiar | experienced",
  "topic_novelty": "new | adjacent | familiar",
  "course_plan": [
    {"part": 1, "title": "<部分标题>", "goal": "<该部分的一句话目标>", "prerequisites": ["<前置概念/工具>"]}
  ],
  "changed_interfaces": [],
  "style_anchor": "<主锚点 id>",
  "repo": "<远程 URL 或空>",
  "repo_branch": "<分支或空>",
  "local_project_path": "<本地项目路径或空>",
  "tools": [{"name": "<工具>", "version": "<版本>"}],
  "sources": ["<url1>"],
  "voice": "plainspoken",
  "model": "<你运行的模型>",
  "continuity": {
    "controlling_example": "<贯穿全课程的具体产物，一句话>",
    "fixed_numbers": {"<名称>": "<值>"},
    "metaphor": "<控制性隐喻，无则空字符串>",
    "metaphor_retired": false,
    "covered_concepts": ["<本部分讲透的概念>"],
    "open_threads": ["<已提出但未展开的问题/伏笔>"],
    "next_hook": "<本部分 ## 接下来 指向的方向>",
    "part_titles": {"part-01.md": "<一级标题>"},
    "updated_at": "<ISO 8601 时间戳>",
    "updated_through": "part-01.md"
  }
}
```

> `course_plan` 的骨架示例只列 1 项；实际填写 **3-8 项**。`verify_workspace` 不在生成时写入——它由 `/lathe 验证` 首次创建 `.lathe-verify/` 工作区时补上。

**3. 登记位置（仅当需要时）** —— **若本次保存位置等于 `tutorials_base_path`，跳过本步**（`tutorial_paths` 缺失即等价于"所有教程都在默认基础目录"，见 `<SKILL_DIR>/SKILL.md`"教程存储路径配置"）。仅当保存到**其他目录**时，才更新 `~/.lathe/config.json`，在 `tutorial_paths` 中写入 `"<slug>": "<本次使用的目录>"`（保留已有条目不动）。

**4. 【条件】同步面试文档** —— **仅当本次触发含 `面试` token 时**：教程全部落盘后，按 `<SKILL_DIR>/references/interview.md` 执行——确认位置（分组提问第 10 项已收）、创建面试文档、写入「第一部分 · Part 1」分段。**未带该 token 时跳过本步，不产生任何面试文档相关写入。**

然后告诉用户：
- "**教程已保存**到 `<实际保存目录>/<slug>/`。"
- "这是第一部分。要添加更多部分，调用 `/lathe 续写 <slug>`（或 `/lathe extend <slug>`），可以给出指导或让它自然延续。"
- "验证是可选的：调用 `/lathe 验证 <slug>`（或 `/lathe verify <slug>`）；需要本地安装教程的工具链。无论是否验证，本部分代码都必须完整（`runnable` / `fragment` / `exercise` 标记；不得用 `...` 省略运行必需代码）。验证只执行 `runnable` 块和检查点，跳过片段/练习。"
- "要对某个部分提问，调用 `/lathe 提问 <slug> part-01.md`（或 `/lathe ask <slug> part-01.md`）然后跟上你的问题。"
- "其他操作：复习 `/lathe 复习 <slug>`、收尾完结 `/lathe 续写 收尾 <slug>`、标签 `/lathe 标签 <slug>`、创建语气 `/lathe 语气 [名称]`、扫描登记 `/lathe 扫描`、查看全部 `/lathe 列表`。"
- **（仅带 `面试` token 时）** "**面试文档已同步生成**到 `<路径>`；后续可 `/lathe 复习 <slug> 面试` 增量补齐，或直接续写（有面试文档时会自动同步）。"
