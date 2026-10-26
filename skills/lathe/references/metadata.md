---
name: metadata
description: Lathe 0.7.0 metadata 完整结构、Part 级叙事大纲、continuity 可重建缓存、双布局与自愈协议
---

# metadata 规范（0.7.0 权威契约）

新课程只写 `_lathe/metadata.json`。它是课程索引与连续性缓存，不是知识点事实源；点级状态只读写 `_lathe/knowledge-points.md`。调用脚本时仍传课程根目录。

---

## 1. 布局契约

由 metadata 的位置**整体决定**辅助文件布局：

| 布局 | metadata | 知识点 | research | verify result | verify workspace |
|---|---|---|---|---|---|
| 新课程 | `_lathe/metadata.json` | `_lathe/knowledge-points.md` | `_lathe/research.md` | `_lathe/verify-result.json` | `_lathe/verify-workspace/` |
| 0.6.0 legacy | `metadata.json` | `syllabus.json` | `research.md` | `verify-result.json` | `.lathe-verify/` |

正文 `part-*.md` 留在课程根目录。不要按文件存在与否逐个回退：判定新布局后只查 `_lathe/`，判定 legacy 后只查根目录。两处 metadata 同时存在，或辅助文件跨布局混放，均报告冲突并停止写入。旧课程始终原地兼容，不迁移、不创建 `_lathe/`。

---

## 2. 新课程完整结构

```json
{
  "_warning": "⚠️ 本文件是 Lathe 课程索引；知识点事实源是同目录 knowledge-points.md。",
  "_needs_backfill": [],
  "lathe_version": "0.7.0",
  "slug": "<kebab-case>",
  "title": "<课程标题>",
  "topic": "<用户原始主题>",
  "goal": "<可评估的一句话目标>",
  "created": "<ISO 8601>",
  "status": "unverified",
  "tags": ["<标签>"],
  "parts": ["part-01.md"],
  "language": "zh-CN",
  "experience_level": "beginner",
  "topic_novelty": "new",
  "course_plan": [
    {"part": 1, "title": "<Part 标题>", "goal": "<Part 目标>", "prerequisites": ["<前置>"]}
  ],
  "changed_interfaces": [
    {
      "file": "<路径>",
      "symbol": "<符号>",
      "from": "<旧契约>",
      "to": "<新契约>",
      "call_sites": ["<调用点>"],
      "supersedes": ["part-01.md#3"],
      "part": "part-NN.md"
    }
  ],
  "part_versions": {"part-01.md": "0.7.0"},
  "style_anchor": "<作者 id>",
  "repo": "<远程 URL 或空>",
  "repo_branch": "<分支或空>",
  "local_project_path": "<路径或空>",
  "tools": [{"name": "<工具>", "version": "<版本>"}],
  "sources": ["<URL>"],
  "voice": "plainspoken",
  "model": "<模型名>",
  "continuity": {
    "controlling_example": "<控制性示例>",
    "fixed_numbers": {"<名称>": "<值>"},
    "metaphor": "<隐喻或空字符串>",
    "metaphor_retired": false,
    "covered_concepts": ["<最近讲过的概念>"],
    "open_threads": ["<未决问题或伏笔>"],
    "next_hook": "<一到两句衔接>",
    "part_titles": {"part-01.md": "<一级标题>"},
    "updated_at": "<ISO 8601>",
    "updated_through": "part-NN.md"
  },
  "verify_workspace": {
    "path": "_lathe/verify-workspace/",
    "note": "教程验证工作区；可删除，下次验证重建。"
  }
}
```

不要为新课程添加任何点级状态、ID 或练习承接镜像字段。

---

## 3. 字段语义

