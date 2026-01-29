#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HelloAGENTS evals runner（本地自动校验，无外部依赖）

目标：
- 将 evals/*.json 从“纯人工核对”升级为“可重复执行的 smoke checks”
- 不调用任何 LLM / 外部服务；只验证可确定的本地事实（文件/结构/脚本返回值/关键约束文本）

限制：
- 无法端到端验证“模型是否真的按预期回复/是否扫描目录”等对话级行为；
  这类验证需要接入 LLM runner 或人工抽样。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str = ""


def _base_dir() -> Path:
    """Resolve base dir that contains AGENTS.md and skills/ (i.e., the 'Codex CLI' folder)."""
    base = Path(__file__).resolve().parent.parent
    if (base / "AGENTS.md").is_file() and (base / "skills").is_dir():
        return base
    raise SystemExit(f"无法定位工作目录：期望在 {base} 下找到 AGENTS.md 与 skills/。")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _run(cmd: List[str], cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    p = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return p.returncode, p.stdout, p.stderr


def _run_py(script: Path, args: List[str], cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    # Use -X utf8 for stable encoding across platforms.
    cmd = [sys.executable, "-X", "utf8", str(script), *args]
    return _run(cmd, cwd=cwd)


def _load_eval(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SystemExit(f"JSON 解析失败: {path}: {e}")


def _schema_checks(eval_path: Path, data: Dict[str, Any], base: Path) -> List[CheckResult]:
    results: List[CheckResult] = []

    required: Dict[str, Any] = {
        "skills": list,
        "query": str,
        "files": list,
        "expected_behavior": list,
    }
    for k, t in required.items():
        if k not in data:
            results.append(CheckResult(f"{eval_path.name}:{k}", False, "缺少字段"))
            continue
        if not isinstance(data[k], t):
            results.append(CheckResult(f"{eval_path.name}:{k}", False, f"字段类型应为 {t.__name__}"))
            continue
        results.append(CheckResult(f"{eval_path.name}:{k}", True))

    # files exist
    for f in data.get("files", []):
        if not isinstance(f, str):
            results.append(CheckResult(f"{eval_path.name}:files", False, "files 中存在非字符串项"))
            continue
        if not (base / f).exists():
            results.append(CheckResult(f"{eval_path.name}:file:{f}", False, "文件不存在"))
        else:
            results.append(CheckResult(f"{eval_path.name}:file:{f}", True))

    return results


def _check_activate(base: Path) -> List[CheckResult]:
    """helloagents-01-activate.json 的可自动验证子集（入口触发 + 可降级输出）。"""
    results: List[CheckResult] = []

    skill_md = _read_text(base / "skills/helloagents/SKILL.md")
    agents_md = _read_text(base / "AGENTS.md")

    triggers_ok = ("/helloagents" in skill_md) and ("$helloagents" in skill_md)
    results.append(
        CheckResult(
            "activate:skill-triggers",
            triggers_ok,
            "SKILL.md 未包含 /helloagents 或 $helloagents" if not triggers_ok else "",
        )
    )

    downgrade_ok = ("允许**降级输出**" in agents_md) or ("允许降级输出" in agents_md)
    results.append(
        CheckResult(
            "activate:output-downgrade",
            downgrade_ok,
            "AGENTS.md 未声明可降级输出" if not downgrade_ok else "",
        )
    )

    output_rule = base / "skills/helloagents/references/rules/output.md"
    results.append(CheckResult("activate:output-rule-file", output_rule.is_file(), "缺少 output.md" if not output_rule.is_file() else ""))

    output_link_ok = "references/rules/output.md" in skill_md
    results.append(
        CheckResult(
            "activate:skill-links-output-rule",
            output_link_ok,
            "SKILL.md 未索引 output.md" if not output_link_ok else "",
        )
    )

    return results


def _check_plan_clarify(base: Path) -> List[CheckResult]:
    """helloagents-02-plan-clarify.json 的可自动验证子集（EVALUATE 阶段禁止扫描/读代码）。"""
    results: List[CheckResult] = []
    evaluate_md = _read_text(base / "skills/helloagents/references/stages/evaluate.md")

    must_have = [
        "禁止在需求评估阶段扫描用户项目目录或读取用户项目代码文件",
        "禁止在需求评估阶段获取项目上下文",
        "仅基于用户输入进行评估",
    ]
    for s in must_have:
        results.append(CheckResult(f"plan-clarify:evaluate-has:{s}", s in evaluate_md, "缺少硬约束文本" if s not in evaluate_md else ""))

    return results


def _mk_temp_project() -> tempfile.TemporaryDirectory:
    # Keep it outside the repo to avoid leaving untracked files.
    return tempfile.TemporaryDirectory(prefix="helloagents-evals-")


def _check_create_package(base: Path) -> List[CheckResult]:
    """helloagents-03-plan-create-package.json 的可自动验证子集（脚本级 smoke test）。"""
    results: List[CheckResult] = []

    scripts = base / "skills/helloagents/scripts"
    create = scripts / "create_package.py"
    validate = scripts / "validate_package.py"

    with _mk_temp_project() as td:
        proj = Path(td)

        code, out, err = _run_py(create, ["evals-smoke", "--path", str(proj)], cwd=base)
        if code != 0:
            results.append(CheckResult("plan-create-package:create_package", False, f"exit={code}, err={err.strip()}"))
            return results

        try:
            report = json.loads(out)
        except json.JSONDecodeError:
            results.append(CheckResult("plan-create-package:create_package", False, "create_package 输出不是 JSON"))
            return results

        results.append(CheckResult("plan-create-package:create_package", report.get("success") is True, "report.success != true"))

        pkg_path = report.get("context", {}).get("package_path") or report.get("context", {}).get("final_result")
        if not pkg_path:
            results.append(CheckResult("plan-create-package:package_path", False, "report.context.package_path 缺失"))
            return results

        pkg_dir = Path(pkg_path)
        results.append(CheckResult("plan-create-package:proposal.md", (pkg_dir / "proposal.md").is_file(), "proposal.md 不存在"))
        results.append(CheckResult("plan-create-package:tasks.md", (pkg_dir / "tasks.md").is_file(), "tasks.md 不存在"))

        code, out, err = _run_py(validate, ["--path", str(proj)], cwd=base)
        if code != 0:
            results.append(CheckResult("plan-create-package:validate_package", False, f"exit={code}, err={err.strip()}"))
            return results

        try:
            res = json.loads(out)
        except json.JSONDecodeError:
            results.append(CheckResult("plan-create-package:validate_package", False, "validate_package 输出不是 JSON"))
            return results

        results.append(CheckResult("plan-create-package:validate.total>=1", int(res.get("total", 0)) >= 1, f"total={res.get('total')}"))
        results.append(CheckResult("plan-create-package:validate.invalid==0", int(res.get("invalid", 0)) == 0, f"invalid={res.get('invalid')}"))

    return results


def _check_init_upgrade(base: Path) -> List[CheckResult]:
    """helloagents-04-init-upgrade.json 的可自动验证子集（upgradewiki --scan/--init）。"""
    results: List[CheckResult] = []

    upgradewiki = base / "skills/helloagents/scripts/upgradewiki.py"
    with _mk_temp_project() as td:
        proj = Path(td)

        code, out, err = _run_py(upgradewiki, ["--scan", "--path", str(proj)], cwd=base)
        if code != 0:
            results.append(CheckResult("init-upgrade:scan-before", False, f"exit={code}, err={err.strip()}"))
            return results
        before = json.loads(out)
        results.append(CheckResult("init-upgrade:scan-before.exists==false", before.get("exists") is False, f"exists={before.get('exists')}"))

        code, out, err = _run_py(upgradewiki, ["--init", "--path", str(proj)], cwd=base)
        if code != 0:
            results.append(CheckResult("init-upgrade:init", False, f"exit={code}, err={err.strip()}"))
            return results
        init_res = json.loads(out)
        created_or_existed = set(init_res.get("created", [])) | set(init_res.get("existed", []))
        for d in ("modules", "archive", "plan"):
            results.append(CheckResult(f"init-upgrade:init-has:{d}", d in created_or_existed, f"未创建/未识别目录: {d}"))

        code, out, err = _run_py(upgradewiki, ["--scan", "--path", str(proj)], cwd=base)
        if code != 0:
            results.append(CheckResult("init-upgrade:scan-after", False, f"exit={code}, err={err.strip()}"))
            return results
        after = json.loads(out)
        results.append(CheckResult("init-upgrade:scan-after.exists==true", after.get("exists") is True, f"exists={after.get('exists')}"))

        dirs = set(after.get("structure", {}).get("directories", []))
        for d in ("modules", "archive", "plan"):
            results.append(CheckResult(f"init-upgrade:structure-has:{d}", d in dirs, f"structure.directories 缺少 {d}"))

        root_files = after.get("structure", {}).get("root_files", [])
        results.append(CheckResult("init-upgrade:root_files_empty", root_files == [], f"root_files={root_files}"))

    return results


def _check_exec_safety_primitives(base: Path) -> List[CheckResult]:
    """helloagents-05-exec-safety.json 的可自动验证子集（validate_package 可识别不完整方案包）。"""
    results: List[CheckResult] = []

    scripts = base / "skills/helloagents/scripts"
    create = scripts / "create_package.py"
    validate = scripts / "validate_package.py"

    with _mk_temp_project() as td:
        proj = Path(td)

        code, _, err = _run_py(create, ["evals-exec-ok", "--path", str(proj)], cwd=base)
        if code != 0:
            results.append(CheckResult("exec-safety:create_ok", False, f"exit={code}, err={err.strip()}"))
            return results

        bad_dir = proj / "helloagents" / "plan" / "200001010000_incomplete"
        bad_dir.mkdir(parents=True, exist_ok=False)
        (bad_dir / "proposal.md").write_text("# proposal\n", encoding="utf-8")  # tasks.md missing

        code, out, err = _run_py(validate, ["--path", str(proj)], cwd=base)
        results.append(CheckResult("exec-safety:validate_exit_nonzero", code != 0, f"exit={code}, err={err.strip()}"))

        try:
            res = json.loads(out)
        except json.JSONDecodeError:
            results.append(CheckResult("exec-safety:validate_json", False, "validate_package 输出不是 JSON"))
            return results

        results.append(CheckResult("exec-safety:invalid>=1", int(res.get("invalid", 0)) >= 1, f"invalid={res.get('invalid')}"))

    return results


def _lint_no_bare_references(base: Path) -> List[CheckResult]:
    """references/*.md 中非代码块内不应出现裸露的 references/...（应为显式 Markdown 链接）。"""
    root = base / "skills/helloagents/references"
    pat = re.compile(r"references/(functions|stages|rules|services)/[a-z0-9_-]+\.md", re.IGNORECASE)

    bad: List[str] = []
    for p in root.rglob("*.md"):
        text = p.read_text(encoding="utf-8")
        in_fence = False
        for i, line in enumerate(text.splitlines(), start=1):
            s = line.lstrip()
            if s.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for m in pat.finditer(line):
                start, end = m.span()
                before = line[start - 1] if start - 1 >= 0 else ""
                after = line[end : end + 2]
                if before == "[" and after == "](":
                    continue
                bad.append(f"{p.relative_to(base)}:{i}: {m.group(0)}")

    return [
        CheckResult(
            "lint:no-bare-references",
            len(bad) == 0,
            "\n".join(bad[:20]) if bad else "",
        )
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run HelloAGENTS evals (local smoke checks)")
    parser.add_argument(
        "--only",
        choices=["schema", "lint", "docs", "scripts", "all"],
        default="all",
        help="只运行某一类检查",
    )
    args = parser.parse_args()

    base = _base_dir()
    eval_dir = base / "evals"

    checks: List[CheckResult] = []

    if args.only in ("schema", "all"):
        for p in sorted(eval_dir.glob("*.json")):
            checks.extend(_schema_checks(p, _load_eval(p), base))

    if args.only in ("lint", "all"):
        checks.extend(_lint_no_bare_references(base))

    if args.only in ("docs", "all"):
        checks.extend(_check_activate(base))
        checks.extend(_check_plan_clarify(base))

    if args.only in ("scripts", "all"):
        checks.extend(_check_create_package(base))
        checks.extend(_check_init_upgrade(base))
        checks.extend(_check_exec_safety_primitives(base))

    ok = True
    for c in checks:
        if c.ok:
            print(f"PASS {c.name}")
        else:
            ok = False
            detail = f" - {c.detail}" if c.detail else ""
            print(f"FAIL {c.name}{detail}")

    passed = sum(1 for c in checks if c.ok)
    failed = sum(1 for c in checks if not c.ok)
    print(f"\nSUMMARY passed={passed} failed={failed}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

