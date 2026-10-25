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

1. **吸收现有教程。** 先读 `metadata.json`，取 `voice`（复习材料沿用同一 voice）、`language`（保持同一正文语言）、`goal`（如有）、`continuity`（控制性示例与固定数字直接取自摘要，无需从正文重新提炼）、`knowledge_backlog` 与 `continuity.exercise_carry`（见下方「未讲条目」）。读取 `changed_interfaces`（如有）。**读取 `syllabus.json`（知识点账本，存在时）**——它是「哪些讲了、讲在哪，哪些还没讲」的权威记录。若教程目录存在 `research.md`，同时读取其中的 `## Open Threads Archive`、`## Changed Interfaces Archive`、**`## Self-study Backlog` 与 `## Covered Concepts Archive`**——前两节用于后续方向，后两节用于「整门课覆盖核对」与「已归档概念」；归档内容不是新教学内容，但**复习必须把它们算进覆盖范围**，否则长课程只能看到最近未被归档的概念。

   然后**读取全部常规部分的正文**——复习材料要逐部分回顾并原样摘录代码与检查点命令，这是本操作绕不开的成本。但两处可以省：
   - **跳过已有的 `-review` 复习材料**：旧复习材料对新复习无用，只需从 `parts` 数组知道它们占用了哪些编号。
   - **`continuity.part_titles` 已有标题时直接用**，不必为取标题而打开文件（正文仍需读，但不用重复提取）。

2. **确定复习材料编号。** 术语固定：**常规部分** = `part-NN.md`，**复习部分** = `part-NN-review.md`，两者共用同一条编号轴。新复习部分的编号取 `parts` 里**所有部分（含复习部分）的最大编号 + 1**，零填充 2 位，文件名 `part-<NN>-review.md`。例如 `parts` 为 `["part-01.md", "part-02.md", "part-03.md"]` 时得到 `part-04-review.md`；**同名文件已存在时顺延下一个编号**（此前复习过 → `part-05-review.md`），不停止、不覆盖，并在结果里说明「这是第 k 份复习材料，旧的 `part-MM-review.md` 保留」。
   编号只用于文件名；复习材料 H1 里的「截至 part-NN」**只取最后的常规部分**，不含复习部分（见下方结构模板）。

3. **写入复习材料** `part-<NN>-review.md`，结构如下：

   ```
   # 复习：<教程标题>（截至 part-<最后的常规部分编号，忽略 -review>）

   [引子——1 到 2 段：点明这份材料的用途：久未接触后快速找回状态]

   ## 逐部分回顾
   每个常规部分一个小节（### part-NN — <该部分一级标题>）：
   该部分构建了什么、核心概念 2-3 个、关键数字/配置、一个代表性代码片段或命令（摘自原文，不新写）。

   ## 自测：间隔检索
   5-8 个问题，覆盖各部分的关键概念——要求读者先自己回答再对照正文（问题后标注出处部分，如"见 part-02 §选举超时"）。不给答案。

   ## 重跑检查点
   列出各部分 `## 检查点` 的核心命令与预期输出（原样摘录），供读者在本地环境重新执行、确认手感仍在。

   ## 学习目标回顾（goal 字段存在时）
   对照 `goal` 说明当前已建立的能力，以及尚未覆盖的部分（如有）。若 `changed_interfaces` 非空，列出仍未闭合的接口变更；若 `open_threads` / `research.md` 归档有未决问题，列出 1-3 个最重要的。

   ## 还没讲到的（按 ID）
   **有账本时**：按 `syllabus.json` 列出所有不是 `taught` / `duplicate` 的条目，按状态分组（`queued` 欠着的 → `planned` 按大纲还没轮到的 → `self-study` 你选择自学的 → `dropped_by_user` 你删掉的），每条写一句「为什么没讲 / 计划何时讲（`plan_ref` 指向哪个 Part）」，末尾附一行账本各状态条数。**没有账本的旧教程**：按 `metadata.knowledge_backlog`（`core` 在前）与 `research.md` 的 `## Self-study Backlog` 列出，并提示下次续写会建立账本。**全部已讲时写「无——所有列入清单的知识点都已讲完」**，不要省略本节。这一段是「覆盖度」的唯一可见账本，读者据此判断这门课是否完整。

   ## 还可以继续深入的方向
   基于课程内容、`continuity.open_threads`、`next_hook`、`knowledge_backlog` 头部以及 `research.md` 的归档线索，给出 3-5 个延伸方向：
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

- 写入 `part-<NN>-review.md` 和更新 `metadata.json` 是唯一的文件写入操作；不编辑已有部分，**不写 `syllabus.json`**（复习只读账本）。
- 不引入新教学内容，不做网络研究，不修改 `status`、`tags`、`tools`、`sources`。允许写入的 metadata 字段仅限：`parts`、`model`、`lathe_version`、`continuity.part_titles` / `continuity.updated_at`，以及**原本缺失**的 `goal` / `language` / `style_anchor` / `experience_level`（补齐，不覆盖已有值）。
- 复习材料计入 `parts` 但**不参与验证**（verify 跳过 `-review` 文件），**也不写验证状态横幅**（它永远不会被验证）；后续常规续写的编号在所有部分（常规 + 复习）的最大编号上递增。
