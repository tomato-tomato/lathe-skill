---
name: lathe
version: 0.5.3
description: 按需生成、续写、复习、验证、提问动手实践型技术教程。当用户说 /lathe 并附带主题时使用，如 "/lathe 用 Zig 构建数字合成器"；也处理续写(extend)、收尾完结(finish)、复习(review)、验证(verify)、提问(ask)、打标签(tag)、创建语气(voice)、扫描登记(scan)和列出教程(list)等所有教程相关操作。支持中文和英文关键词。
---

# Lathe — 教程体系

Lathe 是一套完整的动手实践型教程管理工具，涵盖生成、续写、收尾、复习、面试文档、验证、提问、标签、语气、扫描、列表十一项功能。质量基准线由 `references/style-benchmarks.md` 的标杆作者定义（生成时按下方「风格主锚点速查」表只选一个 id；需要理解具体写作手法时才加载该文件）。

## 使用方式

所有操作通过 `/lathe` 调用，后跟**意图关键词**（中文或英文均可）和参数：

```
/lathe <主题>                          → 生成新教程
/lathe 续写|extend <slug> [指导]       → 续写教程下一部分（该教程已有面试文档时，自动同步本部分）
/lathe 续写 收尾 <slug>                → 生成总结部分并完结课程
/lathe 复习|review <slug>              → 生成复习材料（不改变课程方向）
/lathe 面试|interview <slug> [part]    → 生成或补齐面试文档（详见 references/interview.md）
/lathe 验证|verify <slug>              → 端到端验证教程
/lathe 提问|ask <slug> <part> <问题>   → 提问教程内容
/lathe 标签|tag <slug>                 → 管理教程标签
/lathe 语气|voice [名称]               → 创建自定义语气
/lathe 扫描|scan [目录]                → 登记磁盘上未被识别的教程
/lathe 列表|list [slug]                → 列出所有教程或查看某教程状态
```

面试文档也可从复习或生成进入：`/lathe 复习 <slug> 面试 [part-NN]`、`/lathe <主题> 面试`。

也支持纯自然语言触发（无需 `/lathe`），AI 会自动识别意图。中文和英文关键词均可识别。

## 操作路由

根据用户消息中的意图关键词，**立即读取对应模块文件**（位于 `<SKILL_DIR>/references/`）并按其中的完整协议执行：

| 用户意图 | 识别关键词（中文 / 英文） | 使用示例 | 读取模块 |
|----------|-------------------------|----------|----------|
| **生成新教程** | 主题描述（无下述关键词时） / topic description | `/lathe 用 Go 构建 Raft` | [references/generate.md](references/generate.md) |
| **续写教程** | 续写、继续、下一部分 / extend、continue、next、add、part | `/lathe extend raft-go` 或 `/lathe 续写 raft-go`（该教程已有面试文档时自动同步本部分） | [references/extend.md](references/extend.md) |
| **收尾完结** | 续写/extend + 收尾、完结、总结 / finish、wrap up | `/lathe 续写 收尾 raft-go` | [references/extend.md](references/extend.md)（收尾模式） |
| **复习教程** | 复习、回顾 / review、revise、recap | `/lathe 复习 raft-go` 或 `/lathe review raft-go` | [references/review.md](references/review.md)（**含 `面试` token 时转** [references/interview.md](references/interview.md)） |
| **面试文档** | 面试、interview（作为首个 token 且后跟已存在的 slug） | `/lathe 面试 raft-go` 或 `/lathe 面试 raft-go part-02` | [references/interview.md](references/interview.md) |
| **验证教程** | 验证、检查、测试 / verify、check、test、validate | `/lathe verify raft-go` 或 `/lathe 验证 raft-go` | [references/verify.md](references/verify.md) |
| **提问内容** | 提问、问、问题 / ask、question | `/lathe ask raft-go part-01 why use ring buffer` | [references/ask.md](references/ask.md) |
| **管理标签** | 标签、打标签 / tag、tags、label | `/lathe tag raft-go` 或 `/lathe 标签 raft-go` | [references/tag.md](references/tag.md) |
| **创建语气** | 语气、风格 / voice、tone、style | `/lathe voice terse` 或 `/lathe 语气 terse` | [references/voice.md](references/voice.md) |
| **扫描登记** | 扫描、登记、注册 / scan、register、sync | `/lathe 扫描` 或 `/lathe scan ~/tutorials` | [references/scan.md](references/scan.md) |
| **列出教程** | 列表、列出、查看状态 / list、ls、status | `/lathe list` 或 `/lathe 列表 raft-go` | [references/list.md](references/list.md) |

