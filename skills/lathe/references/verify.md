# 验证教程

像读者一样在教程目录下的验证工作区（`.lathe-verify/`）中按照已存储的教程逐步执行，并记录它是否确实可用。

本操作**对教程内容默认只读**。唯一例外是**版本冲突修复**（见下方专节）和**part 顶部的验证状态横幅**：前者经用户确认后可最小化修改冲突相关内容，后者只能替换/移除 `lathe:verify-status` 标记块。常规写入仅限：`verify-result.json`、`metadata.json` 的 `status` 字段、`verify_workspace` 字段、仅因横幅变化而刷新的 `continuity.updated_at`，以及状态横幅。

## 代码块类型（最小约定）

代码块 fence 的 info string 可带类型标记：

| 标记 | 含义 | verify 行为 |
|------|------|-------------|
| `runnable` | 完整可运行/可编译的单元 | 执行 |
| `fragment` | 片段；前文应写明属于哪个文件、插在哪里、与哪些块组合 | 跳过，不单独执行 |
| `exercise` | 练习/填空；应有参考答案或检查方式 | 跳过，不执行 |
| `text` / `output` | 非执行文本：预期输出、文法、文件树、日志、树形 | 跳过，不占步骤号 |
| `expected_failure` | 故意失败的命令/示例；前文写明预期退出码/错误 | 执行；预期非零退出；意外成功记失败 |
| 未标记 | 兼容旧教程，按 `runnable` 处理 | 执行 |

语法：在语言标识后追加类型词，例如 `rust runnable`、`rust fragment`、`rust exercise`、`bash expected_failure`、`text` / `output`。`fragment` 的文件与接缝说明写在前文，不塞进 fence；`expected_failure` 的预期退出码/错误写在前文。

同一文件的完整代码如果被拆成多个 `fragment`，教程必须另外提供一个覆盖最终状态的 `runnable` 块或检查点；verify 不自动拼装 fragments，也不把 `exercise` 当完整代码执行。

## 验证状态横幅

按 `<SKILL_DIR>/SKILL.md` 的「验证状态横幅」维护。verify 只允许改动 `<!-- lathe:verify-status:start -->` 与 `<!-- lathe:verify-status:end -->` 之间的内容，不得改正文。

- 本次实际执行且**通过**的部分：移除整个标记块，不写“已验证”正面横幅。
- 本次实际执行且**失败**的部分：写 WARNING，包含 `failed_step` 和错误摘要。
- 本次实际执行且**跳过**的部分（`parts` 中状态为 `skipped`）：写 NOTE，包含跳过原因。全局 `skipped` 但没有 `parts` 时不改横幅。
- **未执行**或**增量复用跳过**（`skipped_reuse`）的部分：不改横幅。
- 旧 part 没有标记块：失败/跳过时在 H1 之后插入，通过时不添加。
- **标记冲突保护：** 如果发现多个 `lathe:verify-status` 块、标记嵌套、或缺少 `end`，停止写入该 part，报告冲突；不要猜测替换。
- **先更新横幅，再写 `verify-result.json` 的 `checked_at`。** 否则 part 的 mtime 会晚于 `checked_at`，下次增量复用会误判为“内容已变更”。

## 协议

1. **阅读教程元数据。** 按 `<SKILL_DIR>/SKILL.md`"教程位置解析规则"定位该教程目录，读取其 `metadata.json`，获取部分列表、工具和当前状态。**若 `metadata.json` 缺失或损坏**，先执行 `<SKILL_DIR>/references/metadata.md`"metadata.json 自愈"：用户确认重建后再继续验证；用户拒绝则终止并说明。后文中该教程的文件均以定位到的目录为准。

   **本操作不需要 writing-core.md**——验证不写教程正文，不加载写作规则。

