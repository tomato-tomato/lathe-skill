---
name: scan
description: 扫描目录发现未登记的教程并写入 config，同时清理悬空条目
---

# 扫描并登记教程

把**存在于磁盘但不在 `~/.lathe/config.json` 视野内**的教程登记进来，并清理指向已消失目录的悬空条目。

**为什么需要这个操作：** 生成新教程时会自动登记位置，但教程也会通过其他途径出现——手工拷贝、`git clone` 拉下他人仓库、移动目录、跨机器同步。config 里的"已使用过"扫描分支**只在 config.json 不存在时触发**，所以 config 一旦建立，这些教程就永久不可见：`/lathe 列表` 看不到它们，`/lathe 续写 <slug>` 会落到"列出已知 slug"的兜底分支。本操作是这些情况的唯一修复入口。

**触发格式：**
```
/lathe 扫描|scan [目录1] [目录2] ...
```

中文关键词 `扫描`、`登记`、`注册` 与英文 `scan`、`register`、`sync` 等价。目录参数可省略。

---

## 建立 config（config.json 不存在时）

任何操作解析配置时若发现 `~/.lathe/config.json` 不存在，走此流程（`<SKILL_DIR>/SKILL.md`"教程存储路径配置"指向这里）——它同时替代了本次扫描：

1. 先问 *"这是你第一次使用 Lathe，还是之前已经生成过教程？"*，按回答分支：
   - **第一次使用：** 询问 *"教程默认存储在 `~/others/lathe_tutorials/`，要使用其他位置吗？"*，确认后创建 `~/.lathe/` 并写入 config（`tutorial_paths` 为空对象）。
   - **已经使用过：** 请用户提供已有教程的存放位置（一个或多个目录），按下方协议的枚举与分类规则扫描、展示结果并经用户确认后写入 config：`tutorials_base_path` 取教程最多的位置（并列时请用户指定），`tutorial_paths` 逐个记录每个 slug 的位置。
2. 完成后继续用户原本的调用意图。

---

## 协议

1. **确定扫描范围。**
   - **给了目录参数** → 扫描这些目录（逐个展开 `~`，不存在的目录告知用户并跳过）。
   - **未给目录参数** → 扫描已知目录的并集：`tutorials_base_path` + `tutorial_paths` 的所有值（去重）。随后询问用户是否还有其他位置需要一并扫描（一次询问，用户答"没有"就继续）。
   - **config.json 不存在** → 走本文件"建立 config（config.json 不存在时）"一节（这也是 SKILL.md 解析配置时的落点）；该流程即完成本次扫描登记，无需再重复扫描。

2. **枚举候选教程目录。** 在每个扫描目录下列出子目录，判定为教程的条件：**含 `metadata.json` 或含至少一个 `part-*.md`**。排除：
   - `voices/`（自定义 voice 目录，非教程）；
   - **以 `.` 开头的隐藏目录**——尤其是验证工作区 `.lathe-verify/`；
   - 教程目录内部的嵌套目录（只扫一层子目录，不递归进教程内部）。

3. **对每个候选分类。** 用 `metadata.json` 的 `slug` 字段作为身份（缺失时用目录名）：

   | 情况 | 分类 |
   |------|------|
   | 未在 `tutorial_paths` 中，且 `metadata.json` 完好 | 🆕 **待登记** |
   | 未在 `tutorial_paths` 中，且 metadata 缺失/损坏 | ⚠️ **待登记 + 需自愈** |
   | 已登记且路径一致 | ✅ 已是最新，不动 |
   | 已登记但 `tutorial_paths` 里的路径与实际位置不同 | 🔀 **待更正路径**（教程被移动过） |
   | 同一 slug 在多个目录下都存在 | ⚠️ **副本冲突** |

4. **检测悬空条目。** 遍历 `tutorial_paths` 的每个条目，检查 `<目录>/<slug>/` 是否仍然存在且仍是教程目录。不存在的记为 🗑️ **悬空**（教程已被删除或移动）。同样检查 `tutorials_base_path` 目录本身是否存在。

5. **展示扫描报告并请求确认。** 一次性展示全部结果，不要逐条询问：

   ```
   扫描了 2 个目录，发现：

   🆕 待登记（3）
   - todo-cli-rust — 用 Rust 构建命令行待办事项应用（5 个部分）｜~/projects/tutorials
   - raft-go — 用 Go 实现 Raft（2 个部分）｜~/projects/tutorials
   - wasm-jit ⚠️ metadata 缺失，发现 3 个 part 文件｜~/others/lathe_tutorials

   🔀 待更正路径（1）
   - taskr：config 记录 ~/others/lathe_tutorials，实际在 ~/projects/tutorials

   🗑️ 悬空条目（1）
   - old-experiment：config 指向 ~/others/lathe_tutorials，该目录已不存在

   ⚠️ 副本冲突（1）
   - taskr 同时存在于两个目录，需要你指定保留哪一个作为登记位置

   要应用这些变更吗？（可以只应用部分——告诉我跳过哪些）
   ```

   - 副本冲突**必须**由用户指定保留哪个位置，不要自行猜测。
   - metadata 缺失的教程：先登记位置，并告知可用 `/lathe 标签 <slug>` 等写入型操作触发自愈重建（见 `<SKILL_DIR>/references/metadata.md`"metadata.json 自愈"）。**本操作不主动重建 metadata**——那需要逐个教程确认推断字段，会把一次批量操作拖成长对话。

6. **写入 config.json。** 用户确认后：
   - 待登记与待更正的 slug 写入/更新 `tutorial_paths`；
   - 悬空条目从 `tutorial_paths` 中删除；
   - `tutorials_base_path` 保持不变——**除非**它已不存在，此时请用户指定新的默认目录；
   - 未获确认的条目保持原状。

7. **报告结果**：登记了几个、更正了几个、清理了几个悬空条目，并提示接下来可以 `/lathe 列表` 查看完整清单。

---

## 边界

- **唯一写入的文件是 `~/.lathe/config.json`。** 不创建、不修改、不删除任何教程文件或 `metadata.json`。
- **不重建 metadata**——只识别并报告缺失，重建由用户发起写入型操作时按自愈协议执行。
- **不删除任何磁盘内容。** "清理悬空条目"仅指移除 config 里的失效映射；教程目录本身若存在就绝不触碰。
- 未经用户确认不写入 config。