**路由规则：**

1. 解析 `/lathe` 后的第一个关键词来确定意图。中英文关键词等价。疑问词（为什么、怎么 / why、how、what）**仅在同时给出已知 slug 时**视为提问意图，否则按歧义处理——避免把 `/lathe 怎么用` 这类话误判为 ask。
2. **`面试` / `interview` 的识别**：必须是**独立 token**（前后为空白、行尾或标点）。两种成立方式——① 出现在 `复习` 语境中（`/lathe 复习 <slug> 面试`）；② 作为**首个 token** 且**后跟一个已存在的 slug**（`/lathe 面试 <slug>`）。不满足时视为**主题的一部分**，走正常生成（如 `/lathe 面试题生成器怎么做` → 生成教程）。不确定时**先问**，不要默认进入面试模式。
3. **意图不明确时，先询问再执行。不要默认生成教程。** 歧义情形：只输入 `/lathe`、只给一个 slug（可能是续写/验证/提问/复习/面试）、含糊表达（`/lathe 这个教程怎么样`、`/lathe how is this tutorial`）。此时**以上方路由表为清单**，列出十一项操作（带简短说明）让用户选编号或关键词；用户选定的意图若缺参数（如续写需要 slug），补充询问后再读取模块。
   反例——这些是**明确**的，不要多问：`/lathe 用 Go 构建 Raft`（主题 → 生成）、`/lathe 续写 raft-go`、`/lathe 验证 raft-go`。
4. 纯自然语言触发（不含 `/lathe`）时通过上下文语义匹配意图，中英文均可。
5. 各模块文件可能引用下方共享配置或 `references/` 下的其他共享文件。

## 技能目录与共享文件

本技能的入口文件是 `SKILL.md`，各模块文件位于其同级的 `references/` 子目录下。后文中 `<SKILL_DIR>` 指 **SKILL.md 所在目录**（如 `~/.qoder/skills/lathe` 或 `<项目>/.reasonix/skills/lathe`）。

三个**共享**文件按需加载，不要无条件读取：

| 文件 | 内容 | 何时读取 |
|------|------|----------|
| [references/writing-core.md](references/writing-core.md) | 教程结构、标注类型与配额、不变量、研究纪律、预检、写法细节、交付前自检 | **仅写作型操作**：生成、续写、收尾、复习、面试文档（面试文档**只用**其中的检索预算与「有据可依或标记」不变量） |
| [references/metadata.md](references/metadata.md) | `metadata.json` 完整结构、`continuity` 摘要规范、自愈协议 | 写 `continuity`、或遇到 metadata 缺失/损坏需自愈时；**生成时字段速查表已足够，不读** |
| [references/style-benchmarks.md](references/style-benchmarks.md) | 标杆作者表与场景侧重表 | **仅当需要理解某锚点的具体写作手法时**；只选 id 用下方「风格主锚点速查」表，不读本文件 |

**反向清单——明确不要读取**（读多了会挤占上下文并拖慢执行）：

