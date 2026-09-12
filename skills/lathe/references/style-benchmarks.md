# 风格标杆

十位标杆作者代表了 Lathe 教程的质量基准线：五位**核心标杆**定义整体水准，五位**扩展参考**在特定维度上补充。生成教程时，根据主题和场景**侧重参考**不同作者的长项。

## 标杆作者

`id` 列是该作者在 `metadata.json` 的 `style_anchor` 字段中的取值——**这是 `style_anchor` 的唯一合法取值来源**，不要自创 id。

| id | 作者 | 定位 | 代表作 | 核心风格 |
|----|------|------|--------|----------|
| `nystrom` | **Robert Nystrom** | 核心 | *Crafting Interpreters*、*Game Programming Patterns* | 散文式构建：先讲"为什么"再讲"怎么做"，每章独立成篇，手绘插图，恰到好处的幽默 |
| `sam-who` | **Sam Who** | 核心 | samwho.dev（Raft、Bloom Filter、LSM Tree） | 极简散文 + 交互可视化：每句都有信息量，篇幅精炼，具体数字驱动 |
| `julia-evans` | **Julia Evans** | 核心 | jvns.ca、*Bite Size* zine 系列 | 亲切去神秘化：像经验丰富的同事在白板前聊天，善用类比和漫画，技术精确 |
| `ciechanowski` | **Bartosz Ciechanowski** | 核心 | ciechanow.ski（Cameras、Mechanical Watch、GPS） | 极致深度拆解：逐层揭示系统，每件艺术品级的交互配合深思熟虑的散文 |
| `amit-patel` | **Amit Patel** | 核心 | Red Blob Games（A*、Graphs、Map Generation） | 交互式算法教程：平实精确，可运行演示驱动，"边做边学"结构 |
| `kleppmann` | **Martin Kleppmann** | 扩展 | *Designing Data-Intensive Applications* | 系统设计 + 工程权衡分析，将抽象概念落地为具体实现路径 |
| `klabnik-nichols` | **Steve Klabnik & Carol Nichols** | 扩展 | *The Rust Programming Language* | 渐进式引入、兼顾新手与老手、社区共建风格 |
| `matuschak` | **Andy Matuschak** | 扩展 | andymatuschak.org | 主动回忆、间隔重复、知识沉淀理念 |
| `bernhardt` | **Gary Bernhardt** | 扩展 | *Destroy All Software* | 极简主义、从本质出发、"少即是多" |
| `bret-victor` | **Bret Victor** | 扩展 | worrydream.com | "让知识看得见"、交互教学哲学、即时反馈 |

## 场景侧重

生成教程时，根据主题特征**侧重参考**对应作者的长项。这不是排他的——好教程融合多种风格，但每个场景有一个主锚点：

| 场景 | 主锚点 id | 参考什么 | 示例主题 |
|------|-----------|----------|----------|
| **构建编译器/解释器/语言工具** | `nystrom` | 散文节奏、章节独立性、先展示错误再修复的节拍 | PL 编译器、DSL 解释器、解析器组合子 |
| **算法/数据结构/数学可视化** | `amit-patel` | 可交互演示、渐进式揭示、平实精确的语言 | 寻路算法、噪声函数、图算法、几何计算 |
| **系统底层/硬件/协议拆解** | `ciechanowski` | 逐层拆解的深度、从外到内的揭示顺序 | 操作系统内核、网络协议栈、GPU 管线、机械结构 |
| **分布式系统/基础设施** | `sam-who` | 精炼散文、交互可视化、具体数字驱动 | Raft/Paxos 共识、分布式哈希表、LSM 存储引擎 |
| **日常工具/去神秘化/入门** | `julia-evans` | 亲切语气、类比驱动、去神秘化叙事 | Linux 命令行、HTTP 调试、DNS 原理、容器基础 |
| **系统架构/工程权衡** | `kleppmann` | 权衡分析结构、将抽象概念落地为具体实现路径 | 数据一致性、消息队列、缓存策略 |
| **Rust 语言相关** | `klabnik-nichols` | 渐进式引入、兼顾新手与老手、社区共建风格 | Rust 所有权、生命周期、异步编程 |
| **涉及记忆/回顾机制设计** | `matuschak` | 主动回忆、间隔重复、知识沉淀理念 | 教程中 `[!PREDICT]`/`[!RECALL]` 标注的设计 |
| **底层原理/追本溯源** | `bernhardt` | 极简主义、从本质出发、"少即是多" | Unix 哲学、编码原理、类型系统基础 |
| **需要"让概念可见"的交互** | `bret-victor` | 交互式教学哲学、视觉化表达、即时反馈 | 信号处理、物理模拟、数学概念可视化 |

**使用方式：** 生成教程时，先按主题匹配场景行，侧重参考主锚点作者的长项来指导写作节奏和结构选择。如果主题跨多个场景，选最强的一个作为主锚点，其余为辅。**把选定的主锚点 id 写入 `metadata.json` 的 `style_anchor`**——续写与复习据此沿用同一节奏，无需再次读取本文件（见 `<SKILL_DIR>/references/writing-core.md`"风格标杆与主锚点"）。

**何时读取本文件：** 仅在**生成新教程**（选定主锚点）或**为缺少 `style_anchor` 的旧教程补齐该字段**时。续写、复习、收尾一律从 metadata 读取 id，不加载本文件。
