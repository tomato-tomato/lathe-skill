"""Lathe 脚本共用工具：双布局、知识表、代码块与章节解析。

纯标准库，兼容 Python 3.9+。
"""

from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

BLOCK_TYPES = ("runnable", "fragment", "exercise", "text", "output", "expected_failure")
DIAGRAM_LANGS = ("mermaid", "plantuml", "dot")
FENCE = re.compile(r"^```([^\n]*)\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
PART_NO = re.compile(r"part-(\d{2})")

POINT_SOURCES = ("user", "plan", "exercise", "deepen")
POINT_TYPES = ("main", "foundation", "mergeable", "carry")
POINT_STATUSES = ("planned", "queued", "taught", "self-study", "dropped_by_user", "duplicate")
KNOWLEDGE_HEADERS = ("ID", "知识点", "来源", "类型", "计划 Part", "状态", "已讲位置 / 承诺来源", "备注")


class LayoutError(ValueError):
    """教程辅助文件布局错误。"""


class LayoutConflictError(LayoutError):
    """新旧布局标记同时出现。"""


class LayoutNotFoundError(LayoutError):
    """没有找到 metadata.json。"""


class KnowledgeTableError(ValueError):
    """knowledge-points.md 结构无法可靠解析。"""

    def __init__(self, errors: Sequence[str]):
        self.errors = list(errors)
        super().__init__("；".join(self.errors))


@dataclass(frozen=True)
class TutorialLayout:
    kind: str
    root: Path
    support_dir: Path
    metadata_path: Path
    ledger_path: Path
    research_path: Path
    verify_result_path: Path
    verify_workspace_path: Path


@dataclass
class KnowledgeTable:
    points: List[Dict[str, Any]]
    row_lines: List[int]
    progress_cache: Optional[Tuple[int, int, int]]
    status_cache: Optional[Dict[str, int]]


@dataclass
class LedgerData:
    layout: TutorialLayout
    path: Path
    points: List[Dict[str, Any]]
    raw: str
    document: Optional[Dict[str, Any]] = None
    table: Optional[KnowledgeTable] = None


_NEW_MARKERS = (
    "_lathe/metadata.json",
    "_lathe/knowledge-points.md",
    "_lathe/research.md",
    "_lathe/verify-result.json",
    "_lathe/interview.md",
    "_lathe/verify-workspace",
)
_LEGACY_MARKERS = (
    "metadata.json",
    "syllabus.json",
    "research.md",
    "verify-result.json",
    "interview.md",
    ".lathe-verify",
)
_WRONG_NEW_NAMES = ("knowledge-points.md", "verify-workspace")
_WRONG_LEGACY_NAMES = ("_lathe/syllabus.json", "_lathe/.lathe-verify")


def _course_root(path: Union[str, Path]) -> Path:
    root = Path(path)
    return root.parent if root.is_file() else root


def _existing(root: Path, names: Sequence[str]) -> List[str]:
    return [name for name in names if (root / name).exists()]


def detect_layout(course_root: Union[str, Path]) -> str:
    """返回 ``new`` / ``legacy`` / ``conflict`` / ``missing``。

    metadata 决定整套辅助文件的位置；不允许从两个位置逐文件拼装。
    """
    root = _course_root(course_root)
    new_meta = (root / "_lathe" / "metadata.json").is_file()
    old_meta = (root / "metadata.json").is_file()
    new_seen = _existing(root, _NEW_MARKERS)
    old_seen = _existing(root, _LEGACY_MARKERS)
    wrong_new = _existing(root, _WRONG_NEW_NAMES)
    wrong_old = _existing(root, _WRONG_LEGACY_NAMES)

    if new_meta and old_meta:
        return "conflict"
    if new_meta:
        return "conflict" if old_seen or wrong_new or wrong_old else "new"
    if old_meta:
        return "conflict" if new_seen or wrong_new or wrong_old else "legacy"
    if (new_seen and old_seen) or wrong_new or wrong_old:
        return "conflict"
    return "missing"


def layout_conflicts(course_root: Union[str, Path]) -> List[str]:
    """列出导致 conflict 的路径，供命令行给出简洁诊断。"""
    root = _course_root(course_root)
    names = _NEW_MARKERS + _LEGACY_MARKERS + _WRONG_NEW_NAMES + _WRONG_LEGACY_NAMES
    return _existing(root, names)


def resolve_layout(course_root: Union[str, Path]) -> TutorialLayout:
    """按 metadata 所在位置解析整套辅助文件；混合布局立即拒绝。"""
    root = _course_root(course_root)
    kind = detect_layout(root)
    if kind == "conflict":
        found = "、".join(layout_conflicts(root)) or "新旧辅助文件"
        raise LayoutConflictError("conflict：检测到混合布局（%s）" % found)
    if kind == "missing":
        raise LayoutNotFoundError("未找到 metadata.json（检查根目录与 _lathe/）")
    if kind == "new":
        support = root / "_lathe"
        return TutorialLayout(
            kind="new",
            root=root,
            support_dir=support,
            metadata_path=support / "metadata.json",
            ledger_path=support / "knowledge-points.md",
            research_path=support / "research.md",
            verify_result_path=support / "verify-result.json",
            verify_workspace_path=support / "verify-workspace",
        )
    return TutorialLayout(
        kind="legacy",
        root=root,
        support_dir=root,
        metadata_path=root / "metadata.json",
        ledger_path=root / "syllabus.json",
        research_path=root / "research.md",
        verify_result_path=root / "verify-result.json",
        verify_workspace_path=root / ".lathe-verify",
    )


def resolve_support_file(course_root: Union[str, Path], name: str) -> Path:
    """按已解析布局返回辅助文件；ledger 名称在新旧布局间自动映射。"""
    layout = resolve_layout(course_root)
    aliases = {
        "metadata": layout.metadata_path,
        "metadata.json": layout.metadata_path,
        "ledger": layout.ledger_path,
        "syllabus.json": layout.ledger_path,
        "knowledge-points.md": layout.ledger_path,
        "research": layout.research_path,
        "research.md": layout.research_path,
        "verify-result": layout.verify_result_path,
        "verify-result.json": layout.verify_result_path,
        "verify-workspace": layout.verify_workspace_path,
        ".lathe-verify": layout.verify_workspace_path,
    }
    if name not in aliases:
        raise KeyError("未知辅助文件角色：%s" % name)
    return aliases[name]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_metadata(course_root: Union[str, Path]) -> Dict[str, Any]:
    layout = resolve_layout(course_root)
    data = load_json(layout.metadata_path)
    if not isinstance(data, dict):
        raise ValueError("metadata.json 顶层必须是对象")
    return data


def _split_table_row(line: str, line_no: int) -> List[str]:
    if not line.startswith("|") or not line.endswith("|"):
        raise KnowledgeTableError(["第 %d 行：表格行必须以 | 开始和结束" % line_no])
    cells: List[str] = []
    cell: List[str] = []
    text = line[1:-1]
    i = 0
    while i < len(text):
        char = text[i]
        if char == "\\" and i + 1 < len(text) and text[i + 1] == "|":
            cell.append("|")
            i += 2
            continue
        if char == "|":
            cells.append("".join(cell).strip())
            cell = []
        else:
            cell.append(char)
        i += 1
    cells.append("".join(cell).strip())
    return cells


def _parse_progress(lines: Sequence[str]) -> Tuple[Optional[Tuple[int, int, int]], List[str]]:
    found: Optional[Tuple[int, int, int]] = None
    errors: List[str] = []
    pattern = re.compile(r"^进度[：:]\s*(?:已完成|已讲)\s*(\d+)\s*/\s*计划内\s*(\d+)\s*[（(](\d+)%[）)]$")
    for no, line in enumerate(lines, 1):
        if not line.strip().startswith("进度"):
            continue
        match = pattern.fullmatch(line.strip())
        if not match:
            errors.append("第 %d 行：进度缓存格式错误" % no)
        elif found is not None:
            errors.append("第 %d 行：进度缓存重复" % no)
        else:
            found = tuple(int(x) for x in match.groups())  # type: ignore[assignment]
    return found, errors


def _parse_status_cache(lines: Sequence[str]) -> Tuple[Optional[Dict[str, int]], List[str]]:
    found: Optional[Dict[str, int]] = None
    errors: List[str] = []
    for no, line in enumerate(lines, 1):
        if not line.strip().startswith("状态"):
            continue
        match = re.fullmatch(r"状态[：:]\s*(.*?)(?:\s*[（(]共\s*\d+\s*条[）)])?", line.strip())
        if not match:
            errors.append("第 %d 行：状态缓存格式错误" % no)
            continue
        counts: Dict[str, int] = {}
        bad = False
        for item in re.split(r"\s*[·•]\s*", match.group(1)):
            piece = re.fullmatch(r"([a-z_-]+)\s+(\d+)", item.strip())
            if not piece or piece.group(1) in counts:
                bad = True
                break
            counts[piece.group(1)] = int(piece.group(2))
        if bad:
            errors.append("第 %d 行：状态缓存格式错误" % no)
        elif found is not None:
            errors.append("第 %d 行：状态缓存重复" % no)
        else:
            found = counts
    return found, errors


def parse_knowledge_table(text: str) -> KnowledgeTable:
    """严格解析固定八列知识表，不猜测损坏的 Markdown。"""
    lines = text.splitlines()
    progress, errors = _parse_progress(lines)
    status_cache, status_errors = _parse_status_cache(lines)
    errors.extend(status_errors)

    header_indexes: List[int] = []
    for index, line in enumerate(lines):
        if not line.lstrip().startswith("|"):
            continue
        try:
            cells = _split_table_row(line.strip(), index + 1)
        except KnowledgeTableError:
            continue
        if cells == list(KNOWLEDGE_HEADERS):
            header_indexes.append(index)
    if len(header_indexes) != 1:
        errors.append("知识表必须且只能有一个固定八列表头")
        raise KnowledgeTableError(errors)
    header = header_indexes[0]
    if header + 1 >= len(lines):
        errors.append("知识表缺少分隔行")
        raise KnowledgeTableError(errors)
    try:
        separator = _split_table_row(lines[header + 1].strip(), header + 2)
    except KnowledgeTableError as exc:
        errors.extend(exc.errors)
        raise KnowledgeTableError(errors)
    if len(separator) != 8 or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in separator):
        errors.append("第 %d 行：固定八列表头后必须是 Markdown 分隔行" % (header + 2))

    points: List[Dict[str, Any]] = []
    row_lines: List[int] = []
    index = header + 2
    while index < len(lines) and lines[index].strip().startswith("|"):
        line_no = index + 1
        try:
            cells = _split_table_row(lines[index].strip(), line_no)
        except KnowledgeTableError as exc:
            errors.extend(exc.errors)
            index += 1
            continue
        if len(cells) != 8:
            errors.append("第 %d 行：知识点必须正好 8 列（单元格里的 | 写成 \\|）" % line_no)
            index += 1
            continue
        pid, point_text, src, point_type, plan_cell, status, location, note = cells
        if plan_cell in ("", "—"):
            plan_ref = None
        elif re.fullmatch(r"[1-9]\d*", plan_cell):
            plan_ref = int(plan_cell)
        else:
            errors.append("第 %d 行：计划 Part 必须是正整数或 —" % line_no)
            plan_ref = plan_cell
        point: Dict[str, Any] = {
            "id": pid,
            "text": point_text,
            "src": src,
            "tag": point_type,
            "plan_ref": plan_ref,
            "status": status,
        }
        if note not in ("", "—"):
            point["note"] = note
        if location == "—":
            pass
        elif location == "":
            errors.append("第 %d 行：无位置时必须写 —" % line_no)
        elif location.startswith("at:"):
            point["at"] = location[3:]
        elif location.startswith("promise:"):
            point["promised_by"] = location[8:]
        elif location.startswith("dup:"):
            point["dup_of"] = location[4:]
        else:
            errors.append("第 %d 行：位置必须使用 at: / promise: / dup: / —" % line_no)
        points.append(point)
        row_lines.append(line_no)
        index += 1

    for later, line in enumerate(lines[index:], index + 1):
        if line.strip().startswith("|"):
            errors.append("第 %d 行：知识点数据行必须连续，一条物理行一条" % later)
    if errors:
        raise KnowledgeTableError(errors)
    return KnowledgeTable(points, row_lines, progress, status_cache)


