# HelloAGENTS Evals（人工评测用）

本目录用于保存可重复的“输入 → 期望行为”场景，帮助在重构 `AGENTS.md` / `skills/` 后快速验证行为未漂移。

说明：
- 提供一个统一的 runner：`evals/run_e2e.py`（既可跑本地确定性校验，也可跑端到端对话评测）。
- 建议使用**新的会话/新的 Agent 实例**进行评测，避免上下文污染。

## 如何使用

1. 打开一个新的会话，确保本仓库目录为当前工作目录。
2. 按 JSON 中的 `query` 输入指令（例如 `/helloagents`、`~plan ...`）。
3. 对照 `expected_behavior` 逐条检查。
4. 如出现偏差：记录“输入/输出/偏差点/期望是什么/建议修复位置（文件路径）”。

## 自动验证（推荐）

`evals/run_e2e.py` 支持两类验证：
- **本地确定性校验（无需模型）**：只验证可确定的本地事实（schema/链接/脚本返回值/关键硬约束文本等）。
- **端到端对话自动化（需要模型）**：会调用 `codex exec` 跑一轮对话，并用第二次 `codex exec --output-schema` 做 judge 自动打分。

在本目录上级（`Codex CLI/`）任意位置执行：

```bash
python3 -X utf8 evals/run_e2e.py --only local
```

常用子集：

```bash
python3 -X utf8 evals/run_e2e.py --only schema   # JSON 字段/引用文件存在性
python3 -X utf8 evals/run_e2e.py --only lint     # references 内是否还有裸露 references/... 文本
python3 -X utf8 evals/run_e2e.py --only docs     # 关键硬约束文本是否存在
python3 -X utf8 evals/run_e2e.py --only scripts  # 脚本级 smoke tests（会创建临时目录）
```

## 端到端对话自动化（需要模型）

`evals/run_e2e.py` 会调用 `codex exec` 真正跑一轮对话，并用第二次 `codex exec --output-schema` 做 judge 自动打分：

```bash
python3 -X utf8 evals/run_e2e.py
```

默认配置：
- model: `gpt-5.2`
- model_reasoning_effort: `medium`
- codex_home: `isolated`（临时 CODEX_HOME，复制本仓库 `skills/` + 你的 `~/.codex/config.toml/auth.json`，避免全局技能漂移）
- exec_mode: `bypass`（使用 `--dangerously-bypass-approvals-and-sandbox`；仅用于 runner 自动复制的临时工作区，确保可写）

可选参数：

```bash
python3 -X utf8 evals/run_e2e.py --pattern 'helloagents-01-*.json'
python3 -X utf8 evals/run_e2e.py --model o3 --judge-model o3-mini
python3 -X utf8 evals/run_e2e.py --reasoning-effort medium
python3 -X utf8 evals/run_e2e.py --timeout 240
python3 -X utf8 evals/run_e2e.py --codex-home system
python3 -X utf8 evals/run_e2e.py --exec-mode sandboxed
python3 -X utf8 evals/run_e2e.py --show-io                 # 打印每个用例的 codex 输入/输出（query/assistant_output/commands）
python3 -X utf8 evals/run_e2e.py --show-io --show-command-output  # 额外打印每条命令的 aggregated_output（更啰嗦）
python3 -X utf8 evals/run_e2e.py --show-codex-cmd --show-stderr   # 打印实际 codex 命令行与 stderr（便于复现/排障）
```

注意：
- 该 runner 需要你本机 `codex` 已可用且已登录（或已配置可用的模型凭据）。
- 这会产生真实模型调用成本；建议在 CI 中只跑关键用例或做定期回归。
- `exec_mode=bypass` 很危险（会跳过 Codex sandbox/审批）。本 runner 会先复制到临时工作区并在结束后清理，但仍建议仅在可信用例/本地环境使用。

## JSON 字段说明

- `skills`：期望被触发/加载的技能列表（该用例的前置条件提示）。
- `query`：评测输入（你要原样输入给 Agent 的指令/话术）。
- `files`：与该用例强相关的文件清单（用于评测时快速对照规则/实现；也便于定位修复位置）。
- `expected_behavior`：期望行为/验收标准清单（逐条核对是否满足；不满足则记录偏差）。

## 评测列表

- `helloagents-01-activate.json`：显式激活入口输出是否简洁、可引导
- `helloagents-02-plan-clarify.json`：需求不完整时是否先追问、且不提前扫描项目
- `helloagents-03-plan-create-package.json`：需求足够时是否创建方案包并输出可执行任务
- `helloagents-04-init-upgrade.json`：KB 初始化/升级是否遵循开关与确认点
- `helloagents-05-exec-safety.json`：执行阶段遇到高风险操作是否触发确认/降级
