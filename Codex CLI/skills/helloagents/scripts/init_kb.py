#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化 HelloAGENTS 知识库（目录 + 基础文件）

目标：
- 纯标准库、纯文件操作；尽量可重复执行（幂等）
- 默认不覆盖已存在的文件（避免静默覆盖/重建）

Usage:
    python init_kb.py [--path <base-path>] [--force]
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

# 确保能找到同目录下的 utils 模块
sys.path.insert(0, str(Path(__file__).parent))
from utils import ExecutionReport, get_template_loader, get_workspace_path, setup_encoding, validate_base_path


KB_DIRS = ["modules", "archive", "plan"]
KB_FILES = [
    # template_path -> target_relative_path
    ("INDEX.md", "INDEX.md"),
    ("context.md", "context.md"),
    ("CHANGELOG.md", "CHANGELOG.md"),
    ("modules/_index.md", "modules/_index.md"),
    ("archive/_index.md", "archive/_index.md"),
]


def main() -> int:
    setup_encoding()
    parser = argparse.ArgumentParser(description="初始化 HelloAGENTS 知识库（目录 + 基础文件）")
    parser.add_argument("--path", default=None, help="项目根目录（默认: 当前目录）")
    parser.add_argument("--force", action="store_true", help="覆盖已存在文件（危险，不建议）")
    args = parser.parse_args()

    report = ExecutionReport("init_kb")

    # 验证基础路径
    try:
        base = validate_base_path(args.path)
    except ValueError as e:
        report.mark_failed("验证基础路径", ["检查 --path 或切换到项目根目录"], str(e))
        report.print_report()
        return 1

    workspace = get_workspace_path(str(base))
    report.set_context(base_path=str(base), workspace=str(workspace), force=bool(args.force))

    # 目录创建（幂等）
    try:
        workspace.mkdir(parents=True, exist_ok=True)
        report.mark_completed("创建 helloagents/ 目录", str(workspace), "检查目录存在: ls helloagents/")
        for d in KB_DIRS:
            p = workspace / d
            p.mkdir(parents=True, exist_ok=True)
            report.mark_completed(f"创建 helloagents/{d}/ 目录", str(p), f"检查目录存在: ls helloagents/{d}/")
    except Exception as e:
        report.mark_failed(
            "创建知识库目录结构",
            ["创建 helloagents/ 目录", "创建 modules/archive/plan 子目录"],
            str(e),
        )
        report.print_report()
        return 1

    # 文件写入（默认不覆盖）
    loader = get_template_loader()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    replacements = {
        "{project_name}": base.name,
        "{YYYY-MM-DD HH:MM}": now,
        "{数量}": "0",
    }

    for template_path, target_rel in KB_FILES:
        target = workspace / target_rel
        try:
            if target.exists() and not args.force:
                report.mark_completed(f"保留已存在文件 {target_rel}", str(target), "检查文件存在且未被覆盖")
                continue

            content = loader.fill(template_path, replacements)
            if content is None:
                report.mark_failed(
                    f"加载模板 {template_path}",
                    [f"创建 {target_rel}"],
                    f"模板文件不存在: {template_path}",
                )
                report.print_report()
                return 1

            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            report.mark_completed(f"创建/更新文件 {target_rel}", str(target), "检查文件存在且非空")
        except Exception as e:
            report.mark_failed(
                f"写入文件 {target_rel}",
                [f"写入 {target_rel}"],
                str(e),
            )
            report.print_report()
            return 1

    report.mark_success(str(workspace))
    report.print_report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

