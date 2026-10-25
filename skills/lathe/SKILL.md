---
name: lathe
version: 0.6.1
description: 按需生成、续写、复习、验证、提问动手实践型技术教程。当用户说 /lathe 并附带主题时使用，如 "/lathe 用 Zig 构建数字合成器"；也处理续写(extend)、收尾完结(finish)、复习(review)、验证(verify)、提问(ask)、面试(interview)、标签(tag)、语气(voice)、扫描(scan)和列表(list)等教程操作。支持中文和英文关键词。
---

# Lathe — 教程体系

Lathe 管理动手实践型教程。写作质量以 `references/writing-core.md` 为准；主风格锚点从下方速查表选择。

## 使用方式

```text
/lathe <主题>                          → 生成新教程
/lathe 续写|extend <slug> [指导]       → 续写下一部分
/lathe 续写 收尾 <slug>                → 生成总结部分并完结
/lathe 复习|review <slug>              → 生成复习材料
/lathe 面试|interview <slug> [part]    → 生成或补齐面试文档
/lathe 验证|verify <slug>              → 端到端验证
/lathe 提问|ask <slug> <part> <问题>   → 提问教程内容
/lathe 标签|tag <slug>                 → 管理标签
/lathe 语气|voice [名称]               → 创建自定义语气
/lathe 扫描|scan [目录]                → 登记已有教程
/lathe 列表|list [slug]                → 列出教程或查看状态
```

面试也可从复习或生成进入：`/lathe 复习 <slug> 面试 [part-NN]`、`/lathe <主题> 面试`。纯自然语言同样可触发。

## 操作路由

识别意图后立即读取对应模块：

| 意图 | 关键词 | 模块 |
|---|---|---|
| 生成 | 无下述操作词的主题描述 | [references/generate.md](references/generate.md) |
| 续写 | 续写、继续、下一部分 / extend、continue、next、add、part | [references/extend.md](references/extend.md) |
| 收尾 | 续写/extend + 收尾、完结、总结 / finish、wrap up | [references/extend.md](references/extend.md) |
| 复习 | 复习、回顾 / review、revise、recap | [references/review.md](references/review.md) |
| 面试 | 面试 / interview | [references/interview.md](references/interview.md) |
| 验证 | 验证、检查、测试 / verify、check、test、validate | [references/verify.md](references/verify.md) |
| 提问 | 提问、问、问题 / ask、question | [references/ask.md](references/ask.md) |
| 标签 | 标签、打标签 / tag、tags、label | [references/tag.md](references/tag.md) |
| 语气 | 语气、风格 / voice、tone、style | [references/voice.md](references/voice.md) |
| 扫描 | 扫描、登记、注册 / scan、register、sync | [references/scan.md](references/scan.md) |
| 列表 | 列表、列出、查看状态 / list、ls、status | [references/list.md](references/list.md) |

路由规则：

1. 疑问词仅在同时给出已知 slug 时视为提问，否则先消歧。
2. `面试` / `interview` 必须是独立 token，且位于复习语境，或作为首 token 后跟已存在 slug；否则把它当主题的一部分。不确定时先问。
3. 意图不明确时列出上方十一项让用户选择，不要默认生成。明确主题、明确操作不要多问。
4. 复习语境含面试 token 时转 `interview.md`。

## 技能目录与共享文件

`<SKILL_DIR>` 是本文件所在目录。共享文件按需加载：

| 文件 | 单一职责 | 何时读取 |
|---|---|---|
| [references/writing-core.md](references/writing-core.md) | 教程结构、4–7 构建配额、地基/承接豁免、总章 ≤9、研究与自检 | 生成、续写、收尾、复习；面试仅取研究预算与事实不变量 |
| [references/knowledge-ledger.md](references/knowledge-ledger.md) | 双布局、canonical 知识表、固定八列、六态、选点优先级、确认/回执、承诺与闸门 | 生成、续写、收尾 |
| [references/metadata.md](references/metadata.md) | metadata、Part 级路线、continuity 缓存、双布局与自愈 | 新建或写回 metadata、解析布局、自愈 |
| [references/style-benchmarks.md](references/style-benchmarks.md) | 标杆作者写法 | 只有需要理解锚点手法时 |

最小加载集：

- 生成：`generate.md` + `writing-core.md` + `knowledge-ledger.md` + `metadata.md`；非默认 voice 才读 `voice.md`；带面试 token 才读 `interview.md`。
- 续写：`extend.md` + 上述三个共享规范；已有或请求面试文档时加 `interview.md`。
- 收尾：先读 `extend.md` 收尾节与课程 metadata/知识事实源判门禁；通过后再读共享规范和必要正文。
- 复习、面试、验证、提问、标签、扫描、列表按各模块声明加载；保留这些模块尚未迁移的兼容读法，不把它们反向当成 0.6.1 写入规范。

## 风格主锚点速查

生成时选一个 id 写入 metadata 的 `style_anchor`；续写沿用。

| 场景 | id |
|---|---|
| 编译器 / 解释器 / 语言工具 | `nystrom` |
| 算法 / 数据结构 / 数学可视化 | `amit-patel` |
| 系统底层 / 硬件 / 协议 | `ciechanowski` |
| 分布式系统 / 基础设施 | `sam-who` |
| 日常工具 / 入门 | `julia-evans` |
| 系统架构 / 工程权衡 | `kleppmann` |
| Rust | `klabnik-nichols` |
| 记忆 / 回顾机制 | `matuschak` |
| 底层原理 | `bernhardt` |
| 交互式概念可视化 | `bret-victor` |