- **生成新教程：** 不要读 `extend.md`、`verify.md`、`list.md`、`scan.md`、`review.md`、`ask.md`、`tag.md`；`voice.md` 仅在 voice 非 `plainspoken` 时读；`metadata.md` 仅在字段速查表不足或需自愈时读；`interview.md` **仅在本次带 `面试` 参数时**读。
- **续写 / 收尾：** 不要读 `generate.md`、`style-benchmarks.md`、`verify.md`、`list.md`、`scan.md`、`review.md`、`ask.md`、`tag.md`。**`interview.md` 是例外**——该教程已有面试文档时读它以追加本部分分段，或带 `面试` 参数时读它以创建文档。
- **复习：** 不要读 `generate.md`、`extend.md`、`style-benchmarks.md`、`verify.md`、`list.md`、`scan.md`、`ask.md`、`tag.md`；**含 `面试` token 时改读 `interview.md`**（本文件下方协议不再适用）。
- **面试文档：** 不要读 `generate.md`、`extend.md`、`review.md`、`verify.md`、`list.md`、`scan.md`、`ask.md`、`tag.md`、`style-benchmarks.md`；`metadata.md` 仅在需自愈时读。
- **验证：** 不要读 `writing-core.md`、`generate.md`、`extend.md`、`review.md`、`interview.md`、`style-benchmarks.md`。
- **提问 / 标签 / 列表 / 扫描：** 不要读 `writing-core.md`、`generate.md`、`extend.md`、`review.md`、`interview.md`、`verify.md`、`style-benchmarks.md`。

> 判据：只读上方"何时读取"列为"是"的文件；本清单是它的补集，两者不应有交集。

## 风格主锚点速查

生成新教程时按主题选定**一个**主锚点，把其 id 写入 `metadata.json` 的 `style_anchor`（续写 / 复习 / 收尾从 metadata 读取，不重选、不加载 `style-benchmarks.md`）。

| 主题场景 | 主锚点 id |
|----------|-----------|
| 构建编译器 / 解释器 / 语言工具 | `nystrom` |
| 算法 / 数据结构 / 数学可视化 | `amit-patel` |
| 系统底层 / 硬件 / 协议拆解 | `ciechanowski` |
| 分布式系统 / 基础设施 | `sam-who` |
| 日常工具 / 去神秘化 / 入门 | `julia-evans` |
| 系统架构 / 工程权衡 | `kleppmann` |
| Rust 语言相关 | `klabnik-nichols` |
| 涉及记忆 / 回顾机制设计 | `matuschak` |
| 底层原理 / 追本溯源 | `bernhardt` |
| 需要"让概念可见"的交互 | `bret-victor` |

**本表是 `references/style-benchmarks.md`「场景侧重」表的投影**——两者同为 `style_anchor` 的合法取值来源，**id 只有这 10 个，不得自创**。主题跨多个场景时选最强的一个作主锚点，其余为辅。**需要理解某锚点的具体写作手法时**（如"nystrom 式章节独立成篇"具体指什么）才去读 `style-benchmarks.md` 的「标杆作者」表。

## 教程存储路径配置

教程存储位置记录在 `~/.lathe/config.json`，支持**多路径存储**——不同教程可以保存在不同目录：

```json
{
  "tutorials_base_path": "~/others/lathe_tutorials",
  "tutorial_paths": {
    "taskr": "~/others/lathe_tutorials",
    "raft-go": "~/projects/my-tutorials"
  }
}
```

| 字段 | 含义 |
|------|------|
| `tutorials_base_path` | **默认基础目录**：生成新教程时默认提议的位置；`voices/` 自定义语气目录也始终位于此处 |
| `tutorial_paths` | **教程 → 位置映射**：每个教程（slug）实际所在的基础目录。可选字段——缺失时等价于所有教程都在 `tutorials_base_path` |

**每次调用本技能时，首先解析配置：**

1. 尝试读取 `~/.lathe/config.json`。
2. **文件存在** → 直接读取，不再询问默认目录。
3. **文件不存在** → 按 `<SKILL_DIR>/references/scan.md`"建立 config（config.json 不存在时）"询问用户是首次使用还是已有教程并写入 config，完成后继续原本的调用意图。

**教程位置解析规则（各操作通用）：**

