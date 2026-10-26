#!/usr/bin/env python3
"""Lathe 知识点账本对账：兼容新 Markdown 表与 legacy JSON。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lathe_common import (  # noqa: E402
    KnowledgeTableError,
    LayoutConflictError,
    LayoutNotFoundError,
    POINT_SOURCES,
    POINT_STATUSES,
    POINT_TYPES,
    headings,
    load_ledger,
    load_metadata,
    point_counts,
    point_progress,
    resolve_layout,
)

STATUSES = POINT_STATUSES
SRC = POINT_SOURCES
TAGS = POINT_TYPES
DEPTH = ("full", "foundation", "ch0", "tier1")
LEGACY_REQUIRED = ("id", "text", "src", "from", "tag", "plan_ref", "status")
LEGACY_OPTIONAL = ("original", "parent", "at", "depth", "dup_of", "note", "promised_by")
NUM_HEAD = re.compile(r"^(\d+)[.．、]")
PART_FILE = re.compile(r"part-\d{2}\.md")
PART_AT = re.compile(r"(part-\d{2}\.md)#(.+)")


def head_match(head: str, heads: Set[str]) -> str:
    """章节命中方式：exact / number / prefix / none。"""
    head = head.strip()
    if head in heads:
        return "exact"
    match = NUM_HEAD.match(head)
    if match and any(
        NUM_HEAD.match(item.strip()) and NUM_HEAD.match(item.strip()).group(1) == match.group(1)
        for item in heads
    ):
        return "number"
    if len(head) >= 6:
        hits = [item for item in heads if item.strip().startswith(head) or head.startswith(item.strip())]
        if len(hits) == 1:
            return "prefix"
    return "none"


def num_version(value: Any) -> tuple:
    return tuple(int(item) for item in re.findall(r"\d+", str(value or ""))[:3])


def field_size(value: Any) -> int:
    if isinstance(value, str):
        return len(value)
    if isinstance(value, list):
        return sum(field_size(item) for item in value) + max(len(value) - 1, 0)
    if isinstance(value, dict):
        return sum(field_size(item) for item in value.values()) + max(len(value) - 1, 0)
    return len(str(value))


def report_continuity(metadata: Dict[str, Any]) -> int:
    """报告 continuity 缓存预算；知识承接不再依赖 exercise_carry 镜像。"""
    continuity = metadata.get("continuity") or {}
    if not continuity:
        print("ℹ️ metadata 里没有 continuity 摘要：下次续写可重建")
        return 0
    soft, hard = 2200, 3000
    caps = {
        "covered_concepts": (24, 40),
        "open_threads": (8, 80),
        "fixed_numbers": (18, 40),
        "part_titles": (8, 60),
    }
    sizes = {
        key: field_size(value)
        for key, value in continuity.items()
        if key != "exercise_carry" and value not in (None, "", [], {})
    }
    total = sum(sizes.values())
    print("索引预算：软 %d 字 · 硬 %d 字 ｜ 实测 %d 字" % (soft, hard, total))
    for key in sorted(sizes, key=sizes.get, reverse=True):
        print("  %-20s%5d 字" % (key, sizes[key]))

    counts = {
        "covered_concepts": len(continuity.get("covered_concepts") or []),
        "open_threads": len(continuity.get("open_threads") or []),
        "fixed_numbers": len(continuity.get("fixed_numbers") or {}),
        "part_titles": len(continuity.get("part_titles") or {}),
    }
    problems: List[str] = []
    tips: List[str] = []
    for key, (cap, _) in caps.items():
        if counts[key] > cap:
            problems.append("%s %d 条 > 上限 %d 条" % (key, counts[key], cap))
            tips.append("%s：归档最旧的 %d 条" % (key, counts[key] - cap))
    for key in ("controlling_example", "next_hook", "metaphor"):
        if sizes.get(key, 0) > 200:
            problems.append("%s %d 字 > 200 字" % (key, sizes[key]))
    if total > hard:
        print("❌ 超硬上限 %d 字" % (total - hard))
        for tip in tips or ["优先归档 covered_concepts，其次 fixed_numbers"]:
            print("   - " + tip)
        return 1
    if problems:
        print("⚠️ 字段条数超限（下次写回归档）：")
        for problem in problems:
            print("   - " + problem)
        return 0
    if total > soft:
        print("⚠️ 超软上限：下次归档一次索引字段即可")
        return 0
    print("✅ 索引在预算内")
    return 0


def _point_tag(point: Dict[str, Any], row_line: Optional[int]) -> str:
    pid = point.get("id")
    if pid:
        return str(pid)
    return "第 %d 行" % row_line if row_line else "空 ID 条目"


def _check_at(
    tag: str,
    value: Any,
    parts: List[str],
    part_heads: Dict[str, Set[str]],
    errors: List[str],
    drifted: List[str],
    label: str = "at",
) -> None:
    match = PART_AT.fullmatch(str(value or ""))
    if not match:
        errors.append("%s %s 必须写成 part-NN.md#标题" % (tag, label))
        return
    target, head = match.groups()
    if target not in parts:
        errors.append("%s %s 指向不在 parts 里的文件：%r" % (tag, label, target))
        return
    how = head_match(head, part_heads.get(target, set()))
    if how == "none":
        errors.append("%s %s 的章节在 %s 里找不到：%r" % (tag, label, target, head))
    elif how != "exact":
        drifted.append("%s（%s#%s）" % (tag, target, head[:28]))


def _validate_table_cache(ledger: Any, points: List[Dict[str, Any]], errors: List[str]) -> None:
    table = ledger.table
    if table is None:
        return
    expected_progress = point_progress(points)
    if table.progress_cache is None:
        errors.append("知识表缺少进度缓存")
    elif table.progress_cache != expected_progress:
        errors.append(
            "进度缓存不一致：表头 %s，真实 %s"
            % (table.progress_cache, expected_progress)
        )
    expected_counts = point_counts(points)
    if table.status_cache is None:
        errors.append("知识表缺少状态缓存")
    elif table.status_cache != expected_counts:
        errors.append("状态缓存不一致：请按真实行重建表头统计")


def check(
    root: Path,
    receipt: Optional[str],
    force_legacy: bool = False,
    finish: bool = False,
    continuity: bool = False,
) -> int:
    errors: List[str] = []
    warnings: List[str] = []
    drifted: List[str] = []
    root = root.resolve()

    try:
        layout = resolve_layout(root)
    except LayoutConflictError as exc:
        print("❌ 布局 conflict：%s" % exc)
        return 1
    except LayoutNotFoundError as exc:
        print("❌ %s：先重建 metadata.json" % exc)
        return 1

    try:
        metadata = load_metadata(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("❌ metadata.json 无法读取：%s" % exc)
        return 1

    if continuity:
        return report_continuity(metadata)

    if not layout.ledger_path.is_file():
        if layout.kind == "legacy":
            print("⚠️ 账本 syllabus.json 不存在：旧教程，需要首次回填。")
            return 3
        print("❌ 新布局缺少 _lathe/knowledge-points.md")
        return 1

    try:
        ledger = load_ledger(layout)
    except KnowledgeTableError as exc:
        print("❌ knowledge-points.md 无法解析：")
        for message in exc.errors:
            print("   - " + message)
        return 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        name = "knowledge-points.md" if layout.kind == "new" else "syllabus.json"
        print("❌ %s 无法读取：%s" % (name, exc))
        return 1

    points = ledger.points
    raw = ledger.raw
    parts = metadata.get("parts", []) or []
    if not isinstance(parts, list):
        print("❌ metadata.parts 必须是数组")
        return 1
    plan = metadata.get("course_plan", []) or []
    part_versions = metadata.get("part_versions", {}) or {}
    if layout.kind == "new" and (not isinstance(plan, list) or not 2 <= len(plan) <= 12):
        warnings.append(
            "course_plan 建议为 2–12 个 Part 级大纲项（当前 %s 项）；它已不绑定知识点，仅作叙事参考"
            % len(plan)
        )
    elif layout.kind == "legacy" and isinstance(plan, list) and plan and not 2 <= len(plan) <= 12:
        warnings.append("legacy course_plan 为 %d 项，不在 2–12 的现行范围；旧课不强制迁移" % len(plan))

    def part_legacy(name: str) -> bool:
        if force_legacy:
            return True
        version = part_versions.get(name) or metadata.get("lathe_version")
        return num_version(version) < (0, 6, 0)

    if force_legacy:
        print("ℹ️ 已按 --legacy 运行：0.6.0 新增的正文提醒约束降级")

    part_heads: Dict[str, Set[str]] = {}
    for part in parts:
        path = root / part
        if path.is_file():
            part_heads[part] = set(headings(path.read_text(encoding="utf-8")))
    due_promises: List[tuple] = []

    if layout.kind == "legacy":
        document = ledger.document or {}
        if document.get("slug") != metadata.get("slug"):
            errors.append("slug 不一致：账本 %r ≠ metadata %r" % (document.get("slug"), metadata.get("slug")))
        # 只检查 points 数组内部的物理行，不要求 `id` 必须是对象的第一个键。
        # legacy 写回必须保留未知字段与原键序；用 `startswith('{\"id\"')` 会误报合法 round-trip。
        block = re.search(r'"points"\s*:\s*\[\s*\n(?P<body>.*?)\n\s*\]', raw, flags=re.DOTALL)
        one_line = []
        if block:
            for line in block.group("body").splitlines():
                candidate = line.strip().rstrip(",")
                if not candidate:
                    continue
                try:
                    value = json.loads(candidate)
                except json.JSONDecodeError:
                    continue
                if isinstance(value, dict):
                    one_line.append(value)
        if len(one_line) != len(points):
            errors.append("书写格式：应一行一个知识点（检测到 %d 行 / %d 条）" % (len(one_line), len(points)))
    else:
        _validate_table_cache(ledger, points, errors)
        if ledger.table is not None and ledger.table.schema == "0.6.1":
            old = "、".join(
                "%s→Part %s" % (point.get("id"), point.get("plan_ref"))
                for point in points
                if point.get("plan_ref") is not None
            )
            warnings.append(
                "检测到 0.6.1 八列知识表：下一次写入需先展示迁移对照并确认；"
                "迁移后删除 计划 Part 列" + ("（旧值：%s）" % old if old else "")
            )

    ids = [point.get("id") for point in points]
    nonempty_ids = [str(pid) for pid in ids if pid not in (None, "")]
    duplicates = sorted({pid for pid in nonempty_ids if nonempty_ids.count(pid) > 1})
    if duplicates:
        errors.append("id 重复：%s" % duplicates)

    row_lines = ledger.table.row_lines if ledger.table else [None] * len(points)
    for point, row_line in zip(points, row_lines):
        tag = _point_tag(point, row_line)
        pid = point.get("id")
        if pid in (None, ""):
            errors.append("%s ID 为空：请在写作前补成全课程唯一 ID" % tag)
        if layout.kind == "legacy":
            missing = [field for field in LEGACY_REQUIRED if field not in point]
            if missing:
                errors.append("%s 缺必填字段 %s" % (tag, missing))
                continue
        else:
            missing = [field for field in ("id", "text", "src", "tag", "status") if field not in point]
            if missing:
                errors.append("%s 缺字段 %s" % (tag, missing))
                continue

        status = point.get("status")
        if status not in STATUSES:
            errors.append("%s 非法状态 %r" % (tag, status))
        if point.get("src") not in SRC:
            errors.append("%s 非法来源 %r" % (tag, point.get("src")))
        if point.get("tag") not in TAGS:
            errors.append("%s 非法类型 %r" % (tag, point.get("tag")))
        if not str(point.get("text") or "").strip():
            errors.append("%s 知识点为空" % tag)
        elif len(str(point.get("text"))) > 60:
            errors.append("%s 知识点超过 60 字" % tag)

        if layout.kind == "legacy":
            for field in LEGACY_OPTIONAL:
                if field in point and point[field] in (None, "", []):
                    warnings.append("%s 可选字段 %s 为空，应整个省略" % (tag, field))
            if point.get("src") == "user" and not point.get("original"):
                errors.append("%s 用户条目没有逐字保留 original" % tag)
        elif point.get("src") == "user" and not any(
            marker in str(point.get("note") or "") for marker in ("用户原文：", "用户原文=")
        ):
            errors.append("%s 用户条目的备注必须逐字保留「用户原文：…」或「用户原文=…」" % tag)

        at = point.get("at")
        promised = point.get("promised_by")
        dup_of = point.get("dup_of")
        if status == "taught":
            if not at:
                errors.append("%s taught 缺少 at:part-NN.md#标题" % tag)
            else:
                _check_at(tag, at, parts, part_heads, errors, drifted)
            if layout.kind == "legacy" and point.get("depth") not in DEPTH:
                errors.append("%s 已讲但 depth 非法：%r" % (tag, point.get("depth")))
        elif at:
            errors.append("%s 状态 %s 不应使用 at:" % (tag, status))

        if promised:
            if not PART_FILE.fullmatch(str(promised)):
                errors.append("%s promise 必须写成 part-NN.md" % tag)
            elif str(promised) not in parts:
                errors.append("%s promise 指向不在 parts 里的文件：%s" % (tag, promised))
            if layout.kind == "new" and status not in ("planned", "queued"):
                errors.append("%s 只有 planned/queued 可使用 promise:" % tag)
            elif status in ("planned", "queued") and str(promised) in parts:
                due_promises.append((str(pid), str(promised)))

        if status == "duplicate":
            if not dup_of:
                errors.append("%s duplicate 缺少 dup:<ID或part引用>" % tag)
            else:
                dup_text = str(dup_of)
                if PART_AT.fullmatch(dup_text):
                    _check_at(tag, dup_text, parts, part_heads, errors, drifted, "dup")
                elif dup_text not in nonempty_ids:
                    errors.append("%s dup 引用的 ID 不存在：%s" % (tag, dup_text))
                elif dup_text == str(pid):
                    errors.append("%s dup 不能引用自身" % tag)
        elif dup_of and layout.kind == "new":
            errors.append("%s 只有 duplicate 可使用 dup:" % tag)

        if status in ("self-study", "dropped_by_user") and not str(point.get("note") or "").strip():
            errors.append("%s %s 缺少备注原因" % (tag, status))

        note_text = str(point.get("note") or "")
        depth_match = re.search(r"(?:^|[；;]\s*)深度=([^；;]+)", note_text)
        if depth_match:
            value = depth_match.group(1).strip()
            if value not in ("做", "讲", "知"):
                errors.append("%s 备注中的深度必须是 深度=做 / 深度=讲 / 深度=知，当前 %r" % (tag, value))
        elif "原编号=" in note_text:
            errors.append("%s 外部导入条目缺少 深度=做/讲/知" % tag)
        mastery_match = re.search(r"(?:^|[；;]\s*)个人掌握=([^；;]+)", note_text)
        if mastery_match and mastery_match.group(1).strip() not in ("完成", "未完成"):
            errors.append("%s 个人掌握必须是 完成 / 未完成，不得作为 taught 状态" % tag)

    # duplicate 必须直接指向一个真实主条目，不能形成 duplicate 链或环。
    by_id = {str(point.get("id")): point for point in points if point.get("id")}
    for point in points:
        if point.get("status") != "duplicate":
            continue
        target_id = str(point.get("dup_of") or "")
        if PART_AT.fullmatch(target_id):
            continue
        target = by_id.get(target_id)
        if target and target.get("status") not in ("taught", "planned", "queued"):
            errors.append(
                "%s dup 必须直接指向 taught/planned/queued 主条目，不能指向 %s"
                % (_point_tag(point, None), target.get("status"))
            )

    if due_promises:
        warnings.append(
            "到期承诺 %d 条：%s；续写应优先兑现，收尾会列为剩余知识点"
            % (len(due_promises), "、".join("%s(%s)" % item for item in due_promises))
        )

    queued = {point.get("id") for point in points if point.get("status") == "queued" and point.get("id")}
    taught = {point.get("id") for point in points if point.get("status") == "taught" and point.get("id")}
    if len(queued) > 14:
        warnings.append("queued %d 条 > 14：已超过默认积压闸门" % len(queued))

    for part in parts:
        path = root / part
        if "-review" in part or not path.exists():
            continue
        for line in re.findall(r"\*本题涉及的知识点（[^\n]*", path.read_text(encoding="utf-8")):
            if part_legacy(part) and "积压 ID" not in line:
                continue
            match = re.search(r"积压 ID `([^`]+)`", line)
            if not match:
                errors.append("%s：档 3 提醒没有写积压 ID" % part)
            elif match.group(1) not in nonempty_ids:
                errors.append("%s：档 3 提醒引用的 %s 不在知识表里" % (part, match.group(1)))
            elif match.group(1) not in queued | taught:
                state = next(point.get("status") for point in points if point.get("id") == match.group(1))
                warnings.append("%s：档 3 提醒引用的 %s 状态已是 %s" % (part, match.group(1), state))

    counts = point_counts(points)
    summary = " · ".join("%s %d" % (status, count) for status, count in counts.items() if count)
    print("账本：%s（共 %d 条）" % (summary or "无条目", len(points)))

    if finish:
        remaining = [point for point in points if point.get("status") in ("planned", "queued")]
        remaining_ids = [str(point.get("id")) for point in remaining if point.get("id")]
        if remaining:
            print("收尾检查：仍有 %d 条未学知识点（允许收尾，但总结必须写提示）" % len(remaining))
            for point in remaining:
                print(
                    "  - %s｜%s｜%s｜%s"
                    % (point.get("id"), point.get("status"), point.get("tag"), point.get("text"))
                )
            print(
                "必写提示：完成状态：未学完（剩余 %d 条）；未讲清单按 ID 列全；"
                "可用 /lathe 续写 <slug> 继续学习。" % len(remaining)
            )
            if receipt:
                path = root / receipt
                if not path.is_file():
                    errors.append("总结文件不存在：%s" % receipt)
                else:
                    text = path.read_text(encoding="utf-8")
                    if "未学完" not in text:
                        errors.append("总结缺少「未学完」提示")
                    if "续写" not in text:
                        errors.append("总结缺少「续写」继续学习提示")
                    missing = [pid for pid in remaining_ids if pid not in text]
                    if missing:
                        errors.append("总结未讲清单缺少 ID：%s" % "、".join(missing))
        else:
            print("收尾检查：全部知识点已学完或已处置（无 planned/queued）")
        for warning in warnings:
            print("⚠️ " + warning)
        for error in errors:
            print("❌ " + error)
        if errors:
            return 1
        return 0

    if receipt:
        mine = [
            point
            for point in points
            if point.get("status") == "taught" and str(point.get("at") or "").startswith(receipt + "#")
        ]
        heads = headings((root / receipt).read_text(encoding="utf-8")) if (root / receipt).exists() else []
        build_points = [
            point
            for point in mine
            if point.get("tag") in ("main", "mergeable")
            and point.get("depth") not in ("foundation", "ch0")
        ]
        foundation_points = [
            point for point in mine if point.get("tag") == "foundation" or point.get("depth") == "foundation"
        ]
        carry_points = [
            point for point in mine if point.get("tag") == "carry" or point.get("depth") == "ch0"
        ]
        written_version = num_version(part_versions.get(receipt) or metadata.get("lathe_version"))
        pool_remaining = [
            point
            for point in points
            if point.get("status") in ("planned", "queued")
            and point.get("tag") in ("main", "mergeable")
        ]
        if written_version >= (0, 6, 1):
            if len(build_points) > 7:
                errors.append(
                    "%s 构建知识点 %d 个，超过 7 个上限（地基 %d、承接 %d 不占构建名额）"
                    % (receipt, len(build_points), len(foundation_points), len(carry_points))
                )
            elif len(build_points) < 4:
                warnings.append(
                    "%s 构建知识点只有 %d 个：候选不足 4 时不凑数；有候选则在回执说明未选原因"
                    % (receipt, len(build_points))
                )
        if pool_remaining:
            preview = "、".join(str(point.get("id")) for point in pool_remaining[:8])
            if len(pool_remaining) > 8:
                preview += "…"
            print("池中剩余构建候选：%d 条（行序前 8：%s）" % (len(pool_remaining), preview))
        depth_counts = Counter()
        for point in mine:
            match = re.search(r"(?:^|[；;]\s*)深度=([做讲知])(?:[；;]|$)", str(point.get("note") or ""))
            if match:
                depth_counts[match.group(1)] += 1

        def section_name(head: str) -> str:
            match = re.match(r"(\d+)\.", head)
            if match:
                return "§" + match.group(1)
            return "§%d" % (heads.index(head) + 1) if head in heads else head

        cover = " · ".join(
            "%s→%s ✅" % (point.get("id"), section_name(str(point.get("at")).split("#", 1)[1]))
            for point in mine
        )
        print("本部分覆盖：%s" % (cover or "（无 taught 条目指向该 part）"))
        print("当前积压：%s" % ("、".join(sorted(str(item) for item in queued)) if queued else "无"))
        if depth_counts:
            print(
                "深度：做 %d · 讲 %d · 知 %d"
                % (depth_counts.get("做", 0), depth_counts.get("讲", 0), depth_counts.get("知", 0))
            )

    if drifted:
        print("ℹ️ %d 条章节文字已按章号命中：%s" % (len(drifted), "、".join(drifted[:6])))
    for warning in warnings:
        print("⚠️ " + warning)
    if errors:
        print("❌ 发现 %d 处不一致：" % len(errors))
        for error in errors:
            print("   - " + error)
        return 1
    print("✅ 账本闭合")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Lathe 知识点账本对账")
    parser.add_argument("tutorial_dir")
    parser.add_argument(
        "--receipt",
        metavar="PART",
        help="打印该 part 的覆盖回执；与 --finish 同用时校验总结的未学完提示",
    )
    parser.add_argument("--legacy", action="store_true", help="按 0.6.0 之前规则检查历史正文")
    parser.add_argument("--finish", action="store_true", help="列出全部剩余点；与 --receipt 同用时校验总结的未学完提示")
    parser.add_argument("--continuity", action="store_true", help="只报 continuity 索引预算")
    args = parser.parse_args()
    return check(Path(args.tutorial_dir), args.receipt, args.legacy, args.finish, args.continuity)


if __name__ == "__main__":
    sys.exit(main())
