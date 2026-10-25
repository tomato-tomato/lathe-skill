# 续写教程

为已有课程添加一个新 Part，并延续它的示例、数字、voice、风格锚点与正文契约。

**常规续写先读：** `<SKILL_DIR>/references/writing-core.md`、`knowledge-ledger.md`、`metadata.md`。收尾模式先用本文件与课程 metadata/canonical ledger 判门禁；通过后再加载写作规范和正文。

## 触发与边界

- 常规：`/lathe 续写|extend <slug> [指导]`
- 收尾：`/lathe 续写 收尾 <slug>`
- 每次只新增一个 `part-NN.md`；不写 `index.md`，不回改任何已消费的旧 part。
- 常规 Part 使用 **4–7 个构建知识点**；地基与 §0 承接不占构建名额，但地基 + 承接 + 构建总章数 **≤9**。
- 新课程辅助文件只写 `_lathe/`；legacy 全部原地读写，不迁移，不创建另一套布局。
- 已有面试文档默认同步本次教学 Part；`不同步面试` / `--no-interview` 跳过。收尾不产出面试分段。

## 常规协议

### 0. 按 metadata 位置解析布局

先定位 `<COURSE_DIR>`，再一次性判定：

| 布局 | metadata | canonical ledger | research | 面试 fallback |
|---|---|---|---|---|
| 新课程 | `_lathe/metadata.json` | `_lathe/knowledge-points.md` | `_lathe/research.md` | `_lathe/interview.md` |
| legacy | `metadata.json` | `syllabus.json` | `research.md` | `interview.md` |

两处 metadata 同时存在，或辅助文件跨布局混放：列出冲突路径并停止。不得按文件逐个回退。只有 part 而 metadata 缺失/损坏时按 metadata.md 自愈；legacy 只在旧位置重建。

### 1. 吸收现有课程

1. 读取实际 metadata 与 canonical ledger；有 shell 先运行 `ledger_check.py <COURSE_DIR>`。legacy 账本缺失时按 knowledge-ledger.md 推断、展示并确认后原地回填。
2. 判断 `continuity` 新鲜度：`updated_through` 等于最后常规 Part，用户未声明修改旧正文，且没有 part mtime 晚于实际 metadata mtime 超过 2 分钟。
3. 缓存可信时读取 metadata、最后一个常规 Part 全文、ledger 未结行；按需读取接口/线程涉及的小节。写 part-03/06/09…时仍全读审计。
4. 缓存不可信时读取全部常规 Part 与 canonical ledger，重建 continuity。`covered_concepts` 只从 ledger 中最近 24 个 `taught` 点重建，是缓存，不是覆盖证据。
5. 最后一个 Part 的“下一部分起始状态”和“本部分不覆盖”是起点契约；与 `next_hook` 冲突时以正文为准。上一部分练习承诺直接从 ledger 的 `promise:` / legacy 对应字段读取。

### 2. 读取约束

从 metadata 沿用：控制性示例、固定数字、隐喻状态、goal、course_plan、voice、language、style_anchor、experience、novelty、工具版本、仓库、接口变更与本地项目路径。不要重新选择或静默升级。

- `course_plan` 指定默认 Part 方向；canonical ledger 决定具体知识点及状态。
- `next_hook` 只提供衔接语境，不是点队列。
- 当前布局 research 只用于来源、接口归档、线程与勘误，不承载知识点状态。
- legacy 缺 `course_plan` 时可从目标、标题与衔接推断 3–12 项；先展示后写。新课程不得从 `next_hook` 生成隐藏知识点。

### 3. 确认本地项目路径

`local_project_path` 有值时轻确认沿用、换路径或跳过；无值时询问是否提供。提供后只读关键代码与目录了解真实进度，并在本次 metadata 写回。路径无效时告知并按教程契约续写。

### 4. 用户临时内容先入 canonical ledger

用户本次给出的临时主题、知识清单或“顺便讲”内容，必须在选点前归一化进当前布局的 canonical ledger：

- 新课程：在固定八列表新增 `来源=user` 行，分配稳定 ID，保留原文到备注；
- legacy：在 `syllabus.json` 新增兼容 point，保持未知字段与 JSON 格式；
- 拆分复合项，完全重复记 `duplicate`，部分重叠改为 `deepen`；
- 先写点及预定 Part，再参与配额，不把用户内容藏在 `next_hook`、research 或 metadata。

用户直接编辑表留下空 ID 时，本次写操作先分配 ID。用户删除整行时按 knowledge-ledger.md 区分主动删除与损坏；不确定就停止并确认。

### 5. 按硬优先级选本 Part

在同一配额池严格依次选择：