def parse_knowledge_points(text: str) -> List[Dict[str, Any]]:
    """返回 Markdown ledger 的 canonical point dict 列表。"""
    return parse_knowledge_table(text).points


def point_counts(points: Sequence[Dict[str, Any]]) -> Dict[str, int]:
    return {status: sum(1 for point in points if point.get("status") == status) for status in POINT_STATUSES}


def point_progress(points: Sequence[Dict[str, Any]]) -> Tuple[int, int, int]:
    counts = point_counts(points)
    taught = counts["taught"]
    planned_total = taught + counts["planned"] + counts["queued"]
    percent = (taught * 100 + planned_total // 2) // planned_total if planned_total else 0
    return taught, planned_total, percent


def _markdown_cell(value: Any) -> str:
    text = str(value)
    if "\n" in text or "\r" in text:
        raise ValueError("知识表单元格不能包含换行")
    return text.replace("|", "\\|")


def _point_location(point: Dict[str, Any]) -> str:
    locations = [key for key in ("at", "promised_by", "dup_of") if point.get(key)]
    if len(locations) > 1:
        raise ValueError("知识点 %s 同时有多个位置字段" % point.get("id", ""))
    if not locations:
        return "—"
    key = locations[0]
    prefix = {"at": "at:", "promised_by": "promise:", "dup_of": "dup:"}[key]
    return prefix + str(point[key])


def render_knowledge_points(points: Sequence[Dict[str, Any]]) -> str:
    """把 canonical points 渲染成可重复生成的固定八列 Markdown。"""
    counts = point_counts(points)
    taught, total, percent = point_progress(points)
    status = " · ".join("%s %d" % (name, counts[name]) for name in POINT_STATUSES)
    lines = [
        "# 课程知识点与进度",
        "",
        "进度：已完成 %d / 计划内 %d（%d%%）" % (taught, total, percent),
        "状态：" + status,
        "",
        "| " + " | ".join(KNOWLEDGE_HEADERS) + " |",
        "|---|---|---|---|---:|---|---|---|",
    ]
    for point in points:
        cells = (
            point.get("id", ""),
            point.get("text", ""),
            point.get("src", ""),
            point.get("tag", ""),
            point.get("plan_ref") if point.get("plan_ref") is not None else "—",
            point.get("status", ""),
            _point_location(point),
            point.get("note", ""),
        )
        lines.append("| " + " | ".join(_markdown_cell(cell) for cell in cells) + " |")
    return "\n".join(lines) + "\n"


def load_ledger(course_root: Union[str, Path, TutorialLayout]) -> LedgerData:
    """加载新旧 ledger，并统一返回 canonical point dict。"""
    layout = course_root if isinstance(course_root, TutorialLayout) else resolve_layout(course_root)
    raw = layout.ledger_path.read_text(encoding="utf-8")
    if layout.kind == "new":
        table = parse_knowledge_table(raw)
        return LedgerData(layout, layout.ledger_path, table.points, raw, table=table)
    document = json.loads(raw)
    if not isinstance(document, dict) or not isinstance(document.get("points"), list):
        raise ValueError("syllabus.json 顶层必须是对象且 points 必须是数组")
    points = [copy.deepcopy(point) for point in document["points"]]
    if not all(isinstance(point, dict) for point in points):
        raise ValueError("syllabus.json 的每个知识点必须是对象")
    return LedgerData(layout, layout.ledger_path, points, raw, document=document)


def render_legacy_ledger(document: Dict[str, Any], points: Optional[Sequence[Dict[str, Any]]] = None) -> str:
    """写回 legacy JSON；顶层和 point 未知字段都保留，point 仍一行一条。"""
    data = copy.deepcopy(document)
    current = list(points) if points is not None else list(data.get("points", []))
    marker = "__LATHE_POINTS_PLACEHOLDER_061__"
    serialized = json.dumps(data, ensure_ascii=False)
    while marker in serialized:
        marker += "_"
    data["points"] = marker
    rendered = json.dumps(data, ensure_ascii=False, indent=2)
    compact = [json.dumps(point, ensure_ascii=False, separators=(",", ": ")) for point in current]
    replacement = "["
    if compact:
        replacement += "\n" + ",\n".join("    " + line for line in compact) + "\n  "
    replacement += "]"
    rendered = rendered.replace(json.dumps(marker), replacement, 1)
    return rendered + "\n"


def render_ledger(ledger: LedgerData, points: Optional[Sequence[Dict[str, Any]]] = None) -> str:
    current = list(points) if points is not None else ledger.points
    if ledger.layout.kind == "new":
        return render_knowledge_points(current)
    if ledger.document is None:
        raise ValueError("legacy ledger 缺少原始 JSON 对象")
    return render_legacy_ledger(ledger.document, current)


def write_ledger(ledger: LedgerData, points: Optional[Sequence[Dict[str, Any]]] = None) -> None:
    ledger.path.write_text(render_ledger(ledger, points), encoding="utf-8")


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
    return any(token in BLOCK_TYPES for token in tokens) or (bool(tokens) and tokens[0] in DIAGRAM_LANGS)


def code_blocks(text: str) -> List[Dict[str, Any]]:
    """返回 [{info, lang, type, body, line}]；line 是 fence 起始行号（1 起）。"""
    blocks: List[Dict[str, Any]] = []
    for match in FENCE.finditer(text):
        info, body = match.group(1), match.group(2)
        blocks.append(
            {
                "info": info.strip(),
                "lang": block_lang(info),
                "type": block_type(info),
                "marked": is_marked(info),
                "body": body,
                "line": text.count("\n", 0, match.start()) + 1,
            }
        )
    return blocks


def strip_code(text: str) -> str:
    return FENCE.sub("", text)


def headings(text: str, level: int = 2) -> List[str]:
    prefix = "#" * level + " "
    out: List[str] = []
    for line in strip_code(text).splitlines():
        if line.startswith(prefix):
            out.append(line[len(prefix):].strip())
    return out


def part_number(name: str) -> int:
    match = PART_NO.match(Path(name).name)
    return int(match.group(1)) if match else 0


def section(text: str, title_prefix: str) -> str:
    """取某个 ``## `` 小节正文。"""
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.startswith("## ") and line[3:].strip().startswith(title_prefix):
            start = index + 1
            continue
        if start is not None and line.startswith("## "):
            return "\n".join(lines[start:index])
    return "\n".join(lines[start:]) if start is not None else ""