2. **版本一致性静态预检（动态执行之前）。** 这一步不运行任何代码，专门捕捉"示例声明的版本与文本介绍的特性相冲突"这类问题：
   - **提取三类版本信息并两两比对：**
     1. `metadata.json` 中 `tools` 锁定的工具链版本；
     2. 各部分配置代码块中声明的版本（如 `Cargo.toml` 的 `edition`/依赖版本、`package.json`、`go.mod`、`build.zig.zon` 等）；
     3. 教程文本介绍和示例代码实际使用的语法/特性/API 所要求的最低版本。
   - **典型冲突模式：** `Cargo.toml` 声明 `edition = "2024"` 但测试代码按 2021 语义编写；文本介绍某特性但该特性在锁定版本尚未发布；依赖包的 API 在声明的包版本中不存在或签名不同。
   - **不凭记忆断言特性的引入版本。** 不确定时查阅官方 changelog/release notes 确认。
   - **发现冲突：** 记入冲突清单，进入下方**版本冲突修复流程**；修复完成（或用户拒绝修复）后再开始动态执行。预检能提前拦截大部分版本问题，避免动态执行阶段才发现。

2b. **改动面静态预检（有 `changed_interfaces` 时）。** 读取 `metadata.json` 的活跃 `changed_interfaces`，只对本次待执行部分逐条核对；被增量复用跳过的部分继承上次结果，不重复核对：

   - `call_sites` 中的每个调用点，是否在教程中有对应代码块、插入位置，或明确的“无需改”说明；
   - 当前部分的 `runnable` 代码块中，是否还出现该条目的 `from` 旧签名/旧契约（出现在正文解释里不算，出现在 `runnable` 块里算）；
   - 新签名/新契约 `to` 是否至少出现在代码块或改动面表中；
   - 条目缺少必要字段（file/symbol/from/to/call_sites/part）时，记为 metadata 风险并报告；
   - 若 `research.md` 的 `## Changed Interfaces Archive` 中有 `active (overflow)` 条目且涉及本次部分，同样按上述规则核对；
   - `changed_interfaces` 缺失或为空数组时跳过本步。

   **判定：** 调用点既没有代码块/插入位置、也没有“无需改”说明，或旧签名仍出现在 `runnable` 块中，或 `to` 完全找不到，记该部分 `failed`（改动面不完整），并在报告中列出文件/符号/调用点。不要自动推断签名，也不要替读者改代码。

2c. **代码块结构预检。** 对本次待执行部分扫描代码块：

   - 每个 `fragment` 是否有前文说明（属于哪个文件、插在哪里、与哪些块组合），且同部分存在覆盖最终状态的 `runnable` 块或检查点；否则记该部分 `failed`。
   - 每个 `exercise` 是否有参考答案或检查方式；否则记该部分 `failed`。
   - 只做结构检查，不执行 `fragment` / `exercise`。

   结构不完整时，在报告中列出块所在位置和缺失项；不要为了让验证通过而把 fragment/exercise 改成 runnable。

3. **标记为进行中。** 在该教程目录中写入 `verify-result.json`：
   ```json
   {
     "status": "verifying",
     "checked_at": "<当前 ISO 8601 时间戳>"
   }
   ```

   **若读取时发现已有一份 `status: "verifying"` 的旧结果**（上次验证中途中断）：读取其中的逐部分明细用于增量判定，然后正常覆写为本次的 `verifying`——不要因存在陈旧的 `verifying` 而报错或终止。本次验证结束时写入终态（`verified`/`failed`/`skipped`）即完成复位。