1. **本 Part 到期的 `promise:` 条目**；
2. **本次用户新增条目**；
3. **`queued`**，先进先出且本 Part 预计项优先；
4. **当前 `course_plan` 项的 `planned`**。

到期承诺硬优先于用户新增，不得被挤出。构建类型共用 4–7 名额；有待处理点时容量按 7。`foundation` 使用地基额度，`carry` 使用 §0 承接额度；两者不占构建名额但都计入总章 ≤9。容量不足时按优先级保留：后续路线项维持 `planned`，当前项或临时项转 `queued`。

到期承诺确实讲不成时保持/转 `queued`，保留原承诺来源，更新预计 Part，并在新正文和回执点名“未兑现”；不得静默留作到期 `planned`，也不得自行降级或删除。

### 6. 写前计划确认

有用户新增、顺延、去重、闸门、路线重规划、planned 变更或 legacy 首次回填时，展示 knowledge-ledger.md 的计划模板，并与本地路径确认合并成一条消息。计划至少列：

```text
写前计划确认（part-NN）
① 到期承诺：…
② 用户新增：…
③ queued：…
④ 当前 planned：…
⑤ 本部分选中：构建 N / 4–7；地基 F；承接 C；总章 T / ≤9
⑥ 顺延、去重、闸门与路线调整：…
```

拿到回复再写正文。用户明确“直接写”可跳过常规确认，但仍须先完成 ledger 入表、配额选择和闸门；生成规则不适用此豁免。

### 7. 研究新内容

只研究本 Part 新引入的内容，按 `topic_novelty` 使用 writing-core.md 预算。复用 metadata sources 与固定数字；跨 Part 来源笔记写当前布局 research。不得在那里维护自学、已讲、排队或练习承诺镜像。

### 8. 确定编号并写一个 Part

取 metadata `parts` 中所有课程/复习文件的最大编号 + 1，零填充；目标文件已存在则停止。写入根目录 `<COURSE_DIR>/part-NN.md`：

- H1 后插入未验证横幅，再写 `[!RECALL]`；
- 起点必须接上最后 Part 的文件、符号、命令与未完成项；接不上就停止说明，不静默改路线；
- 按 writing-core.md 的续写结构写，`## 接下来` 前加入 `## 目标达成回顾`；
- 先讲到期承诺，再讲用户新增、queued、planned；旧 queued/承诺章节开头回指来源；
- 上一部分存在档 2 时，在前置条件后写一个 §0 承接章，最多 2 条；档 3 与本次顺延按 ID 留痕；
- 写清本部分结束状态、下一部分起始状态、非目标与练习承接；
- 只修改新 Part，不回改旧正文，不因本次接口变化修补旧检查点；跨 Part 变更写 `changed_interfaces`；
- 完成两轮自检，运行 `part_lint.py` 与 `trial_run.py --run`。

### 9. 写后更新 canonical ledger

正文完成后，以事实更新同一 ledger：

- 已讲条目改 `taught`，写真实 `at:part-NN.md#<标题>` / legacy 等价位置与深度；
- 未讲成的到期承诺和当前项改/保持 `queued`，保留 promise 并更新预计 Part；
- 后续路线点维持 `planned`；新增练习承诺以 `exercise` + `carry` 入表；
- 去重、用户选择的自学/删除状态按规范写；模型不得自行设置；
- 新课程按数据行重建“进度”和六态统计缓存；legacy 刷新其账本时间与兼容字段。

先写回 canonical ledger，但此时不要运行对账：新 Part 还没加入 metadata `parts`，提前检查会把合法 `at:` 误报为悬空。不要生成点级 metadata 投影或 research 镜像。

### 10. 更新 metadata 与 continuity

读取实际 metadata 原地更新：

- `parts` 追加新文件，`part_versions[part-NN.md]` 记录当前版本；
- 来源去重追加；维护最多 8 条活跃 `changed_interfaces`，旧项归档到当前布局 research；
- continuity 只更新可重建缓存：控制性示例、固定数字、隐喻状态、open threads、`next_hook`、最近标题、时间；
- `covered_concepts` 从 canonical ledger 的最新 `taught` 行重建最近 24 条，不归档、不作为事实源；
- 知识点状态、排队与练习承诺不写入 continuity；
- 路线漂移时更新 Part 级 `course_plan` 并报告原因；补齐可推断缺字段；
- 更新本地项目路径、模型、当前技能版本，`status` 设 `unverified`；原为 `completed` 时课程重新开放；
- metadata 与 continuity 写回后，依次运行 `ledger_check.py <COURSE_DIR> --receipt part-NN.md` 和 `--continuity`；前者确认新 Part 已进入 `parts` 且写前计划逐点闭合，后者检查缓存预算。失败先修再交付，超限只修剪缓存，不压缩正文。

