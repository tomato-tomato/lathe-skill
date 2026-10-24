#!/usr/bin/env python3
"""交付前试跑：把一个 part 的可执行代码块放进一次性临时目录，逐块编译 / 运行。

用法：
    python3 <SKILL_DIR>/scripts/trial_run.py <教程目录>/part-03.md [--run] [--edition 2024] [--keep]

对应 writing-core.md「交付前试跑」。不是 /lathe 验证：不写 verify-result.json、不改横幅与 status、
不用 .lathe-verify/、不碰用户项目；所有文件都在系统临时目录里，结束后删除（--keep 保留以便排查）。

各语言的处理（只用本机已有的工具，缺工具就记为「未执行」）：
  rust        rustc 编译（无 fn main 的块按库编译）；--run 时运行，20 秒超时
  python      py_compile；--run 时用 python3 运行，20 秒超时
  bash/sh/zsh/shell/console   只做 `bash -n` 语法检查，从不执行——命令要按检查点手动在临时工程里跑
  javascript/js/node          node --check；--run 时用 node 运行
  其他语言    记为「未执行（脚本不支持）」，按正文在临时工程里手动跑
依赖外部 crate / 模块 / 前文代码而无法单独编译的块，记为「需拼工程」：按正文插入说明在临时目录里拼出工程再跑。
expected_failure 块：编译或运行失败才算通过。

最后一行打印「试跑：…」，可直接贴进覆盖回执。退出码：0 = 无失败；1 = 有失败。
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lathe_common import code_blocks  # noqa: E402

NEEDS_PROJECT = re.compile(
    r"E0432|E0433|E0463|E0583|can't find crate|unresolved import|failed to resolve|"
    r"ModuleNotFoundError|No module named|Cannot find module"
)
SHELL = ("bash", "sh", "zsh", "shell", "console", "shell-session")
JS = ("javascript", "js", "node", "mjs")


def detect_edition(part: Path) -> str:
    for candidate in sorted(part.parent.glob("part-*.md")):
        text = candidate.read_text(encoding="utf-8")
        m = re.search(r'edition\s*=\s*"(20\d\d)"', text) or re.search(r"edition\s*(20\d\d)", text)
        if m:
            return m.group(1)
    return "2021"


def run(cmd: list[str], cwd: Path, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)


def first_error(stderr: str) -> str:
    for line in stderr.splitlines():
        if line.startswith("error") or "Error" in line:
            return line.strip()[:160]
    return stderr.strip().splitlines()[0][:160] if stderr.strip() else "（无错误输出）"


def try_block(block: dict, work: Path, idx: int, edition: str, do_run: bool) -> tuple[str, str]:
    lang = block["lang"].lower()
    body = block["body"]
    expect_fail = block["type"] == "expected_failure"

    def verdict(ok: bool, detail: str) -> tuple[str, str]:
        if expect_fail:
            return ("pass", "按预期失败") if not ok else ("fail", "预期失败却成功了")
        return ("pass", detail) if ok else ("fail", detail)

    if lang in ("rust", "rs"):
        if not shutil.which("rustc"):
            return "skip", "本机没有 rustc"
        src = work / f"b{idx}.rs"
        src.write_text(body, encoding="utf-8")
        is_bin = re.search(r"\bfn\s+main\s*\(", body) is not None
        cmd = ["rustc", "--edition", edition, "-A", "warnings", "-o", str(work / f"b{idx}"), str(src)]
        if not is_bin:
            cmd[1:1] = ["--crate-type", "lib"]
        res = run(cmd, work)
        if res.returncode != 0:
            if NEEDS_PROJECT.search(res.stderr) and not expect_fail:
                return "project", first_error(res.stderr)
            return verdict(False, "编译失败：" + first_error(res.stderr))
        if do_run and is_bin:
            try:
                out = run([str(work / f"b{idx}")], work, timeout=20)
            except subprocess.TimeoutExpired:
                return verdict(False, "运行超时（20 s）")
            return verdict(out.returncode == 0, f"运行退出码 {out.returncode}")
        return verdict(True, "编译通过" + ("（未运行，加 --run）" if is_bin else "（库）"))

    if lang in ("python", "py", "python3"):
        src = work / f"b{idx}.py"
        src.write_text(body, encoding="utf-8")
        res = run([sys.executable, "-m", "py_compile", str(src)], work)
        if res.returncode != 0:
            return verdict(False, "语法错误：" + first_error(res.stderr))
        if do_run:
            try:
                out = run([sys.executable, str(src)], work, timeout=20)
            except subprocess.TimeoutExpired:
                return verdict(False, "运行超时（20 s）")
            if out.returncode != 0 and NEEDS_PROJECT.search(out.stderr) and not expect_fail:
                return "project", first_error(out.stderr)
            return verdict(out.returncode == 0, f"运行退出码 {out.returncode}")
        return verdict(True, "语法通过")

    if lang in SHELL:
        if not shutil.which("bash"):
            return "skip", "本机没有 bash"
        src = work / f"b{idx}.sh"
        src.write_text(body, encoding="utf-8")
        res = run(["bash", "-n", str(src)], work)
        if res.returncode != 0 and not expect_fail:
            return "fail", "shell 语法错误：" + first_error(res.stderr)
        return "manual", "命令块只做语法检查，需在临时工程里按检查点手动跑"

    if lang in JS:
        if not shutil.which("node"):
            return "skip", "本机没有 node"
        src = work / f"b{idx}.js"
        src.write_text(body, encoding="utf-8")
        res = run(["node", "--check", str(src)], work)
        if res.returncode != 0:
            return verdict(False, "语法错误：" + first_error(res.stderr))
        if do_run:
            try:
                out = run(["node", str(src)], work, timeout=20)
            except subprocess.TimeoutExpired:
                return verdict(False, "运行超时（20 s）")
            if out.returncode != 0 and NEEDS_PROJECT.search(out.stderr) and not expect_fail:
                return "project", first_error(out.stderr)
            return verdict(out.returncode == 0, f"运行退出码 {out.returncode}")
        return verdict(True, "语法通过")

    return "skip", f"脚本不支持语言 {lang or '（未写语言）'}，按正文手动跑"


def main() -> int:
    ap = argparse.ArgumentParser(description="Lathe 交付前试跑")
    ap.add_argument("part")
    ap.add_argument("--run", action="store_true", help="编译后实际运行（rust/python/js）")
    ap.add_argument("--edition", help="Rust edition，默认从教程的 Cargo.toml 代码块推断，找不到用 2021")
    ap.add_argument("--keep", action="store_true", help="保留临时目录")
    args = ap.parse_args()

    part = Path(args.part)
    blocks = [b for b in code_blocks(part.read_text(encoding="utf-8")) if b["type"] in ("runnable", "expected_failure")]
    edition = args.edition or detect_edition(part)
    work = Path(tempfile.mkdtemp(prefix=f"lathe-draft-{part.stem}-"))
    tally = {"pass": 0, "fail": 0, "project": 0, "manual": 0, "skip": 0}
    labels = {"pass": "✅", "fail": "❌", "project": "🧩 需拼工程", "manual": "👣 手动", "skip": "⏭️ 未执行"}
    try:
        for i, b in enumerate(blocks, start=1):
            try:
                status, detail = try_block(b, work, i, edition, args.run)
            except subprocess.TimeoutExpired:
                status, detail = "fail", "编译超时"
            tally[status] += 1
            print(f"{labels[status]} 第 {b['line']} 行 ```{b['info'] or '（未标记）'}：{detail}")
    finally:
        if args.keep:
            print(f"临时目录保留在 {work}")
        else:
            shutil.rmtree(work, ignore_errors=True)

    auto = tally["pass"] + tally["fail"]
    print(
        f"试跑：runnable {tally['pass']}/{auto} 通过"
        f" · 需拼工程 {tally['project']} · 命令块待手动 {tally['manual']} · 未执行 {tally['skip']}"
        f"（edition {edition}{'，已运行' if args.run else '，仅编译'}）"
    )
    return 1 if tally["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
