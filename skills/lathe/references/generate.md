# 生成教程

为一个主题建立完整课程地图，并只写第一部分。

**先读：** `<SKILL_DIR>/references/writing-core.md`、`knowledge-ledger.md`、`metadata.md`。本文件只规定生成流程；结构、配额、canonical ledger 与 schema 以三份共享规范为准。

## 不可变边界

- 一次只写 `<COURSE_DIR>/part-01.md`，不写多个 Part，不写 `index.md`。
- 新课程目录中，正文只放根目录；所有辅助文件放 `<COURSE_DIR>/_lathe/`。
- 第一部分使用 **4–7 个构建知识点**；地基与 §0 承接不占构建名额，但地基 + 承接 + 构建总章数 **≤9**。
- 课程地图覆盖完整课程；`course_plan` 只规划 3–12 个 Part，点级状态只写 canonical 知识表。
- 用户确认写前计划前不写正文。

## 协议

1. **解析配置并确认保存位置。** 按 SKILL.md 解析 `~/.lathe/config.json`。每次生成都展示默认基础目录并确认；不得静默采用。
2. **一轮分组提问。** 一次收集保存位置、slug、经验水平、主题新颖度、voice、至多一个澄清问题、仓库、工具版本、学习目标，以及“知识清单策略”三选一。除保存位置外均给建议值并标 `[默认]`。
3. **检查冲突。** 在研究前检查 `<保存位置>/<slug>/` 和 `tutorial_paths[slug]`；已有课程绝不覆盖，让用户选择改 slug、改为续写或取消。
4. **确定语言与主锚点。** 语言按 SKILL.md；主锚点从速查表选一个 id。默认 `plainspoken` 不读 voice.md。
5. **先研究。** 按 writing-core.md 的 `topic_novelty` 预算研究主题，锁定版本并建立关键事实覆盖。
6. **建立完整课程地图。** 根据主题、目标、研究结果和清单策略，先形成覆盖完整学习目标的知识点集合，再组织成 3–12 项 `course_plan`。每个 Part 项只含 part、标题、目标、前置；知识点逐行进入 canonical 表。
7. **选择 part-01。** 按 knowledge-ledger.md 的优先级与现有配额，从完整知识表选出 part-01：构建 4–7；地基/承接按各自额度，总章 ≤9。其余点按路线保留 `planned`，属于当前 Part 却装不下的改 `queued`；不要塞进 `next_hook`。
8. **写前确认。** 展示完整 `course_plan`、清单归一化/去重结果、part-01 选点、顺延、章数与闸门结果，等待用户确认。生成时不可用“直接写”或 `--no-confirm` 跳过。
9. **写入新布局。** 创建 `_lathe/`，写根目录 `part-01.md`、`_lathe/metadata.json` 与 `_lathe/knowledge-points.md`；正文按 writing-core.md 结构，在 H1 后插入未验证横幅，写清结束状态、下一部分起始状态、非目标和练习承接。不得回写或预写其他 Part。
10. **自检与试跑。** 文件落盘后执行 writing-core.md 的两轮自检，并运行 `part_lint.py`、`trial_run.py --run`、`ledger_check.py <COURSE_DIR> --receipt part-01.md` 和 `--continuity`。命令都传课程根目录；失败先修再交付。
11. **登记位置。** 保存到非默认基础目录时登记 `tutorial_paths[slug]`；默认基础目录无需重复登记。
12. **可选同步面试文档。** 仅本次含独立 `面试` / `interview` token 时，课程落盘后按 interview.md 创建 Part 1 分段；fallback 路径按 SKILL.md 的布局规则。

## 一轮分组提问

用一条消息列出以下项目。用户回复“可以”即采用所有默认值；只追问被明确否定的项。

1. **保存位置：** 展示 config 默认目录，必须取得答复。
2. **slug：** 提议 kebab-case 永久标识并确认。
3. **经验水平：** `beginner` / `familiar` / `experienced`；默认 `familiar`。
4. **主题新颖度：** `new` / `adjacent` / `familiar`；默认按经验映射，无法判断取更高新颖度。
5. **voice：** `plainspoken` `[默认]`、`companion`、`craftsman` 或自定义。
6. **澄清问题：** 主题确实含糊时最多一个；否则“无需补充” `[默认]`。
7. **仓库：** URL 与分支；独立课程为“无” `[默认]`。
8. **工具链版本：** 提议明确稳定版本并确认。
9. **学习目标：** 提议一句可评估目标并确认。
10. **知识清单策略：** 必须三选一：
   - **自动生成完整清单 `[默认]`**：基于目标和研究生成整门课的完整知识点集合；
   - **使用用户清单（粘贴或路径）**：读取本条消息中的清单或用户指定文件；外部文件只读；
   - **合并**：自动生成完整清单，再与用户粘贴/路径清单逐条归一化、拆分和去重。
