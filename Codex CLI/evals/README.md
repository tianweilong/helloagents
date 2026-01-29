# HelloAGENTS Evals（人工评测用）

本目录用于保存可重复的“输入 → 期望行为”场景，帮助在重构 `AGENTS.md` / `skills/` 后快速验证行为未漂移。

说明：
- 目前不提供内置 runner；这些 JSON 主要用于人工评测（也便于未来接入自动化）。
- 建议使用**新的会话/新的 Agent 实例**进行评测，避免上下文污染。

## 如何使用

1. 打开一个新的会话，确保本仓库目录为当前工作目录。
2. 按 JSON 中的 `query` 输入指令（例如 `/helloagents`、`~plan ...`）。
3. 对照 `expected_behavior` 逐条检查。
4. 如出现偏差：记录“输入/输出/偏差点/期望是什么/建议修复位置（文件路径）”。

## 自动验证（推荐）

> `evals/run.py` 不调用任何 LLM，仅做“可确定的本地事实”校验（schema/链接/脚本返回值等）。
> 对话级行为（例如“回复是否足够简洁/是否真的没扫描目录”）仍需要人工抽样或后续接入 LLM runner 才能端到端验证。

在本目录上级（`Codex CLI/`）任意位置执行：

```bash
python3 -X utf8 evals/run.py
```

常用子集：

```bash
python3 -X utf8 evals/run.py --only schema   # JSON 字段/引用文件存在性
python3 -X utf8 evals/run.py --only lint     # references 内是否还有裸露 references/... 文本
python3 -X utf8 evals/run.py --only docs     # 关键硬约束文本是否存在
python3 -X utf8 evals/run.py --only scripts  # 脚本级 smoke tests（会创建临时目录）
```

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