4. **准备验证工作区（持久化复用）。** 工作区固定为该教程目录下的隐藏目录 **`.lathe-verify/`**，教程要求读者创建的所有内容都在其中进行，不在用户的项目中：

   - **先判断全量/增量。** 若满足任一条件，忽略增量，从 `part-01` 全量执行：
     1. 用户消息含单独的 `全量` / `full` token；
     2. 最后一个待验证的**常规 part**（跳过 `-review`）编号是 3 的倍数（`part-03` / `06` / `09`…）；
     3. 旧 `verify-result.json` 的 `changed_interfaces_snapshot` 与当前 `metadata.changed_interfaces` 不一致（旧结果没有 snapshot 且当前非空也算）；
     4. 旧结果缺失/损坏，或全局 `verifying` 且没有可复用的逐部分结果。
     全量时结果记 `mode: "full"`；增量时记 `mode: "incremental"`。
   - **工作区不存在** → 创建它，从 `part-01` 起全量执行；同时在 `metadata.json` 中写入 `verify_workspace` 字段（结构见 `<SKILL_DIR>/references/metadata.md`）向用户说明该目录的作用。
   - **工作区已存在且允许增量** → **增量复用**，不重新生成已有代码：读取 `verify-result.json` 的逐部分明细确定执行范围——上次 `passed` 且对应 `part-NN.md` 自 `checked_at` 后未被修改（比较文件修改时间）的部分跳过；从第一个需要（重）执行的部分（`failed` / `not_run` / 内容已变更 / 新增部分）开始顺序执行，继承工作区内已有的文件状态与依赖产物（已下载的依赖、编译缓存直接复用）。
   - **级联失效：** 如果本次从 `part-k` 开始重跑（`k` 不是 `part-01`），`part-k` 之后的所有常规 part 默认不可复用，按顺序重跑；除非用户明确要求“只跑变更部分”，并在报告中标注“后续 part 未重跑”的风险。原因：后续 part 可能依赖 `part-k` 的代码、接口或状态。
   - **工作区状态与教程不符**（关键文件缺失、工具链已变更等）→ 放弃增量，清空工作区后从头全量执行。

   **针对仓库的教程：** 如果 `metadata.json` 的 `repo` 字段非空，先将该仓库的 `repo_branch` 分支浅克隆到工作区内（已存在则更新到分支最新），在克隆目录中执行教程步骤。克隆失败（无网络、无权限）记为 `skipped` 并说明原因。

   **安全护栏：**
   - 所有命令只在验证工作区内执行，绝不碰用户项目或全局状态。
   - 遇到需要 `sudo`、全局安装（如 `npm install -g`、`cargo install`）、删除工作区之外文件、或修改系统配置的步骤：**先向用户确认**，未获确认则记为 `skipped` 并说明原因。
   - 长时间运行的命令（服务器、watch 模式）后台运行并验证后终止；单条命令超过约 5 分钟无进展视为异常，中断并记录。