11. **面试文档位置：** 仅带面试 token 且文档不存在时加入，展示 SKILL.md 三档解析结果。

用户清单或合并模式下，逐字保留用户原意到“备注”，所有条目归一化进**同一个** canonical 知识表。外部路径不是第二事实源；导入后后续只读知识表。若同时给了粘贴内容和路径，先让用户选一个用户来源，不能静默重复导入。

## slug 冲突

研究前检查 `<保存位置>/<slug>/`：

- 不存在：继续。
- 已存在：读取其 metadata 位置或 part 标题识别课程，停止写入并给出：换 slug、改为续写、取消。
- 同一 slug 已登记在其他目录：同时报告并提示 `/lathe 扫描` 可校正。

绝不覆盖已有 part 或任一位置的 metadata。

## 完整课程地图与写前确认

先把学习目标分解为完整知识点，再组织 Part，而不是只规划 part-01。确认消息至少包含：

```text
课程路线（3–12 Part）
1. <标题> — <目标>
...

写前计划确认（part-01）
① 清单：自动 / 用户 / 合并；归一化与去重 …
② 本部分讲：<ID 列表>（构建 N / 4–7；地基 F；承接 C；总章 T / ≤9）
③ 顺延：<ID> → queued（预计 Part N）
④ 后续 planned：<按 Part 分组的 ID>
⑤ 闸门/重规划：<仅触发时>
```

确认后才创建目录和正文。用户调整地图时先同步 `course_plan` 与知识表的“计划 Part”，再进入写作。

## 写入文件

在用户确认的保存位置创建：

```text
<COURSE_DIR>/
├── part-01.md
└── _lathe/
    ├── metadata.json
    └── knowledge-points.md
```

没有研究归档、验证结果或面试文档时不要预建空文件。

### `_lathe/metadata.json`

按 `metadata.md` 的 0.6.1 完整结构写入，不在本文件复制 schema。生成时至少确保：当前技能版本、`parts: ["part-01.md"]`、`part_versions`、3–12 项 `course_plan`、`status: "unverified"`、写作约束、来源、空或真实的接口变更，以及可从正文/知识表重建的 continuity。`verify_workspace` 使用规范规定的新布局路径；不要添加任何点级状态、ID 或练习承接镜像。

### `_lathe/knowledge-points.md`

使用 knowledge-ledger.md 的固定标题、进度行、六态统计和唯一连续八列表。最小示例：

```markdown
# 课程知识点与进度

进度：已完成 1 / 计划内 2（50%）
状态：planned 1 · queued 0 · taught 1 · self-study 0 · dropped_by_user 0 · duplicate 0

| ID | 知识点 | 来源 | 类型 | 计划 Part | 状态 | 已讲位置 / 承诺来源 | 备注 |
|---|---|---|---|---:|---|---|---|
| P1-1 | 建立可运行的最小主循环 | plan | main | 1 | taught | at:part-01.md#1. 跑通主循环 | |
| U-1 | 解释背压边界 | user | main | 2 | planned | — | 用户原文：背压什么时候发生 |
```

part-01 已讲点写 `taught` + `at:`；当前项溢出写 `queued`；后续路线点写 `planned`；重复点保留为 `duplicate`。数据行写完后重建进度与六态缓存。

## 开头、结尾与练习

- 开头直接进入具体场景、可核实主张、克制引文或读者困惑；禁止“在本教程中我们将”“欢迎来到”“让我们开始”。
- `## 接下来` 写衔接与结尾反思；`next_hook` 只缓存语境，不存知识点状态。
- 必做 3–5、选做 0–3，总数 ≤8；必做最多 2 道引入新概念，并按 knowledge-ledger.md 写成 `carry` 承诺。选做新概念只给线索与官方入口，默认不入表。
- `## 来源` 只列本部分实际引用来源。

## 交付

结果开头直接给 canonical 路径和进度，例如：

```text
知识表：<COURSE_DIR>/_lathe/knowledge-points.md
进度：已完成 X / 计划内 Y（Z%）；queued Q；下一项 Part 2「…」
```

随后粘贴覆盖回执、章数、试跑与账本检查结果，并报告：

- 教程路径与 `part-01.md`；
- 本次顺延/去重/用户处置；
- `/lathe 续写 <slug>`、`/lathe 验证 <slug>`、`/lathe 提问 <slug> part-01.md`；
- 带面试 token 时的实际面试文档路径。
