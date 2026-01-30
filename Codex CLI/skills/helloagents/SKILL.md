---
name: HelloAGENTS
description: 提供 HelloAGENTS 工作流入口与命令/模块导航，并处理 ~auto/~plan/~exec/~help 等指令；当用户输入 /helloagents、$helloagents 或任何 HelloAGENTS ~命令时使用。
---

# HelloAGENTS 技能入口

本技能在以下情况下加载：
- 用户显式调用：`/helloagents` 或 `$helloagents`
- 用户输入 HelloAGENTS 命令：`~auto` / `~plan` / `~exec` / `~help` 等

- 全局硬约束与最小输出包装（SSOT）：项目根目录 `AGENTS.md`
- 本技能索引（SSOT）：命令索引、references 直链、脚本入口、模板入口

## 显式调用输出（快速入口）

当用户通过 `/helloagents` 或 `$helloagents` 显式激活本技能时：

- 默认按 `AGENTS.md` 的输出包装渲染（用户要求短答/外部工具原样输出时允许降级）
- 状态描述：`技能已激活`
- 约束（CRITICAL）：**只做入口引导输出**，不运行任何 Shell 命令、不扫描目录、不读取任何文件（包括 `AGENTS.md`/`skills/`/项目代码）
- 中间内容建议（避免一次性列出过多选项；**总计 1-3 个下一步**）：
  - 直接描述需求（推荐，默认提供）
  - `~plan <需求描述>`：生成可执行的方案包（默认最多提供 1 条命令提示）
  - `~help`：仅当用户明确表示“想看全部命令/不知道怎么用”时再提示
- 中间内容必须包含 1 句“降级输出”说明：当用户随后要求“只要结论/短答/不要模板”时，允许降级输出（不使用完整包装）
- 约束：**不要**在激活输出里一次性列出多条命令（尤其不要把整张命令表倾倒出来）
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

## 快速处理：`~plan`（无参数）

当用户仅输入 `~plan`（未提供任何需求描述）时：

- **直接输出追问**（≤5 个问题）+ 风险说明；不进入方案设计/不创建方案包。
- **禁止行为（CRITICAL）**：不运行任何 Shell 命令、不读取任何文件、不扫描目录（本阶段只能基于用户输入追问）。
- **必须说明后续流转**：用户补充后，你将重新评分 → 判定复杂度 → 在 AUTO_PLAN 下生成 implementation 方案包，并给出“如何验证/如何执行”。

输出要点（示例，措辞可调整但结构保持）：
```text
【HelloAGENTS】- 需求评估：~plan - 追问中

（一句话说明：你只输入了 ~plan，缺少需求描述，无法进入方案设计）

（≤5 个关键追问）
1) ...

（风险说明：缺失会导致方案高度不确定/不推荐继续）

────
下一步: 回复以上问题；我会重新评分/判定复杂度，并生成方案包（含验证/执行命令）。
```

## 阶段索引（SSOT）

- 需求评估： [references/stages/evaluate.md](references/stages/evaluate.md)
- 项目分析： [references/stages/analyze.md](references/stages/analyze.md)
- 方案设计： [references/stages/design.md](references/stages/design.md)
- 开发实施： [references/stages/develop.md](references/stages/develop.md)
- 微调模式： [references/stages/tweak.md](references/stages/tweak.md)

## 规则与服务索引（SSOT）

- 状态管理： [references/rules/state.md](references/rules/state.md)
- 工具/脚本规范： [references/rules/tools.md](references/rules/tools.md)
- 输出与包装： [references/rules/output.md](references/rules/output.md)
- 方案包规则： [references/rules/package.md](references/rules/package.md)
- 大型项目扩展： [references/rules/scaling.md](references/rules/scaling.md)
- 知识库服务： [references/services/knowledge.md](references/services/knowledge.md)
- 模板服务： [references/services/templates.md](references/services/templates.md)

---

## 阅读策略（避免嵌套引用）

- 尽量从本 `SKILL.md` 的索引直接打开 `references/**` 文件；references 内的交叉链接仅作提示，避免多跳导致只读到局部内容。

## 运行与依赖

- **依赖**: Python 3（仅标准库），无需第三方包。
- **路径基准**: `SKILL_ROOT` = 当前 Skill 所在目录的**绝对路径**（即包含本 `SKILL.md` 的目录）。不要假设 `skills/helloagents/` 这样的相对路径一定存在；避免在运行时通过 Shell 探测/切换 CWD 版本（尤其在 EVALUATE 阶段会被视为“扫描目录”）。

## 脚本入口（执行优先）

> 脚本调用规范（路径变量、存在性检查、错误恢复）见 references/rules/tools.md

对确定性操作（创建/迁移/验证方案包、知识库升级等），优先执行 `scripts/` 下脚本；除非需要理解实现细节，不要把脚本全文读入上下文。

脚本位于 `SKILL_ROOT/scripts/` 目录，调用时使用 `-X utf8` 确保编码正确（优先使用 `python3`；如环境仅提供 `python`，可替换命令前缀）：

```text
知识库工具: python3 -X utf8 "{SKILL_ROOT}/scripts/upgradewiki.py" --scan | --init | --backup | --write <plan.json>
知识库初始化: python3 -X utf8 "{SKILL_ROOT}/scripts/init_kb.py" [--path <项目路径>]
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
