# 管理教程标签

选择使已存储教程可被发现的标签。

## 协议

1. **阅读教程。** 按 `<SKILL_DIR>/SKILL.md`"教程位置解析规则"定位该教程目录，读取 `metadata.json`。优先用已有信息判定主题：`title`、`topic`、`tools`、`goal`、`continuity.covered_concepts` 与 `part_titles` 通常已足够选出好标签——**仅在这些信息不足以判断时，才去浏览部分正文**（打标签不值得加载数十万字符的教程正文）。

   **若 `metadata.json` 缺失或损坏**，先执行 `<SKILL_DIR>/references/metadata.md`"metadata.json 自愈"，用户确认重建后再打标签（重建时已推断的 `tags` 可作为候选，由用户确认或调整）。

2. **选择 2-5 个小写、可复用的标签。** 在适用时涵盖：
   - **语言/运行时** —— `zig`、`rust`、`go`；
   - **领域** —— `audio`、`compilers`、`databases`；
   - **核心技术** —— `parsing`、`dsp`、`concurrency`。

   优先选择能与其他教程自然分组的短标签，而非过于具体的一次性标签。

3. **持久化标签。** 读取现有的 `metadata.json`，更新 `tags` 数组，然后写回：
   - **设置整个标签列表**（选择或替换标签）：完全替换 `tags` 数组。
   - **添加标签：** 追加到现有数组，然后去重。
   - **移除标签：** 从现有数组中删除。

   `metadata.json` 中的 `tags` 字段是小写字符串的 JSON 数组：
   ```json
   {
     "tags": ["zig", "audio", "dsp"]
   }
   ```

4. **向用户报告最终的标签集合。**

## 边界

- **常规情况下仅修改 `metadata.json` 中的 `tags` 字段。** 绝不编辑部分文件。
- **唯一例外：metadata 自愈。** `metadata.json` 缺失或损坏时，重建必然要写入全部字段（不重建索引就无处存放 `tags`）——这需要用户先确认重建结果，见 `<SKILL_DIR>/references/metadata.md`。自愈之外不得附带修改其他字段。
- 不涉及生成、验证或续写——仅处理标签。
- **不需要 writing-core.md**——本操作不写教程正文。
