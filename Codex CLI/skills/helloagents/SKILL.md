---
name: HelloAGENTS
description: 提供 HelloAGENTS 工作流入口与命令/模块导航，并处理 ~auto/~plan/~exec/~help 等指令；当用户输入 /helloagents、$helloagents 或任何 HelloAGENTS ~命令时使用。
---

# HelloAGENTS 技能入口

本技能在以下情况下加载：
- 用户显式调用：`/helloagents` 或 `$helloagents`
- 用户输入 HelloAGENTS 命令：`~auto` / `~plan` / `~exec` / `~help` 等

- 全局硬约束与输出包装（SSOT）：项目根目录 `AGENTS.md`
- 本技能索引（SSOT）：命令索引、references 直链、脚本入口、模板入口

## 显式调用输出（快速入口）

当用户通过 `/helloagents` 或 `$helloagents` 显式激活本技能时：

- 按 `AGENTS.md` 的输出包装渲染
- 状态描述：`技能已激活`
- 中间内容建议（避免一次性列出过多选项）：
  - 直接描述需求（推荐）
  - 常用命令：`~plan`（到方案设计）、`~exec`（执行方案包）、`~help`（完整命令）
- 下一步引导：`输入 ~help 查看所有命令，或直接描述你的需求`

后续输入：按 `AGENTS.md` 的 G4 路由架构处理。

## 命令索引（SSOT）

| 命令 | 类型 | 说明 | 细则 |
|------|------|------|------|
| `~auto` | 需求评估 | 全授权命令（从评估到开发实施） | [references/functions/auto.md](references/functions/auto.md) |
| `~plan` | 需求评估 | 执行到方案设计 | [references/functions/plan.md](references/functions/plan.md) |
| `~exec` | 执行 | 执行方案包任务清单 | [references/functions/exec.md](references/functions/exec.md) |
| `~init` | 工具 | 初始化知识库 | [references/functions/init.md](references/functions/init.md) |
| `~upgrade` | 工具 | 升级知识库 | [references/functions/upgrade.md](references/functions/upgrade.md) |
| `~clean` | 工具 | 清理遗留方案包 | [references/functions/clean.md](references/functions/clean.md) |
| `~commit` | 工具 | Git 提交辅助 | [references/functions/commit.md](references/functions/commit.md) |
| `~test` | 工具 | 运行测试 | [references/functions/test.md](references/functions/test.md) |
| `~review` | 工具 | 代码审查 | [references/functions/review.md](references/functions/review.md) |
| `~validate` | 工具 | 验证知识库/方案包 | [references/functions/validate.md](references/functions/validate.md) |
| `~rollback` | 工具 | 智能回滚 | [references/functions/rollback.md](references/functions/rollback.md) |
| `~help` | 工具 | 显示帮助 | [references/functions/help.md](references/functions/help.md) |

## 阶段索引（SSOT）

- 需求评估： [references/stages/evaluate.md](references/stages/evaluate.md)
- 项目分析： [references/stages/analyze.md](references/stages/analyze.md)
- 方案设计： [references/stages/design.md](references/stages/design.md)
- 开发实施： [references/stages/develop.md](references/stages/develop.md)
- 微调模式： [references/stages/tweak.md](references/stages/tweak.md)

## 规则与服务索引（SSOT）

- 状态管理： [references/rules/state.md](references/rules/state.md)
- 工具/脚本规范： [references/rules/tools.md](references/rules/tools.md)
- 方案包规则： [references/rules/package.md](references/rules/package.md)
- 大型项目扩展： [references/rules/scaling.md](references/rules/scaling.md)
- 知识库服务： [references/services/knowledge.md](references/services/knowledge.md)
- 模板服务： [references/services/templates.md](references/services/templates.md)

---

## 运行与依赖

- **依赖**: Python 3（仅标准库），无需第三方包。
- **路径基准**: `SKILL_ROOT` 指向 `helloagents` 技能根目录（例如 `skills/helloagents/` 或 `{USER_HOME}/{CLI_DIR}/skills/helloagents/`）；本文中的 `references/`、`scripts/`、`assets/` 均以 `SKILL_ROOT/` 为前缀。

## 脚本入口（执行优先）

> 脚本调用规范（路径变量、存在性检查、错误恢复）见 references/rules/tools.md

对确定性操作（创建/迁移/验证方案包、知识库升级等），优先执行 `scripts/` 下脚本；除非需要理解实现细节，不要把脚本全文读入上下文。

脚本位于 `SKILL_ROOT/scripts/` 目录，调用时使用 `-X utf8` 确保编码正确（优先使用 `python3`；如环境仅提供 `python`，可替换命令前缀）：

```text
知识库工具: python3 -X utf8 "{SKILL_ROOT}/scripts/upgradewiki.py" --scan | --init | --backup | --write <plan.json>
方案包验证: python3 -X utf8 "{SKILL_ROOT}/scripts/validate_package.py" [<package-name>]
方案包创建: python3 -X utf8 "{SKILL_ROOT}/scripts/create_package.py" "<feature>" [--type <implementation|overview>]
方案包迁移: python3 -X utf8 "{SKILL_ROOT}/scripts/migrate_package.py" "<package-name>" [--status <completed|skipped>] [--all]
方案包列表: python3 -X utf8 "{SKILL_ROOT}/scripts/list_packages.py" [--format <table|json>]
项目统计: python3 -X utf8 "{SKILL_ROOT}/scripts/project_stats.py" [--path <项目路径>]
```

---

## 模板入口

模板位于 `assets/templates/` 目录，结构与知识库一致：

```text
assets/templates/
  INDEX.md
  context.md
  CHANGELOG.md
  CHANGELOG_{YYYY}.md
  modules/_index.md
  modules/module.md
  plan/proposal.md
  plan/tasks.md
  archive/_index.md
```