按目录直接操作时不登记 config；否则仅在必要时补 `tutorial_paths`。

### 11. 同步面试文档

metadata 与 ledger 写完后处理：

| 情形 | 行为 |
|---|---|
| 已有面试文档 | 默认只追加本次教学 Part 分段并更新进度行；不动已有分段 |
| 不存在且带面试 token | 按 interview.md 确认位置后创建；历史缺口先让用户选“补全部/只写当前” |
| 不存在且无 token | 跳过，不创建 |
| 带 `--no-interview` | 跳过 |

外部配置路径优先；fallback 必须按步骤 0 的布局。同步失败不回滚课程续写，只报告原因。

### 12. 交付

结果开头直接报告 canonical 路径和进度：

```text
知识表：<实际 canonical 路径>
进度：已完成 X / 计划内 Y（Z%）；queued Q；下一路线项 …
```

随后粘贴本部分覆盖、顺延/去重、承诺兑现、计划/实写章数、试跑与 ledger 回执。报告新 Part 路径、课程是否重新开放、路线漂移、continuity 重建和面试同步结果。

## 收尾模式

收尾生成一个总结 Part，不引入新教学内容。

### A. 先从 canonical points 判门禁

先按 metadata 位置解析布局，只读取实际 metadata、canonical ledger 和必要的当前布局 research 归档；不要先读正文。运行：

```text
python3 <SKILL_DIR>/scripts/ledger_check.py <COURSE_DIR> --finish
```

直接从 canonical points 分两类：

| 类别 | 定义 | 选择 |
|---|---|---|
| A 类真欠账 | `queued` + 已到期但仍未兑现的 promise | ① 补写涉及路线的 Part；② 用户逐条改为 `self-study`；③ 用户确认强制完结 |
| B 类未开工路线项 | 其余 `planned`，即尚未推进的 course_plan 内容 | ④ 按现状完结 `[默认]`，保留 `planned`；也可选 ①/②/③ |

规则：

- A 类非空时不给 ④；A 为空、只有 B 时默认 ④。
- 缺口必须列全 ID；用户确认前不读正文、不写总结、不改 `status`。
- 无法取得回复时停在门禁并原样报告选项，不写草稿或新增状态字段。
- 选择自学只改 canonical ledger 的状态与备注；新课程改知识表，legacy 改旧 JSON point。不要写 research 镜像。
- 选择强制或按现状完结时未处理行保持原状态。legacy 账本缺失先回填并确认。

### B. 门禁通过后吸收课程

此时才加载 writing-core.md 与 knowledge-ledger.md。continuity 可信时读它、最后常规 Part 全文，并从其他 Part 读取一级/二级标题；不可信时全读并重建。research 只读取接口、线程与勘误等允许归档；旧格式的点级镜像仅为历史兼容，忽略且不续写。收尾不询问本地项目，不做新研究，除非必须核实关键事实。

### C. 写总结 Part

编号仍取最大编号 + 1。总结固定七节：

1. `## 全课程回顾`
2. `## 知识图谱`
3. `## 目标对照`
4. `## 未讲清单（按 ID）`
5. `## 回顾自检`
6. `## 练习方向`
7. `## 寄语`

未讲清单直接按 canonical ledger 对所有非 `taught` / `duplicate` 行分组，逐 ID 说明未讲原因与捡回方式，并列六态总数。总结不写 `## 检查点`、`## 你将构建什么`、`## 前置条件`、`## 来源`、四个交接契约行或验证横幅。运行 `part_lint.py <总结文件> --kind finish`。

### D. 收尾写回

- 新总结加入 `parts` 和 `part_versions`；`status` 设 `completed`；更新模型与技能版本。
- canonical ledger 只执行用户在门禁明确选择的状态变化并刷新缓存/时间；不新增、不删除教学点。
- continuity 更新标题、时间、线程与完结衔接；总结没有新知识，不伪造 `covered_concepts`，该缓存仍从 taught points 重建。
- `course_plan` 保留；接口变更保持；未解决线程按 metadata.md 归档到当前布局 research。
- 运行 `ledger_check.py <COURSE_DIR>` 与 `--continuity`。
- 报告总结路径、canonical 路径、门禁选择、最终进度和 `completed`；课程以后再次续写会自动重新开放。

## 写入边界

- 教程侧只新增本次 `part-NN.md`，并原地更新当前布局的 metadata、canonical ledger 与按需 research 归档。
- 不编辑任何已有 `part-*.md` 正文；接口演进靠新正文与 metadata 记录，不回写历史。
- 面试文档只追加新分段和对应进度；不得自动改已有分段。
- 不运行 `/lathe 验证`，不写 verify result，不把交付前试跑当验证。
- 常规续写不得自行把课程设为 `completed`；continuity 更新不得跳过。
