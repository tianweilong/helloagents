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

## 评测列表

- `helloagents-01-activate.json`：显式激活入口输出是否简洁、可引导
- `helloagents-02-plan-clarify.json`：需求不完整时是否先追问、且不提前扫描项目
- `helloagents-03-plan-create-package.json`：需求足够时是否创建方案包并输出可执行任务
- `helloagents-04-init-upgrade.json`：KB 初始化/升级是否遵循开关与确认点
- `helloagents-05-exec-safety.json`：执行阶段遇到高风险操作是否触发确认/降级
