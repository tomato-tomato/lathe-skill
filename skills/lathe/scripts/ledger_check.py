#!/usr/bin/env python3
"""知识点账本对账：syllabus.json × metadata.json × part 正文。

用法：
    python3 <SKILL_DIR>/scripts/ledger_check.py <教程目录>
    python3 <SKILL_DIR>/scripts/ledger_check.py <教程目录> --receipt part-03.md

检查 references/knowledge-ledger.md「账本不变量」的全部机械可查项：
  字段与状态合规、id 唯一、ID 镜像（metadata.syllabus_ids）、queued = knowledge_backlog、
  taught 的 at 指向真实章节、planned 不悬空、self-study 同步 research.md、
  一行一条与可选字段省略、积压条目字段与上限、正文里档 3 提醒带积压 ID 且不过期。
--receipt 额外打印该 part 的「本部分覆盖」行，供覆盖回执直接粘贴。

退出码：0 = 闭合（可能有警告）；1 = 有不一致；3 = 账本不存在（旧教程，需要回填）。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lathe_common import headings, load_json, part_number  # noqa: E402

STATUSES = ("planned", "queued", "taught", "self-study", "dropped_by_user", "duplicate")
SRC = ("user", "plan", "exercise", "deepen")
TAGS = ("main", "foundation", "mergeable")
DEPTH = ("full", "foundation", "ch0", "tier1")
REQUIRED = ("id", "text", "src", "from", "tag", "plan_ref", "status")
OPTIONAL = ("original", "parent", "at", "depth", "dup_of", "note")
BACKLOG_FIELDS = ("id", "text", "from", "plan_ref", "priority")
NUM_HEAD = re.compile(r"^(\d+)[.．、]")


def head_match(head: str, heads: set[str]) -> str:
    """at 的章节命中方式：exact / number / prefix / none。

    小节标题里可能带数字、措辞也可能因勘误改动，所以带章号的 `at` 优先按章号命中——
    标题文字变了不算断链（避免「改标题 → 账本自检失败 → 而勘误不许改账本」的死结）。
    """
    head = head.strip()
    if head in heads:
        return "exact"
    m = NUM_HEAD.match(head)
    if m and any(NUM_HEAD.match(h.strip()) and NUM_HEAD.match(h.strip()).group(1) == m.group(1) for h in heads):
        return "number"
    if any(h.strip().startswith(head) or head.startswith(h.strip()) for h in heads):
        return "prefix"
    return "none"



def check(root: Path, receipt: str | None, force_legacy: bool = False) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    drifted: list[str] = []
    meta_path, ledger_path = root / "metadata.json", root / "syllabus.json"
    if not meta_path.exists():
        print(f"❌ {meta_path} 不存在：先按 metadata.md「metadata.json 自愈」重建")
        return 1
    metadata = load_json(meta_path)
    nums = tuple(int(x) for x in re.findall(r"\d+", str(metadata.get("lathe_version") or ""))[:3])
    legacy = force_legacy or nums < (0, 6, 0)
    if force_legacy:
        print("ℹ️ 已按 --legacy 运行：0.6.0 新增的账本约束降级（检查历史部分时使用）")
    if not ledger_path.exists():
        print("⚠️ 账本 syllabus.json 不存在：旧教程，需要首次回填。")
        print("   由谁建：**下一次 `/lathe 续写 <slug>`** 会按 knowledge-ledger.md「旧教程首次回填」建账，")
        print("   回填结果作为写前计划确认的一部分交给你过目；本脚本只读不建。")
        print("   现在只想看覆盖度：`/lathe 列表 <slug>`（会显示「账本：未建立」）。")
        return 3
    raw = ledger_path.read_text(encoding="utf-8")
    try:
        ledger = load_json(ledger_path)
    except ValueError as exc:
        print(f"❌ syllabus.json 不是合法 JSON：{exc}——按「账本缺失或损坏」重建")
        return 1

    parts = metadata.get("parts", [])
    points = ledger.get("points", [])
    plan = metadata.get("course_plan", [])
    backlog = metadata.get("knowledge_backlog", []) or []
    part_heads = {p: set(headings((root / p).read_text(encoding="utf-8"))) for p in parts if (root / p).exists()}
    written = {part_number(p) for p in parts if "-review" not in p}

    if ledger.get("slug") != metadata.get("slug"):
        errors.append(f"slug 不一致：账本 {ledger.get('slug')!r} ≠ metadata {metadata.get('slug')!r}")

    # 格式：一行一条
    one_line = [ln for ln in raw.splitlines() if ln.strip().startswith('{"id":')]
    if len(one_line) != len(points):
        errors.append(f"书写格式：应一行一个知识点（检测到 {len(one_line)} 行 / {len(points)} 条）")

    ids = [pt.get("id") for pt in points]
    dups = sorted({i for i in ids if ids.count(i) > 1})
    if dups:
        errors.append(f"id 重复：{dups}")

    mirror = metadata.get("syllabus_ids")
    if mirror is None:
        warnings.append("metadata.syllabus_ids 缺失：写回时按账本补上（旧教程首次建账属正常）")
    else:
        vanished = sorted(set(mirror) - set(ids))
        unregistered = sorted(set(ids) - set(mirror))
        if vanished:
            errors.append(f"账本条目凭空消失：{vanished}（syllabus_ids 里有、账本里没有）——停止写入，按「账本缺失或损坏」恢复")
        if unregistered:
            errors.append(f"新增条目没登记进 metadata.syllabus_ids：{unregistered}")
        if mirror != sorted(mirror):
            warnings.append("syllabus_ids 未按字母序排列")

    for pt in points:
        pid = pt.get("id")
        tag = f"{pid}"
        missing = [f for f in REQUIRED if f not in pt]
        if missing:
            errors.append(f"{tag} 缺必填字段 {missing}")
            continue
        status = pt["status"]
        if status not in STATUSES:
            errors.append(f"{tag} 非法 status {status!r}")
        if pt["src"] not in SRC:
            errors.append(f"{tag} 非法 src {pt['src']!r}")
        if pt["tag"] not in TAGS:
            errors.append(f"{tag} 非法 tag {pt['tag']!r}")
        if len(str(pt["text"])) > 60:
            errors.append(f"{tag} text 超过 60 字")
        for opt in OPTIONAL:
            if opt in pt and pt[opt] in (None, "", []):
                warnings.append(f"{tag} 可选字段 {opt} 为空，应整个省略")
        if pt["src"] == "user" and not pt.get("original"):
            errors.append(f"{tag} 用户条目没有逐字保留 original")
        if status == "taught":
            target, _, head = (pt.get("at") or "").partition("#")
            if pt.get("depth") not in DEPTH:
                errors.append(f"{tag} 已讲但 depth 非法：{pt.get('depth')!r}")
            if target not in parts:
                errors.append(f"{tag} at 指向不在 parts 里的文件：{target!r}")
            else:
                how = head_match(head, part_heads.get(target, set()))
                if how == "none":
                    errors.append(f"{tag} at 的章节在 {target} 里找不到：{head!r}")
                elif how != "exact":
                    drifted.append(f"{tag}（{target}#{head[:28]}）")
        elif pt.get("at"):
            errors.append(f"{tag} 状态 {status} 不应有 at")
        if status == "duplicate" and not pt.get("dup_of"):
            errors.append(f"{tag} duplicate 没写 dup_of")
        if status in ("self-study", "dropped_by_user") and not pt.get("note"):
            errors.append(f"{tag} {status} 没写 note（何时、因何——只能来自用户显式选择）")
        if status == "self-study":
            research = root / "research.md"
            if not research.exists() or pid not in research.read_text(encoding="utf-8"):
                errors.append(f"{tag} self-study 没同步到 research.md 的 ## Self-study Backlog")
        if status == "planned":
            ref = pt["plan_ref"]
            if ref is None:
                if not pt.get("note"):
                    errors.append(f"{tag} planned 但没有 plan_ref，也没有 note 说明归属")
            else:
                item = next((i for i in plan if i.get("part") == ref), None)
                if item is None and isinstance(ref, int) and 0 < ref <= len(plan):
                    item = plan[ref - 1]
                if item is None:
                    errors.append(f"{tag} planned 的 plan_ref {ref} 在 course_plan 里不存在")
                elif item.get("part") in written:
                    errors.append(f"{tag} 仍是 planned，但所属 plan 项（Part {item.get('part')}）已经写完——悬空条目")

    queued = {pt.get("id") for pt in points if pt.get("status") == "queued"}
    backlog_ids = {b.get("id") for b in backlog}
    if queued != backlog_ids:
        errors.append(
            f"账本 queued ≠ knowledge_backlog（只在账本：{sorted(queued - backlog_ids)}；只在积压：{sorted(backlog_ids - queued)}）"
        )
    for b in backlog:
        miss = [f for f in BACKLOG_FIELDS if f not in b]
        if miss:
            errors.append(f"积压 {b.get('id')} 缺字段 {miss}")
        if b.get("priority") not in (None, "core"):
            errors.append(f"积压 {b.get('id')} 的 priority 只能是 core（自学条目只放 research.md）")
    if len(backlog) > 14:
        warnings.append(f"积压 {len(backlog)} 条 > 14：只有闸门选 ① 扩 Part 后才允许（每多 1 个 Part +7）")

    taught = {pt.get("id") for pt in points if pt.get("status") == "taught"}
    for p in parts:
        path = root / p
        if "-review" in p or not path.exists():
            continue
        for line in re.findall(r"\*本题涉及的知识点（[^\n]*", path.read_text(encoding="utf-8")):
            if legacy and "积压 ID" not in line:
                continue  # 0.6.0 之前写的部分不要求写积压 ID
            m = re.search(r"积压 ID `([^`]+)`", line)
            if not m:
                errors.append(f"{p}：档 3 提醒没有写积压 ID")
            elif m.group(1) not in ids:
                errors.append(f"{p}：档 3 提醒引用的 {m.group(1)} 不在账本里")
            elif m.group(1) not in queued | taught:
                warnings.append(f"{p}：档 3 提醒引用的 {m.group(1)} 状态已是 {next(x['status'] for x in points if x['id'] == m.group(1))}")

    counts = {s: sum(1 for pt in points if pt.get("status") == s) for s in STATUSES}
    summary = " · ".join(f"{s} {n}" for s, n in counts.items() if n)
    print(f"账本：{summary}（共 {len(points)} 条）")

    if receipt:
        mine = [pt for pt in points if pt.get("status") == "taught" and (pt.get("at") or "").startswith(receipt + "#")]
        heads = headings((root / receipt).read_text(encoding="utf-8")) if (root / receipt).exists() else []
        def sec(h: str) -> str:
            m = re.match(r"(\d+)\.", h)
            return f"§{m.group(1)}" if m else f"§{heads.index(h) + 1}" if h in heads else h
        cover = " · ".join(f"{pt['id']}→{sec(pt['at'].split('#', 1)[1])} ✅" for pt in mine)
        print(f"本部分覆盖：{cover or '（无 taught 条目指向该 part）'}")
        qd = sorted(queued)
        print(f"当前积压：{'、'.join(qd) if qd else '无'}")

    if drifted:
        print(
            f"ℹ️ {len(drifted)} 条 at 的标题文字与现有小节不一致（已按章号命中，不算断链）："
            f"{'、'.join(drifted[:6])}" + ("…" if len(drifted) > 6 else "")
            + "——择机把 at 的标题部分刷新即可，状态与条目都不用动"
        )
    for w in warnings:
        print(f"⚠️ {w}")
    if errors:
        print(f"❌ 发现 {len(errors)} 处不一致：")
        for e in errors:
            print(f"   - {e}")
        return 1
    print("✅ 账本闭合")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Lathe 知识点账本对账")
    ap.add_argument("tutorial_dir")
    ap.add_argument("--receipt", metavar="PART", help="打印该 part 的「本部分覆盖」行，如 part-03.md")
    ap.add_argument("--legacy", action="store_true", help="按 0.6.0 之前的规则检查（档 3 积压 ID 一条降级）")
    args = ap.parse_args()
    return check(Path(args.tutorial_dir), args.receipt, args.legacy)


if __name__ == "__main__":
    sys.exit(main())
