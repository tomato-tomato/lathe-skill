# 复习教程

为久未学习、想先复习再精进的读者生成一份结构化复习材料。复习**不改变课程方向**：不引入新教学内容，不推进"接下来"的线索，只是把已有部分沉淀为可自测的回顾。

**先读共享文件：** 本操作需要 `<SKILL_DIR>/references/writing-core.md` 中的 voice 应用规则；不需要其中的教程结构（复习材料有自己的结构，见下方）。

**触发格式：**
```
/lathe 复习|review <slug>
```

中文关键词 `复习`、`回顾` 与英文 `review`、`revise`、`recap` 等价。

**分支——面试文档模式：** 若参数含**独立的** `面试` / `interview` token，本操作**转为面试文档模式**，改按 `<SKILL_DIR>/references/interview.md` 执行（粒度可选 `part-NN`；文档不存在时会先与你确认存储位置，文档已存在但不完善时会先与你确认补写范围）。**无该 token 时，下方协议完全不变。**

## 协议

0. **解析教程位置。** 按 `<SKILL_DIR>/SKILL.md`"教程位置解析规则"找到该 slug 的实际目录。**若 `metadata.json` 缺失或损坏**，先执行 `<SKILL_DIR>/references/metadata.md`"metadata.json 自愈"，重建确认后再继续。

1. **吸收现有教程。** 先读 `metadata.json`，取 `voice`（复习材料沿用同一 voice）、`language`（保持同一正文语言）、`goal`（如有）、`continuity`（控制性示例与固定数字直接取自摘要，无需从正文重新提炼），并读取 `changed_interfaces`（如有）。若教程目录存在 `research.md`，同时读取其中的 `## Open Threads Archive` 与 `## Changed Interfaces Archive`，用于后续方向和目标回顾；归档内容不是新教学内容。

   然后**读取全部常规部分的正文**——复习材料要逐部分回顾并原样摘录代码与检查点命令，这是本操作绕不开的成本。但两处可以省：
   - **跳过已有的 `-review` 复习材料**：旧复习材料对新复习无用，只需从 `parts` 数组知道它们占用了哪些编号。
   - **`continuity.part_titles` 已有标题时直接用**，不必为取标题而打开文件（正文仍需读，但不用重复提取）。

2. **确定复习材料编号。** 取 `parts` 数组中所有部分的最大编号 + 1（零填充 2 位），文件名附加 `-review` 后缀：`part-<NN>-review.md`。例如 `parts` 为 `["part-01.md", "part-02.md", "part-03.md"]` 时，复习材料是 `part-04-review.md`；若 `part-04-review.md` 已存在（此前复习过），取下一个编号（`part-05-review.md`）。**检查同名文件是否已存在**，已存在则告诉用户并停止。

3. **写入复习材料** `part-<NN>-review.md`，结构如下：

   ```
   # 复习：<教程标题>（截至 part-<最后常规部分编号>）

   [引子——1 到 2 段：点明这份材料的用途：久未接触后快速找回状态]

   ## 逐部分回顾
   每个常规部分一个小节（### part-NN — <该部分一级标题>）：
   该部分构建了什么、核心概念 2-3 个、关键数字/配置、一个代表性代码片段或命令（摘自原文，不新写）。

   ## 自测：间隔检索
   5-8 个问题，覆盖各部分的关键概念——要求读者先自己回答再对照正文（问题后标注出处部分，如"见 part-02 §选举超时"）。不给答案。

   ## 重跑检查点
   列出各部分 `## 检查点` 的核心命令与预期输出（原样摘录），供读者在本地环境重新执行、确认手感仍在。

   ## 学习目标回顾（goal 字段存在时）
   对照 `goal` 说明当前已建立的能力，以及尚未覆盖的部分（如有）。

   ## 还可以继续深入的方向
   基于课程内容、`continuity.open_threads`、`next_hook` 以及 `research.md` 的归档线索，给出 3-5 个延伸方向：
   每个方向一段话——是什么、为什么值得、从哪个部分的基础出发。
   末尾说明：想继续时调用 /lathe 续写 <slug>（可附带方向指导）。
   ```

   - 复习材料**不做新的网络研究**——内容全部来自已有部分；摘录保持原文精确。
   - 不使用 `> [!PREDICT]` 等教学标注（`[!RECALL]` 除外，最多 1 个）。

4. **更新 `metadata.json`：**
   - 将复习材料文件名追加到 `parts` 数组；
   - 更新 `model` 与 `lathe_version` 字段；
   - **`continuity` 只更新 `part_titles`（加入本复习材料）与 `updated_at`**——`updated_through` **不变**（它追踪常规教学进度，复习不推进进度）；`covered_concepts`、`next_hook` 等一律不动；
   - `goal`、`language`、`style_anchor`、`experience_level` 等字段缺失时可顺带补上（推断依据来自已读的正文）；
   - **`status` 不变**——复习不改变课程状态：`verified` 保持 `verified`，`completed` 保持 `completed`（复习不等于重新开放课程；只有续写新内容才会撤销完结，见 `<SKILL_DIR>/SKILL.md`"status 状态机"）；
   - 写回文件。

5. **告诉用户**复习材料已生成——文件路径、建议的使用方式（先自测再重跑检查点），以及两个后续选项：
   - 状态尚好、想继续精进 → `/lathe 续写 <slug>`；
   - 课程已完结且目标已达成、无需继续 → 保持现状即可。

## 边界

- 写入 `part-<NN>-review.md` 和更新 `metadata.json` 是唯一的文件写入操作；不编辑已有部分。
- 不引入新教学内容，不做网络研究，不修改 `status`、`tags`、`tools`、`sources`。允许写入的 metadata 字段仅限：`parts`、`model`、`lathe_version`、`continuity.part_titles` / `continuity.updated_at`，以及**原本缺失**的 `goal` / `language` / `style_anchor` / `experience_level`（补齐，不覆盖已有值）。
- 复习材料计入 `parts` 但**不参与验证**（verify 跳过 `-review` 文件）；后续常规续写的编号在所有已有部分（含复习材料）的最大编号上递增。
