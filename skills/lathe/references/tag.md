# 管理教程标签

选择使已存储教程可被发现的标签。

## 协议

1. **阅读教程。** 按 `<SKILL_DIR>/SKILL.md`“教程位置与双布局”定位课程根目录，并由 metadata 位置整体判定布局：新课程读取 `_lathe/metadata.json`，legacy 读取根目录 `metadata.json`。两处同时存在或辅助文件混放时列出冲突并停止，不逐文件回退，也不为 legacy 创建 `_lathe/`。优先用 `title`、`topic`、`tools`、`goal`、`continuity.covered_concepts` 与 `part_titles` 判定主题；只有信息不足时才浏览相关正文。

   **若当前布局 metadata 缺失或损坏**，先执行 `<SKILL_DIR>/references/metadata.md`“按布局自愈”，用户确认重建位置与结果后再打标签。

2. **选择 2-5 个小写、可复用的标签。** 在适用时涵盖：
   - **语言/运行时** —— `zig`、`rust`、`go`；
   - **领域** —— `audio`、`compilers`、`databases`；
   - **核心技术** —— `parsing`、`dsp`、`concurrency`。

   优先选择能与其他教程自然分组的短标签，而非过于具体的一次性标签。

3. **持久化标签。** 只读取并原地写回当前布局的 metadata，更新 `tags` 数组：
   - **设置整个标签列表**（选择或替换标签）：完全替换 `tags` 数组。
   - **添加标签：** 追加到现有数组，然后去重。
   - **移除标签：** 从现有数组中删除。

   metadata 中的 `tags` 字段是小写字符串的 JSON 数组：
   ```json
   {
     "tags": ["zig", "audio", "dsp"]
   }
   ```

4. **向用户报告最终的标签集合。**

## 边界

- **常规情况下仅修改当前布局 metadata 中的 `tags` 字段。** 绝不编辑部分文件、canonical ledger 或另一布局的辅助文件。
- **唯一例外：metadata 自愈。** 当前布局 metadata 缺失或损坏时，重建需要用户先确认位置与推断结果；见 `<SKILL_DIR>/references/metadata.md`。自愈之外不得附带修改其他字段。
- 不涉及生成、验证或续写——仅处理标签。
- **不需要 writing-core.md**——本操作不写教程正文。