id 只能取以上十个。跨场景时选最强主锚点。

## 教程位置与双布局

配置位于 `~/.lathe/config.json`：

```json
{
  "tutorials_base_path": "~/others/lathe_tutorials",
  "tutorial_paths": {"raft-go": "~/projects/my-tutorials"}
}
```

- config 不存在时，按 `references/scan.md` 的首次/已有教程流程建立后继续。
- 生成时每次确认保存基础目录；保存到非默认目录才登记 `tutorial_paths[slug]`。
- 已有教程先查 `tutorial_paths[slug]`，再查默认基础目录；找不到时列出已知位置并提示 `/lathe 扫描`。
- 参数是已有目录时直接操作该目录，不登记配置；末级目录名作为 slug。
- 扫描与枚举跳过点号开头的目录。

`<COURSE_DIR>` 指解析后的课程根目录。正文始终是 `<COURSE_DIR>/part-*.md`。辅助布局由 metadata 位置一次性确定：

| 布局 | 判定 | knowledge / research / verify |
|---|---|---|
| 0.6.1 新课程 | `<COURSE_DIR>/_lathe/metadata.json` | `_lathe/knowledge-points.md`、`_lathe/research.md`、`_lathe/verify-result.json`、`_lathe/verify-workspace/` |
| legacy 课程 | `<COURSE_DIR>/metadata.json` | `syllabus.json`、`research.md`、`verify-result.json`、`.lathe-verify/`，全部原地 |

不得逐文件回退。两处 metadata 同时存在，或辅助文件跨布局混放，均列出冲突并停止写入；旧课不迁移、不创建 `_lathe/`。目录只有 part 而 metadata 缺失时按 `metadata.md` 自愈，不能当成 slug 不存在。

## 面试文档路径

按以下顺序解析：

1. `interview_paths[slug]/<slug>.md`；
2. `interview_base_path/<slug>.md`；
3. 都未配置时采用布局 fallback：新课程 `<COURSE_DIR>/_lathe/interview.md`，legacy `<COURSE_DIR>/interview.md`。

首次创建必须展示默认路径并确认；已有文档沿用当前位置。外部路径仍可独立于课程布局。

## metadata 速查

完整契约见 `references/metadata.md`。新课程 metadata 只放 `_lathe/metadata.json`，常用字段为：

`_warning`、`_needs_backfill`、`lathe_version`、`part_versions`、`slug`、`title`、`topic`、`goal`、`created`、`status`、`tags`、`parts`、`language`、`experience_level`、`topic_novelty`、`course_plan`、`changed_interfaces`、`style_anchor`、`repo`、`repo_branch`、`local_project_path`、`tools`、`sources`、`voice`、`model`、`continuity`、`verify_workspace`

`course_plan` 固定为 3–12 个 Part 级项，不复制点级状态。`continuity` 是可重建缓存：控制性示例、固定数字、隐喻、最近已讲概念、未决线程、衔接、最近标题与更新时间；知识点状态与练习承诺只在 canonical ledger。字段缺失时按 metadata.md 推断并在写回时补齐，不能因普通缺字段中止。

状态机：

- 生成/续写后 `unverified`；验证通过为 `verified`；收尾为 `completed`。
- 完结课程再次续写时回到 `unverified`；复习不改状态。
- 提问勘误确认修改后，`verified` 回到 `unverified`，`completed` 保持。

## 知识表速查

新课程唯一知识点事实源是 `_lathe/knowledge-points.md`；固定八列且只能有一个连续表：

`ID | 知识点 | 来源 | 类型 | 计划 Part | 状态 | 已讲位置 / 承诺来源 | 备注`

- 状态：`planned` / `queued` / `taught` / `self-study` / `dropped_by_user` / `duplicate`。
- 类型：`main` / `foundation` / `mergeable` / `carry`。
- 位置使用 `at:` / `promise:` / `dup:` / `—`；进度与六态统计是由数据行重建的显示缓存。
- 每次写操作运行 `ledger_check.py <COURSE_DIR>`；脚本参数永远传课程根目录。
- legacy 课程继续原地维护 `syllabus.json`，保持其 JSON 格式和未知字段。

## 验证状态横幅

常规 `part-NN.md` 在 H1 后可带：

```markdown
<!-- lathe:verify-status:start -->
> [!WARNING]
> 本部分尚未通过端到端验证。生成于 <YYYY-MM-DD>；运行 `/lathe 验证 <slug>` 查看结果。
<!-- lathe:verify-status:end -->
```

生成/续写写未验证态；失败或跳过由 verify 更新；通过时移除。复习与收尾不写横幅。发现重复、嵌套或缺少结束标记时停止修改该 part。verify 先更新横幅，再写当前布局的 verify result；新课程使用 `_lathe/verify-result.json` 和 `_lathe/verify-workspace/`，legacy 保持根目录旧路径。

## 教程语言

生成时默认跟随对话语言，用户可覆盖并写入 `language`。续写、复习、提问沿用；legacy 缺失时从正文推断并在下次 metadata 写回时补齐。

## 保持会话

完成操作后保持可用，继续回答该主题的问题。

## 版本

**技能版本：v0.6.1**。写入型操作同步更新 metadata 的 `lathe_version`；每个新 part 在 `part_versions` 记录本次版本。
