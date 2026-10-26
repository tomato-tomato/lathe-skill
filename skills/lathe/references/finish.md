# 收尾教程

收尾生成一个总结 Part，不引入新教学内容。本文件是收尾操作的单一入口；常规续写不要加载它。

**先读：** 课程 metadata、canonical ledger、必要的当前布局 research；通过 A 步读取剩余点后，再加载 `writing-core.md` 与 `knowledge-ledger.md`。

### A. 先读剩余点，不拦截收尾

先按 metadata 位置解析布局，只读取实际 metadata、canonical ledger 和必要的当前布局 research 归档；不要先读正文。运行：

```text
python3 <SKILL_DIR>/scripts/ledger_check.py <COURSE_DIR> --finish
```

脚本会列出全部 `planned` / `queued` 剩余点，并给出总结必须写的提示模板。它**不再按 A/B 类拒绝收尾**：用户可以学完再收，也可以带着剩余点收尾，但后者必须在总结里留痕。

规则：

- 剩余点必须列全 ID；用户确认前不读正文、不写总结、不改 `status`。
- 用户可以选择：继续写一个 Part；直接收尾并写「未学完」提示；或把部分点明确改为 `self-study` / `dropped_by_user`。后两种状态只能由用户显式选择。
- 无法取得回复时停在门禁并原样报告选项，不写草稿或新增状态字段。
- 选择自学/删除只改 canonical ledger 的状态与备注；新课程改知识表，legacy 改旧 JSON point。不要写 research 镜像。
- legacy 账本缺失先回填并确认。

### B. 吸收课程

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

如果 canonical ledger 仍有 `planned` / `queued`，在 H1 之后加入：

```markdown
> [!WARNING]
> **完成状态：未学完（剩余 N 条知识点）。**
> 未讲清单见下方「未讲清单（按 ID）」。之后可以运行 `/lathe 续写 <slug>` 继续学习剩余知识点；续写会把课程重新开放为 `unverified`。
```

未讲清单直接按 canonical ledger 对所有非 `taught` / `duplicate` 行分组，逐 ID 说明未讲原因与捡回方式，并列六态总数。总结不写 `## 检查点`、`## 你将构建什么`、`## 前置条件`、`## 来源`、四个交接契约行或验证横幅。运行 `part_lint.py <总结文件> --kind finish`。

总结写入后运行：

```text
python3 <SKILL_DIR>/scripts/ledger_check.py <COURSE_DIR> --finish --receipt <总结文件>
```

脚本会校验「未学完」提示、全部剩余 ID 和「续写」继续学习提示；缺任何一项先补再交付。

### D. 收尾写回

- 新总结加入 `parts` 和 `part_versions`；`status` 设 `completed`（允许仍有 `planned` / `queued`）；更新模型与技能版本。
- canonical ledger 只执行用户在门禁明确选择的状态变化并刷新缓存/时间；不新增、不删除教学点。
- continuity 更新标题、时间、线程与完结衔接；总结没有新知识，不伪造 `covered_concepts`，该缓存仍从 taught points 重建。
- `course_plan` 保留；如收尾时路线已偏离，按需改写大纲；接口变更保持；未解决线程按 metadata.md 归档到当前布局 research。
- 运行 `ledger_check.py <COURSE_DIR> --finish --receipt <总结文件> --structure` 与 `--continuity`。
- 报告总结路径、canonical 路径、剩余点、最终进度和 `completed`；课程以后再次续写会自动重新开放，剩余点继续参与选点。

## 写入边界

- 只新增一个总结 `part-NN.md`，并原地更新当前布局的 metadata、canonical ledger 与按需 research 归档。
- 不编辑任何已有 `part-*.md` 正文，不回写旧检查点。
- 不新增、不删除教学知识点；只执行用户在门禁明确选择的状态变化。
- 不写面试分段；收尾不产出面试内容。
- 不运行 `/lathe 验证`，不写 verify result，不把收尾检查当验证。
- 完成后 `status` 设为 `completed`；后续续写会重新开放为 `unverified`，剩余点继续参与选点。