5. **按顺序跟随需要执行的部分。** 按步骤 4 确定的范围，阅读该教程目录下对应的 `part-NN.md`。

   > **只读需要执行的部分。** 被增量复用跳过的部分（上次 `passed` 且文件未修改）**不要读取其文件内容**——既不执行就不需要其正文。只需从 `verify-result.json` 继承它们的 `passed` 状态写入本次结果。同样，步骤 2 的版本预检只需检查本次待执行部分的配置与代码块。

   **跳过文件名含 `-review` 后缀的复习材料**（回顾性内容，无可执行新步骤），结果中记为 `not_applicable` 或省略。安装前置条件，按顺序创建文件并粘贴 `runnable` 代码块，然后运行 `## 检查点` 命令并与声明的预期输出比较。
   - **只把 `runnable` / `expected_failure` 代码块和检查点命令视为可执行面。** `fragment` / `exercise` / `text` / `output` 跳过，不改写、不猜测、不单独粘贴；在结果/报告中说明跳过了哪些块及原因。
   - **`expected_failure` 必须按预期失败执行：** 命令意外成功、或错误/退出码与教程声明不一致，记该块失败；符合预期则通过，并在报告中列为“预期失败”。
   - **`runnable` 块中若出现 `...` 省略行，直接记该块失败**（代码不完整，不区分是否解释），不要猜测省略内容后继续执行。无关样板应放在 `fragment` 块。
   - **`fragment` 必须能说明文件与接缝。** 前文没有写清文件/插入位置的，记为 `failed` 或在报告中明确提示“片段缺少接缝说明”。
   - **`exercise` 不直接执行。** 如果提供了参考答案或检查方式，可人工核对；没有则提示读者自行核对，不把练习块当完整代码。
   - **有代码改动但没有完整 `runnable` 块或检查点的部分，记为 `failed`**（缺少可执行面），除非该部分明确是纯概念/纯回顾内容。
   - **步骤编号定义：** 每个部分内，只对 `runnable` / `expected_failure` 代码块和检查点命令按出现顺序统一编号（从 1 开始）——这就是结果中 `failed_step` 的含义；`fragment` / `exercise` / `text` / `output` 不占步骤号。
   - **跳过教学性和溯源性标注** —— `> [!PREDICT]`、`> [!RECALL]` 和 `> [!UNVERIFIED]` 不是可验证的步骤。
   - **旧签名提示（有 `changed_interfaces` 时）：** 对活跃条目的 `from` 旧签名，在验证工作区或 `local_project_path` 中做一次 grep；命中旧调用点且清单中没有“无需改”说明时，记为风险/失败提示。只做提示，不自动推断签名。
   - **输出归一化：** 比较预期输出时，先去除行尾空白、忽略空行差异，并替换教程明确声明为易变的时间戳/随机 ID/绝对路径；只用于教程声明的不稳定值，不能掩盖真实差异。
   - **报错时先做归因分类：** 判断是否属于版本冲突类错误（编译器提示特性不可用、edition/语法不匹配、API 在该版本不存在）——是则进入**版本冲突修复流程**，而不是直接记 `failed`；不是版本问题才按常规失败处理。
   - **逐部分记录结果**：某部分失败后停止后续部分（后续依赖失败状态，继续无意义），未执行的部分记为 `not_run`。

6. **先更新验证状态横幅，再更新该教程目录中的 `verify-result.json` 记录结果。** 对本次实际执行的部分按上文「验证状态横幅」更新/移除横幅；未执行或增量复用跳过的部分不改。若本次**只**改了状态横幅、没有版本冲突修复等正文改动，刷新 `metadata.continuity.updated_at` 为当前时间，避免下次续写把横幅写入误判为手工编辑；如果改了正文，保留旧 `updated_at`，让续写按手工编辑重建。然后写入结果，包含整体状态、逐部分明细、`mode`（`full` / `incremental`）和 `changed_interfaces_snapshot`（当前活跃 `changed_interfaces` 的 JSON 副本；空数组也要写）。下面示例为简洁省略了后两个字段：

   - **一切正常（含经修复后通过）：** 若某部分经版本冲突修复后通过，用 `fixes` 数组记录修复内容；复习材料用 `not_applicable`；增量复用跳过的部分保留其 `passed` 并可标 `"skipped_reuse": true`：
     ```json
     {
       "status": "verified",
       "checked_at": "<ISO 8601 时间戳>",
       "parts": [
         {"part": "part-01.md", "status": "passed", "skipped_reuse": true},
         {"part": "part-02.md", "status": "passed", "fixes": ["Cargo.toml 锁定 edition 2024，但测试代码按 2021 语义编写；已将测试代码改写为 edition 2024 写法"]},
         {"part": "part-03-review.md", "status": "not_applicable"}
       ]
     }
     ```

   - **缺少必需工具或需要未获确认的敏感操作**（这不是失败——意味着"无法在此处运行"）：
     ```json
     {
       "status": "skipped",
       "checked_at": "<ISO 8601 时间戳>",
       "error": "未安装必需工具：<工具名>",
       "parts": [
         {"part": "part-01.md", "status": "skipped", "reason": "未安装必需工具：<工具名>"}
       ]
     }
     ```

     如已确定哪些部分被跳过，列入 `parts`；无法确定时可省略。全局 `skipped` 且没有 `parts` 时，不更新任何横幅，保留原有的“未验证”警告。

   - **确实出现问题**（输出错误、代码无法编译、步骤自相矛盾）：
     ```json
     {
       "status": "failed",
       "checked_at": "<ISO 8601 时间戳>",
       "parts": [
         {"part": "part-01.md", "status": "passed"},
         {"part": "part-02.md", "status": "failed", "failed_step": 3, "error": "<错误信息或不匹配的输出>"},
         {"part": "part-03.md", "status": "not_run"}
       ]
     }
     ```