- **生成新教程：** 每次生成前都询问本课程保存位置（默认提议 `tutorials_base_path`）；保存后将该教程登记到 `tutorial_paths`。
- **操作已有教程（带 slug）：** 先查 `tutorial_paths[<slug>]`；未登记则回退到 `tutorials_base_path`；该位置也找不到此 slug 时，列出 config 中已知的所有 slug 及其位置供用户选择，**并提示 `/lathe 扫描` 可以把磁盘上未登记的教程找回来**（教程被手工拷贝、克隆或移动进来时就属于这种情况）。
- **枚举教程目录时（扫描、列表等），跳过以 `.` 开头的隐藏目录**——如验证工作区 `.lathe-verify/`，它们不是教程。
- 后文中 `<TUTORIALS_DIR>` 指**默认基础目录**（`tutorials_base_path`）；涉及具体教程时按上述规则解析到其实际所在目录。`voices/` 目录始终位于默认基础目录下。

> 兼容性：仅含 `tutorials_base_path` 的旧 config 继续可用——等价于 `tutorial_paths` 缺失的状态，已有教程无需迁移。

### 面试文档路径配置

面试文档（每个 slug 一个 Markdown 文件，详见 [references/interview.md](references/interview.md)）的位置用**另外两个可选字段**记录，缺失即走下一档：

```json
{
  "interview_base_path": "~/Code/agent-transition/interview",
  "interview_paths": {
    "nest-kb-service": "~/Code/agent-transition/interview/阶段一_NestJS与服务端基础"
  }
}
```

| 顺序 | 条件 | 文档路径 |
|------|------|----------|
| 1 | `interview_paths[<slug>]` 存在 | `<该目录>/<slug>.md` |
| 2 | `interview_base_path` 存在 | `<该目录>/<slug>.md` |
| 3 | 都没有 | `<教程目录>/<slug>/interview.md` |

**位置确认规则：**

- **文档不存在**（首次创建）→ **必须询问**：展示解析出的默认路径并确认；用户改位置则写入 `interview_paths[<slug>]`。**不得静默跳过。**
- **文档已存在** → **不询问**，沿用当前位置，仅在结果里一行播报。

> 兼容性：两个字段都可选，旧 config 缺失即走第 3 档，无需迁移。

## metadata.json 速查

每个教程目录下有一个 `metadata.json` 索引文件。字段一览（**完整结构、字段语义与自愈协议见 [references/metadata.md](references/metadata.md)**）：

`_warning`、`lathe_version`、`slug`、`title`、`topic`、`goal`、`created`、`status`、`tags`、`parts`、`language`、`experience_level`、`style_anchor`、`repo`、`repo_branch`、`local_project_path`、`tools`、`sources`、`voice`、`model`、`continuity`、`verify_workspace`

**读取几个已知字段时直接读 JSON 即可，无需加载 metadata.md。** 遇到以下情况才读：新建 metadata、写 `continuity` 摘要、或文件缺失/损坏需要自愈。

**任何字段缺失都必须可降级运行**——按 metadata.md 的规则推断，并在本次写回时补上，绝不因缺字段中止操作。

**status 状态机：**

- `unverified` → 生成/续写后的默认状态（新增部分后重置为此值）；
- `verified` → 验证通过后由 verify 写入；
- `completed` → 收尾完结（`/lathe 续写 收尾 <slug>`）后写入，表示课程已达成学习目标并体面结束；
- **`completed` 可被撤销：** 用户对已完结课程再次续写（写入任何新的常规部分）时，`status` 重置为 `unverified`——继续学习意味着课程重新开放。**复习不改变 status**。

## 教程语言

教程**正文语言**与触发语言解耦：

1. **生成时确定**：默认跟随用户当前对话语言；用户显式指定（如 "用英文写"）时以指定为准。记录到 `metadata.json` 的 `language` 字段。
2. **续写/复习/提问时沿用**：读取 `language` 字段并保持一致，不因用户切换对话语言而漂移。
3. **旧教程缺失该字段时**：按已有部分的实际语言推断，并在下次写 metadata 时补上。

## 保持会话

无论执行哪个操作，完成后不要结束会话。保持可用以回答后续问题。你是他们在该主题上的专家向导。

## 版本

**技能版本：v0.5.3**（版本号同时记录在每个教程 `metadata.json` 的 `lathe_version` 字段；`/lathe 列表` 会在结尾显示当前版本）
