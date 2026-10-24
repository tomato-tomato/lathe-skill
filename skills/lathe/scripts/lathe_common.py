"""Lathe 脚本共用的小工具：代码块解析、章节标题、metadata/账本读取。

纯标准库，Python 3.9+。被同目录的 ledger_check.py / part_lint.py / trial_run.py 引用。
"""

from __future__ import annotations

import json
import re
from pathlib import Path

BLOCK_TYPES = ("runnable", "fragment", "exercise", "text", "output", "expected_failure")
DIAGRAM_LANGS = ("mermaid", "plantuml", "dot")
FENCE = re.compile(r"^```([^\n]*)\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
PART_NO = re.compile(r"part-(\d{2})")


def block_type(info: str) -> str:
    """info string 里第一个属于类型表的词就是类型；未标记按 runnable，图表语言按 text。"""
    tokens = info.strip().split()
    for token in tokens:
        if token in BLOCK_TYPES:
            return token
    if tokens and tokens[0] in DIAGRAM_LANGS:
        return "text"
    return "runnable"


def block_lang(info: str) -> str:
    tokens = info.strip().split()
    if not tokens or tokens[0] in BLOCK_TYPES:
        return ""
    return tokens[0]


def is_marked(info: str) -> bool:
    tokens = info.strip().split()
    return any(t in BLOCK_TYPES for t in tokens) or (bool(tokens) and tokens[0] in DIAGRAM_LANGS)


def code_blocks(text: str) -> list[dict]:
    """返回 [{info, lang, type, body, line}]；line 是 fence 起始行号（1 起）。"""
    blocks = []
    for m in FENCE.finditer(text):
        info, body = m.group(1), m.group(2)
        blocks.append(
            {
                "info": info.strip(),
                "lang": block_lang(info),
                "type": block_type(info),
                "marked": is_marked(info),
                "body": body,
                "line": text.count("\n", 0, m.start()) + 1,
            }
        )
    return blocks


def strip_code(text: str) -> str:
    return FENCE.sub("", text)


def headings(text: str, level: int = 2) -> list[str]:
    prefix = "#" * level + " "
    out = []
    for line in strip_code(text).splitlines():
        if line.startswith(prefix):
            out.append(line[len(prefix):].strip())
    return out


def part_number(name: str) -> int:
    m = PART_NO.match(Path(name).name)
    return int(m.group(1)) if m else 0


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def section(text: str, title_prefix: str) -> str:
    """取某个 `## ` 小节的正文（不含代码块外的下一个 ## 之后的内容）。"""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.startswith("## ") and line[3:].strip().startswith(title_prefix):
            start = i + 1
            continue
        if start is not None and line.startswith("## "):
            return "\n".join(lines[start:i])
    return "\n".join(lines[start:]) if start is not None else ""