7. **同步 `metadata.json` 的 `status` 字段**，保持两处状态一致：
   - 验证通过 → `"status": "verified"`；
   - 验证失败 → `"status": "unverified"`（失败明细已在 verify-result.json 中）；
   - 跳过 → 不改动 `status`。
   - **例外：`completed` 不降级。** 原 `status` 为 `completed`（已收尾完结）时，验证通过**保持 `completed`**（不写回 `verified`，完结是更强的状态）；验证失败则写 `unverified` 并向用户说明完结标记已因验证失败而撤销。验证结果的真实状态始终以 `verify-result.json` 为准。

8. **向用户报告**发生了什么——本次是 `full` 还是 `incremental`、是否发生级联重跑、验证通过（含应用了哪些版本冲突修复、增量复用时跳过了哪些部分或哪些后续 part 未重跑）、跳过（以及缺少哪个工具），或者逐部分列出确切失败在哪里；同时说明哪些 part 的验证状态横幅被更新或移除、哪些 fragment/exercise 因结构不完整被跳过、哪些 `expected_failure` 按预期失败。

9. **保留工作区。** 无论验证结果如何，`.lathe-verify/` 一律保留（供后续增量验证复用），**不询问、不提醒用户是否清理**——其作用已在 `metadata.json` 的 `verify_workspace` 字段中说明。用户手动删除该目录是安全的：下次验证会自动重建并全量执行。

## 版本冲突修复流程

适用于静态预检发现的冲突，以及动态执行中归因为版本冲突的报错。目标是在验证阶段就修好教程，而不是留给读者自行踩坑。

1. **向用户展示冲突详情：** 所在部分和代码块位置、锁定/声明的版本、冲突的特性，以及证据（编译错误输出或官方文档链接）。
2. **提出修复方案（两个方向，给出你的建议）：**
   - **方案 A：改代码/文本对齐锁定版本** —— 改写示例代码和相关讲解，使其在锁定版本下成立（通常首选：不改变读者环境约束）；
   - **方案 B：调整版本声明对齐特性** —— 修改配置代码块中的版本/edition，并同步更新 `metadata.json` 的 `tools`（适用于文本核心内容依赖新版本特性的情况）。
3. **用户确认后才修改。** 改动最小化：只修改冲突相关的代码块、版本声明和直接相关的讲解文字，不重写其他内容、不改变 voice 和结构。用户拒绝修复则保留原文，按常规 `failed` 记录。
4. **修复后重新执行该部分**（静态预检阶段的修复则在动态执行时一并验证），确认修复真正生效。
5. **记录修复：** 写入 `verify-result.json` 对应部分的 `fixes` 数组（一条修复一句话：冲突原因 + 处理方式），并在最终报告中逐条告知用户。

## 边界

- **对教程部分默认只读。** 常规写入仅限 `verify-result.json`、`metadata.json` 的 `status` 字段与 `verify_workspace` 字段（首次创建工作区时写入）。**唯一例外**：版本冲突修复可修改 `part-NN.md` 中冲突相关内容及 `metadata.json` 的 `tools`，但必须先获用户确认、改动最小化。metadata 自愈时可写入完整结构（见 metadata.md）。
- **不读取被增量复用跳过的部分文件**——不执行就不需要其正文。
- **跳过 ≠ 失败。** 缺少工具链或未获确认的敏感操作是 `skipped`。将 `failed` 保留给教程确实有问题的情况。
- **所有执行限制在验证工作区（`.lathe-verify/`）内。** 敏感操作（sudo、全局安装、工作区外删除）必须先征得用户同意。
- **工作区只进不出。** 验证不在工作区之外产生任何文件；也不主动删除工作区（清理权在用户）。
