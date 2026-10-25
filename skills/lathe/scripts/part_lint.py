#!/usr/bin/env python3
"""单个 part 的结构与代码块静态检查（交付前自检的机械部分）。

用法：
    python3 <SKILL_DIR>/scripts/part_lint.py <教程目录>/part-03.md [--kind regular|finish]

检查（对应 writing-core.md「教程结构」「代码」与 knowledge-ledger.md「延后提醒」）：
  H1、验证状态横幅、必需的 ## 小节与顺序、续写变体（RECALL、目标达成回顾在接下来之前、§0 承接位置）、
  结束状态 / 下一部分起始状态 / 本部分不覆盖 / 练习承接 四行、
  代码块类型（未标记、runnable 含整行 ...、fragment 无最终 runnable/检查点、exercise 无答案）、
  必做练习引入新概念 ≤2（按档 3 提醒计）、选做练习附文档链接、ASIDE ≤2、PREDICT ≥1、
  来源条数、正文长度与单块行数的软阈值。
  `--kind finish`（或没有 `## 检查点` 时自动判定）改查总结部分的七个小节（全课程回顾 / 知识图谱 /
  目标对照 / 未讲清单 / 回顾自检 / 练习方向 / 寄语），并要求**不出现**检查点、你将构建什么、
  前置条件、来源、验证状态横幅（写了横幅就是一句永不撤销的假承诺）。
  `--kind review`（或文件名含 `-review` 自动判定）改查复习材料的六个必备小节、顺序、
  是否覆盖全部常规部分、H1 格式、教学标注，并逐块校验「摘录保真」
  （每个围栏块必须是同目录某个常规部分原文的连续子串——这是「复习可以只定点读取」的前提）；
  不查验证横幅与教程结构。
最后一行打印构建章节数，供覆盖回执的「实写 N 章」使用。

**只检查本次新写/改动的部分。** 教程 `metadata.json` 的 `lathe_version` 低于 0.6.0 时，
0.6.0 才引入的两条约束（档 3 提醒写积压 ID、引入新概念的必做练习 ≤2）降级为 `ℹ️` 提示——
按旧版规则写的部分不该被判成错误，历史部分也不参与交付自检。

退出码：0 = 无错误（可能有警告）；1 = 有错误。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lathe_common import (  # noqa: E402
    LayoutConflictError,
    LayoutNotFoundError,
    code_blocks,
    headings,
    load_metadata,
    part_number,
    resolve_layout,
    section,
    strip_code,
)

REGULAR_SECTIONS = ("你将构建什么", "前置条件", "检查点", "接下来", "练习", "来源")
REVIEW_SECTIONS = ("逐部分回顾", "自测", "重跑检查点", "学习目标回顾", "还没讲到的", "还可以继续深入的方向")
FINISH_SECTIONS = ("全课程回顾", "知识图谱", "目标对照", "未讲清单", "回顾自检", "练习方向", "寄语")
FORBIDDEN_IN_FINISH = ("检查点", "你将构建什么", "前置条件", "来源")
CONTRACT_LINES = ("本部分结束时的文件状态", "下一部分起始状态", "本部分不覆盖", "练习承接")
ELLIPSIS = re.compile(r"^\s*(?://|#|--)?\s*(?:\.\.\.|…)\s*$", re.MULTILINE)


def write_version(path: Path) -> str:
    """通过双布局适配层读取这个部分当初使用的技能版本。

    优先取 `metadata.part_versions[<文件名>]`（逐部分记录），缺失时回落到教程级
    `lathe_version`。旧教程被新版本续写一次后 `lathe_version` 会升级，
    只有逐部分记录才能区分「本次新写的部分」和「历史部分」。"""
    try:
        data = load_metadata(path.parent)
    except Exception:
        return ""
    return str((data.get("part_versions") or {}).get(path.name) or data.get("lathe_version") or "")


def tutorial_legacy(path: Path) -> bool:
    nums = tuple(int(x) for x in re.findall(r"\d+", write_version(path))[:3])
    return bool(nums) and nums < (0, 6, 0)


def lint(path: Path, kind: str, force_legacy: bool = False) -> int:
    try:
        resolve_layout(path.parent)
    except LayoutConflictError as exc:
        print(f"❌ 布局 conflict：{exc}")
        return 1
    except LayoutNotFoundError:
        pass  # 保持旧行为：没有 metadata 时按未知版本继续做结构检查。
    legacy = force_legacy or tutorial_legacy(path)
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []
    heads = headings(text)
    if force_legacy:
        notes.append("已按 --legacy 运行：0.6.0 新增的约束降级为提示（检查历史部分时使用）")
    elif legacy:
        notes.append(f"该部分由 v{write_version(path) or '未知（≤0.5.x）'} 写成，0.6.0 新增约束按历史部分降级为 ℹ️")
    if kind == "auto":
        kind = "review" if "-review" in path.name else ("regular" if "检查点" in heads else "finish")
    if kind == "finish":
        notes.append("按总结部分（finish）结构检查：七节齐全、不含检查点/契约行/横幅")
    number = part_number(path.name)

    if not text.lstrip().startswith("# "):
        errors.append("第一行必须是一级标题 `# `")
    if kind not in ("review", "finish") and "lathe:verify-status:start" not in text:
        warnings.append("缺少验证状态横幅（新写的 part 必须在 H1 后插入未验证横幅）")

    if kind == "regular":
        missing = [s for s in REGULAR_SECTIONS if not any(h.startswith(s) for h in heads)]
        if missing:
            errors.append(f"缺少小节：{missing}")
        order = [next((i for i, h in enumerate(heads) if h.startswith(s)), None) for s in REGULAR_SECTIONS]
        present = [o for o in order if o is not None]
        if present != sorted(present):
            errors.append("小节顺序不对：应为 你将构建什么 → 前置条件 → …构建章… → 检查点 → 接下来 → 练习 → 来源")
        for line in CONTRACT_LINES:
            if f"**{line}" not in text:
                errors.append(f"检查点之后缺少「**{line}：**」一行")
        if number >= 2:
            if "[!RECALL]" not in text:
                errors.append("续写部分（part-02 起）顶部需要 > [!RECALL]")
            gi = next((i for i, h in enumerate(heads) if h.startswith("目标达成回顾")), None)
            ni = next((i for i, h in enumerate(heads) if h.startswith("接下来")), None)
            if gi is None:
                errors.append("续写部分缺少 ## 目标达成回顾")
            elif ni is not None and gi > ni:
                errors.append("## 目标达成回顾 必须在 ## 接下来 之前")
        carry = [i for i, h in enumerate(heads) if re.match(r"0[\.．、]", h)]
        pre = next((i for i, h in enumerate(heads) if h.startswith("前置条件")), None)
        if carry and pre is not None and carry[0] != pre + 1:
            errors.append("§0 承接/地基章必须紧跟 ## 前置条件，放在第一个构建章之前")
        if text.count("[!PREDICT]") == 0:
            warnings.append("检查点前没有 > [!PREDICT]")

    if kind == "finish":
        missing = [x for x in FINISH_SECTIONS if not any(x in h for h in heads)]
        if missing:
            errors.append(f"总结部分缺少小节：{missing}")
        extra = [h for h in heads if any(h.startswith(x) for x in FORBIDDEN_IN_FINISH)]
        if extra:
            errors.append(f"总结部分不该有这些小节：{extra}")
        faked = [x for x in CONTRACT_LINES if f"**{x}" in text]
        if faked:
            warnings.append("总结部分写了契约行（没有下一部分可交接）：" + "、".join(faked))
        if text.count("[!PREDICT]") or text.count("[!RECALL]"):
            warnings.append("总结部分不用教学标注（回顾自检直接用普通问题）")
        if "lathe:verify-status:start" in text:
            errors.append("总结部分不该带验证状态横幅（它永不参与验证，横幅是永不撤销的假承诺）")
        print("总结部分：七节" + ("齐全 ✅" if not missing else "不全 ❌"))
    if kind == "review":
        missing = [x for x in REVIEW_SECTIONS if not any(x in h for h in heads)]
        if missing:
            errors.append(f"复习材料缺少小节：{missing}")
        seq = [h for h in heads if any(x in h for x in REVIEW_SECTIONS)]
        rank = [min(REVIEW_SECTIONS.index(x) for x in REVIEW_SECTIONS if x in h) for h in seq]
        if rank != sorted(rank):
            errors.append("复习材料小节顺序不对：" + " → ".join(seq))
        first = text.lstrip().splitlines()[0] if text.strip() else ""
        if not first.startswith("# 复习："):
            warnings.append("复习材料的 H1 应为「# 复习：<教程标题>（截至 part-NN）」")
        if re.search(r"part-\d+-review", first):
            errors.append("H1 的「截至 part-NN」只能取最后的常规部分，不能取复习部分")
        regs = sorted(f.name for f in path.parent.glob("part-*.md") if "-review" not in f.name)
        want = {m.group(1).lstrip("0") or "0" for n in regs for m in [re.search(r"part-(\d+)\.md", n)] if m}
        covered = {c.lstrip("0") or "0" for c in re.findall(r"^###\s*part-(\d+)", text, flags=re.MULTILINE)}
        if want and not want <= covered:
            errors.append(f"「逐部分回顾」没有覆盖全部常规部分：缺第 {sorted(want - covered, key=int)} 部分")
        if text.count("[!PREDICT]") or text.count("[!ASIDE]"):
            warnings.append("复习材料不用教学标注（PREDICT / ASIDE）")
        if text.count("[!RECALL]") > 1:
            warnings.append("复习材料的 [!RECALL] 最多 1 个")
        # 摘录保真：每个围栏块必须是某个常规部分原文的连续子串
        sources = {f.name: f.read_text(encoding="utf-8")
                   for f in sorted(path.parent.glob("part-*.md"))
                   if f.name != path.name and "-review" not in f.name}
        lost = []
        for b in code_blocks(text):
            body = b["body"].strip()
            if body and not any(body in src for src in sources.values()):
                lost.append(f"第 {b['line']} 行 {b['type']} 块（{len(body)} 字符）")
        if lost:
            errors.append("摘录不是原文逐字子串（改写了/拼接了/漏了标注）：" + "；".join(lost[:4]))
        elif sources:
            notes.append(f"摘录保真：{len([b for b in code_blocks(text) if b['body'].strip()])} 个块全部为原文逐字子串 ✅")

    blocks = code_blocks(text)
    types = [b["type"] for b in blocks]
    unmarked = [b for b in blocks if not b["marked"]]
    if unmarked:
        where = "、".join(f"{b['line']}（{b['info'] or '无语言'}）" for b in unmarked)
        warnings.append(f"{len(unmarked)} 个代码块未标记类型、会按 runnable 执行：第 {where} 行——新写的块请标明类型（检查点命令用 `bash runnable`，示例数据用 `text`）")
    for b in blocks:
        where = f"第 {b['line']} 行 ```{b['info'] or '（未标记）'}"
        if b["info"] and not b["marked"] and any(t in b["info"] for t in ("runnable", "fragment", "exercise", "expected_failure")):
            errors.append(f"{where}：类型词没和后面的文字用空格隔开，会被当成未标记的 runnable")
        if b["type"] == "runnable":
            if ELLIPSIS.search(b["body"]):
                errors.append(f"{where}：runnable 块含整行 `...` 省略（代码不完整）")
            n = len(b["body"].splitlines())
            if n > 120:
                notes.append(f"{where}：runnable 块 {n} 行（超过约 100-120 行的观察值）——可按文件/逻辑段分段呈现，不裁内容；这不是上限")
    if "fragment" in types and "runnable" not in types and "## 检查点" not in text:
        errors.append("有 fragment 但没有覆盖最终状态的 runnable 块或检查点")
    if "exercise" in types and not re.search(r"参考答案|检查方式", text):
        errors.append("有 exercise 块但全文没有「参考答案」或「检查方式」")

    exercises = section(text, "练习")
    if exercises:
        sink = notes if legacy else errors
        tier3 = re.findall(r"\*本题涉及的知识点（[^\n]*", exercises)
        for note in tier3:
            if "积压 ID" not in note:
                sink.append("档 3 练习提醒没有写积压 ID")
        if len(tier3) > 2:
            sink.append(f"引入新概念的必做练习有 {len(tier3)} 道（上限 2）")
        optional = exercises.split("选做", 1)[1] if "选做" in exercises else ""
        for item in re.findall(r"^\d+\.\s.*$", optional, flags=re.MULTILINE):
            if "http" not in item and "](" not in item:
                warnings.append(f"选做练习缺少官方文档入口：{item[:40]}…")

    if text.count("[!ASIDE]") > 2:
        warnings.append(f"ASIDE {text.count('[!ASIDE]')} 个，超过每部分 2 个")
    sources = section(text, "来源")
    if kind == "regular" and sources and len(re.findall(r"https?://", sources)) < 3:
        warnings.append("## 来源 少于 3 个实际来源")
    prose = strip_code(text.split("\n## 来源", 1)[0])
    cjk = len(re.findall(r"[\u4e00-\u9fff]", prose))
    if cjk > 10000:
        notes.append(f"正文约 {cjk} 个中文字符（超过约 10,000 的观察值）——只看里程碑/改动面是否该拆部分，篇幅长不是缺陷，不得压缩解释")

    if kind == "regular":
        pre = next((i for i, h in enumerate(heads) if h.startswith("前置条件")), -1)
        chk = next((i for i, h in enumerate(heads) if h.startswith("检查点")), len(heads))
        chapters = heads[pre + 1:chk]
        if len(chapters) > 9:
            errors.append(f"地基 + 承接 + 构建共 {len(chapters)} 章（上限 9）")
        # 这里只报告章节结构；4–7 构建知识点由 ledger_check --receipt 按知识表类型精确门禁。
        carry = [h for h in chapters if re.match(r"0[\.．、]", h)]
        print(f"章节：§0 承接 {len(carry)} · 其他教学章 {len(chapters) - len(carry)}（实写 {len(chapters)} 章）")
    runnable = sum(1 for t in types if t in ("runnable", "expected_failure"))
    print(f"代码块：{len(blocks)} 个，其中可执行 {runnable} 个")

    for m in notes:
        print(f"ℹ️ {m}")
    for w in warnings:
        print(f"⚠️ {w}")
    if errors:
        print(f"❌ {path.name}：{len(errors)} 个错误")
        for e in errors:
            print(f"   - {e}")
        return 1
    print(f"✅ {path.name}：结构检查通过")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Lathe 单个 part 静态检查")
    ap.add_argument("part")
    ap.add_argument("--kind", choices=("auto", "regular", "finish", "review"), default="auto")
    ap.add_argument("--legacy", action="store_true",
                    help="按 0.6.0 之前的规则检查（档 3 积压 ID 与练习上限两条降级为提示）")
    args = ap.parse_args()
    return lint(Path(args.part), args.kind, args.legacy)


if __name__ == "__main__":
    sys.exit(main())