| 字段 | 写入规则 |
|---|---|
| `_warning` | 每次写回保留；技能读取时忽略文案 |
| `_needs_backfill` | 只列无法可靠推断且需人工补充的字段；补齐即移除 |
| `lathe_version` | 每次写回更新为当前技能版本 |
| `goal` | 生成时确认；收尾按它判断目标是否达成 |
| `status` | 使用 SKILL.md 状态机；新建写 `unverified`。`completed` 允许仍有未学完的 `planned` / `queued`，但总结必须写「未学完」提示；续写会重新开放为 `unverified` |
| `parts` | 按顺序列课程正文与复习材料文件名 |
| `experience_level` | `beginner` / `familiar` / `experienced`；续写沿用 |
| `topic_novelty` | `new` / `adjacent` / `familiar`；驱动写作与研究预算 |
| `course_plan` | 2–12 个 **Part 级叙事大纲**项，只写 part、标题、目标、前置；**不绑定任何知识点**，不承载点级状态或排队项。它只是写作方向参考，可在每次选点后改写；2 项只用于小而完整的课程 |
| `changed_interfaces` | 活跃跨 Part 接口变更，最多 8 条；规则见下节 |
| `part_versions` | 每写一个部分记录当时 Lathe 版本；历史检查按部分降级 |
| `style_anchor` | 生成时选定，续写沿用 |
| `sources` | 去重保存实际使用过的 URL |
| `continuity` | 可从正文和知识表重建的续写缓存，不是事实源 |
| `verify_workspace` | 新课程固定 `_lathe/verify-workspace/`；不要写根目录 `.lathe-verify/` |

**Part 与点分工：** `course_plan` 只回答“课程大致按哪些 Part 推进”，是叙事大纲；`knowledge-points.md` 回答“池里有哪些点、每个点处于什么状态、讲在哪里”。**不要把点分配给 Part，也不要在路线调整时同步所谓“计划 Part”**；两者没有外键关系。

缺字段时按本文降级推断并在本次写回补齐；无法可靠推断才进入 `_needs_backfill`。不要因普通可选字段缺失中止操作。

---

## 4. continuity 可重建缓存

`continuity` 只用于避免续写重读全部历史。知识点状态、排队和练习承诺均从知识表读取，不在 continuity 建镜像。

### 读取与新鲜度

满足以下条件才信任缓存：

1. `updated_through` 等于最后一个常规 part；
2. 用户未声明修改过旧正文；
3. 没有任何 part 的 mtime **晚于实际 metadata 文件 mtime 超过 2 分钟**。

比较的是当前布局中 metadata 文件的真实 mtime，不是 `continuity.updated_at`。2 分钟以内视为同批写入容差；超过才按手工编辑处理。复制、clone 或同步后 metadata 与 part 时间接近时不要误判。

缓存不可信、缺失或落后时，读取全部常规 part 与知识表并重建。要写 part-03、06、09……时即使可信也执行一次全读审计。`changed_interfaces` 或 `open_threads` 指向旧 part 时，额外读取相关小节。

### 字段与预算

| 字段 | 契约 | 上限与溢出 |
|---|---|---|
| `controlling_example` | 精确复用的课程产物 | 1 条，≤200 字 |
| `fixed_numbers` | 后续仍需复用的领域数字 | 18 项，每项 ≤40 字；删除不再复用的旧缓存 |
| `metaphor` / `metaphor_retired` | 控制性隐喻及是否已告别 | 各 1；隐喻 ≤200 字 |
| `covered_concepts` | **从知识表 `taught` 可重建的最近 24 条缓存**；仅用于续写避免重复与 `[!RECALL]` 取材 | 最多 24 条，每条 ≤40 字；溢出直接丢弃最旧缓存，不归档、不作为覆盖证据 |
| `open_threads` | 尚未解决的问题/伏笔 | 8 条，每条 ≤80 字；解决或溢出后按需归档到 research |
| `next_hook` | 最后一个 Part 的衔接语境，不是知识点队列 | 1 条，≤200 字 |
| `part_titles` | 最近部分的文件名到标题映射 | 最近 8 个，每条 ≤60 字；更早标题按正文现取 |
| `updated_through` | 缓存覆盖到的最后常规 part | 每次新写 part 后更新 |
| `updated_at` | continuity 自身的写回时间，仅作说明 | 不用于 mtime 手工编辑判定 |

总量软上限 2200 字、硬上限 3000 字。运行：

```text
python3 <SKILL_DIR>/scripts/ledger_check.py <课程根目录> --continuity
```

超软上限或字段条数超限时修剪可重建缓存；超硬上限必须先修剪再交付。不得压缩正文解决索引预算。每次写入新 part 后，增量更新数字、线程、最近已讲概念、钩子、标题与时间；收尾没有新知识点时不要伪造 covered concept。

---

## 5. changed_interfaces

把跨部分仍活跃的公开 API、签名、导出类型、数据库 schema 或配置契约变更按符号记录：

