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
最后一行打印构建章节数，供覆盖回执的「实写 N 章」使用。

退出码：0 = 无错误（可能有警告）；1 = 有错误。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lathe_common import code_blocks, headings, part_number, section, strip_code  # noqa: E402

REGULAR_SECTIONS = ("你将构建什么", "前置条件", "检查点", "接下来", "练习", "来源")
CONTRACT_LINES = ("本部分结束时的文件状态", "下一部分起始状态", "本部分不覆盖", "练习承接")
ELLIPSIS = re.compile(r"^\s*(?://|#|--)?\s*(?:\.\.\.|…)\s*$", re.MULTILINE)


def lint(path: Path, kind: str) -> int:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    warnings: list[str] = []
    heads = headings(text)
    if kind == "auto":
        kind = "regular" if "检查点" in heads else "finish"
    number = part_number(path.name)

    if not text.lstrip().startswith("# "):
        errors.append("第一行必须是一级标题 `# `")
    if "lathe:verify-status:start" not in text:
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
                warnings.append(f"{where}：runnable 块 {n} 行，超过约 100-120 行的拆分信号")
    if "fragment" in types and "runnable" not in types and "## 检查点" not in text:
        errors.append("有 fragment 但没有覆盖最终状态的 runnable 块或检查点")
    if "exercise" in types and not re.search(r"参考答案|检查方式", text):
        errors.append("有 exercise 块但全文没有「参考答案」或「检查方式」")

    exercises = section(text, "练习")
    if exercises:
        tier3 = re.findall(r"\*本题涉及的知识点（[^\n]*", exercises)
        for note in tier3:
            if "积压 ID" not in note:
                errors.append("档 3 练习提醒没有写积压 ID")
        if len(tier3) > 2:
            errors.append(f"引入新概念的必做练习有 {len(tier3)} 道（上限 2）")
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
        warnings.append(f"正文约 {cjk} 个中文字符，超过约 10,000 的拆分信号")

    if kind == "regular":
        pre = next((i for i, h in enumerate(heads) if h.startswith("前置条件")), -1)
        chk = next((i for i, h in enumerate(heads) if h.startswith("检查点")), len(heads))
        chapters = heads[pre + 1:chk]
        build = [h for h in chapters if not re.match(r"0[\.．、]", h)]
        print(f"章节：地基/承接 {len(chapters) - len(build)} · 构建 {len(build)}（实写 {len(chapters)} 章）")
    runnable = sum(1 for t in types if t in ("runnable", "expected_failure"))
    print(f"代码块：{len(blocks)} 个，其中可执行 {runnable} 个")

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
    ap.add_argument("--kind", choices=("auto", "regular", "finish"), default="auto")
    args = ap.parse_args()
    return lint(Path(args.part), args.kind)


if __name__ == "__main__":
    sys.exit(main())