- 必填 `file`、`symbol`、`from`、`to`、`call_sites`、`part`；确认无调用点时写 `[]` 并在正文说明。
- 变更使旧检查点预期输出失效时，写 `supersedes: ["part-NN.md#<检查点组号>"]`；只覆盖检查点预期，不覆盖 runnable 历史代码。
- 同一符号只留最新活跃项；旧项归档到当前布局的 research，并注明 `superseded by <part>`。
- 活跃最多 8 条；超过时先归档已解决/被替代项，仍溢出则归档最早项并标 `active (overflow)`。
- 无变化写 `[]`；legacy 缺失视为空，不强制回填。

---

## 6. research 归档

新课程只写 `_lathe/research.md`；legacy 只写根目录 `research.md`。没有归档内容时不要创建。允许以下小节按需出现：

```markdown
## Changed Interfaces Archive

### <symbol>（<part>）
- 文件：`<file>`
- 变化：`<from>` → `<to>`
- 调用点：`<call sites>`
- 状态：archived / superseded by <part> / active (overflow)

## Open Threads Archive

### <简短标题>
- 提出于：`part-NN`
- 状态：resolved / deferred / superseded
- 解决于：`part-NN` 或 `—`
- 问题：<原问题>
- 备注/来源：<可选>

## Errata

- <日期> `part-NN` §<章节>：<原文> → <修正>（原因：<原因>；处理：<处理>；影响面：<路径>）
```

一条一个归档块，不写“同上”或按列表位置合并指代。`resolved` 必须有具体解决 Part；其他状态写 `解决于：—` 并说明去向。Errata 的影响面必填。

**不要创建 `## Self-study Backlog` 或 `## Covered Concepts Archive`。** 自学与已讲状态只在知识表；最近已讲概念仅作为 continuity 可重建缓存。读取历史 research 时，旧 `Self-study Backlog` / `Covered Concepts Archive` 只作 0.6.0 格式兼容并忽略，不迁移、不据此改知识表、也不继续追加。

关键事实覆盖表可临时内部记录，确需跨 Part 复用时可在 research 增加不承载知识点状态的来源笔记；不得把它变成第二份知识清单。

---

## 7. course_plan

执行以下规则：

- 生成前初始化 2–12 个 Part 级**叙事大纲**项；part-01 不必严格“完成第 1 项”，它只是方向参考。只有内容确实不足以拆成 3 个独立学习单元时才用 2 项，不为凑数硬拆。
- 续写按知识池现选点，选完再确定本 Part 标题/目标；如果与大纲下一项不同，更新大纲并说明偏离原因，不静默跳项。
- 容量不足需要拆 Part 时，先让用户确认，再改写大纲项；不需要同步知识表的 Part 字段，因为不存在该字段。
- 收尾保留已走路线；完成度由 `goal`、知识表剩余点和用户选择决定，不由路线项数量单独决定。有剩余点时允许 `completed`，但总结必须写未学完提示。
- legacy 缺失时可从 part 标题、目标与 `next_hook` 推断；新课程不得从 `next_hook` 生成隐藏知识点。

---

## 8. 按布局自愈

发现正文存在但 metadata 缺失或损坏时，先判定布局线索：

1. **新布局线索**：仅 `_lathe/` 辅助文件存在时，在 `_lathe/metadata.json` 重建；知识点只从 `_lathe/knowledge-points.md` 读取。
2. **legacy 线索**：仅根目录旧辅助文件存在时，在根目录 `metadata.json` 重建；继续使用 `syllabus.json`，不迁移。
3. 两套线索同时出现、错误名称出现或两处 metadata 同时存在：判混合布局，列出冲突并停止；不得猜测、移动或逐文件回退。
4. 完全没有辅助文件但有 part 时，写入前把拟采用的新布局与推断结果展示给用户；只读操作只报告缺失，不写文件。

按正文推断 `slug`、标题、语言、标签、工具、来源、created、goal、experience、novelty、style、Part 级路线与 continuity；`changed_interfaces` 无法可靠推断时写空并加入 `_needs_backfill`。新布局知识表存在时，以其 `taught` 重建 covered cache；不存在或损坏时不要从 metadata 猜点级状态，先按 knowledge-ledger.md 的恢复流程处理。

用户确认后只写当前布局的 metadata，并更新配置登记。用户拒绝时终止写入型操作。只读操作不得借自愈改文件。

### 0.6.0 legacy 废弃字段

旧 metadata 可能含 `metadata.knowledge_backlog`、`metadata.syllabus_ids`、`continuity.exercise_carry`、`pending_part`。读取时仅作兼容线索；旧课原地写回可保留未知字段，但不要更新、依赖或复制到新 schema。知识点、承诺与排队状态一律以当前布局的账本为准。
