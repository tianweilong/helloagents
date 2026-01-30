# ~exec 命令 - 执行方案包

本模块定义执行方案包命令的执行规则。


## 目录
- 命令说明
- 执行模式适配
- 执行流程
- Overview 类型处理
- 不确定性处理
- 用户选择处理

---

## 命令说明

```yaml
命令: ~exec [<方案包名称>]
类型: 目标选择类
功能: 直接执行 plan/ 目录中的方案包，跳过需求评估和方案设计
模式: STAGE_ENTRY_MODE = DIRECT
```

---

## 执行模式适配

> 规则引用: 按 G4 路由架构及 G5 执行模式规则执行

<mode_adaptation>
~exec 模式适配规则:
1. 本命令使用 DIRECT 入口模式，跳过评估和设计阶段
2. 默认保持 INTERACTIVE 工作流模式
3. 直接从方案包进入开发实施阶段
4. Overview 类型方案包需特殊处理（归档而非执行）
</mode_adaptation>

---

## 执行流程

### 步骤1: 设置状态变量

```yaml
执行内容:
  - STAGE_ENTRY_MODE = DIRECT
  - WORKFLOW_MODE = INTERACTIVE（保持默认）
```

### 步骤2: 扫描方案包

> 脚本路径、存在性检查、错误恢复规则见 [references/rules/tools.md](../rules/tools.md)

**脚本调用:**
- `list_packages.py`（列出候选）
- `validate_package.py --path <项目根目录>`（执行前完整性预检查；用于给出“缺失 proposal.md/tasks.md”的可修复提示）
- （建议）在列出候选时做“只读风险预扫描”（EHRB 关键词/语义信号），用于提前标注风险包，避免误选

<package_scan_analysis>
方案包扫描要点:
1. 扫描 helloagents/plan/ 目录
2. 统计有效方案包数量
3. 根据数量和命令参数决定选择策略
</package_scan_analysis>

```yaml
扫描范围: helloagents/plan/ 目录

判断处理:
  0个方案包: 按 G3 场景内容规则（错误）输出，流程终止
    - 输出中必须明确：执行前需要 `{package}/proposal.md` 与 `{package}/tasks.md`
    - 并给出可修复提示：建议先用 `~plan <需求>` 创建方案包（或直接运行 create_package.py）
    - 并提示后续动作（当执行完成后）：同步知识库（如 `~upgrade`）与归档方案包（如 `migrate_package.py`/`~clean`）
  1个方案包: 自动选择，设置 CURRENT_PACKAGE
  多个方案包:
    - 如命令指定了方案包名称: 匹配并选择
    - 如未指定: 按 G3 场景内容规则（确认）输出，等待用户选择
      - 输出必须包含：候选列表（名称/完整性/任务数/摘要），以及“如何选择”（回复序号或重新运行 `~exec <方案包名称>`）
      - 并建议先运行 `validate_package.py --path <项目根目录>` 做全量完整性校验（或你已在本步自动运行并摘要展示结果）
      - 如候选中存在“不完整/不可执行”的方案包：必须列出缺失项（proposal.md/tasks.md）并给出可复制的修复命令（见步骤3）
      - 候选列表中必须明确说明对 **proposal.md 与 tasks.md** 的检查结果（例如 `proposal.md=OK, tasks.md=missing`），不能只提其中一个文件
      - 即使本轮等待选择、未进入实际执行，也要说明：执行完成后会提供“验收/验证摘要 + 后续动作”（例如建议 `~upgrade` 同步 KB、`migrate_package.py`/`~clean` 归档方案包）
      - 输出末尾必须包含“执行完成后我会提供”的说明（至少包含：验收/验证摘要、KB 同步、方案包归档）
```

### 步骤3: 验证方案包完整性

<package_validation_analysis>
方案包验证要点:
1. 检查 proposal.md 存在性和非空性
2. 检查 tasks.md 存在性和任务项数量
3. 判定方案包是否满足执行条件
</package_validation_analysis>

```yaml
优先脚本验证:
  - validate_package.py ${CURRENT_PACKAGE}

最小必需项:
  - proposal.md（存在且非空）
  - tasks.md（存在且至少1个任务项，overview类型除外）

验证失败: 按 G3 场景内容规则（错误）输出，流程终止
  - 必须列出缺失项（例如 proposal.md/tasks.md）
    - 必须给出可修复提示（包含可复制命令），例如：
    - 重新生成（推荐）：`~plan <需求>` 或 `python3 -X utf8 "{SKILL_ROOT}/scripts/create_package.py" "<feature>" --type implementation --path .`
    - 修复现有包（适合只缺文件）：从 templates 写入再人工补全占位符
      - `cp "{TEMPLATE_DIR}/plan/proposal.md" "helloagents/plan/<package>/proposal.md"`
      - `cp "{TEMPLATE_DIR}/plan/tasks.md" "helloagents/plan/<package>/tasks.md"`
```

### 步骤3.5: 风险预检（EHRB）

> 目的：在真正执行任何不可逆操作前，尽早暴露风险并设置确认点。

```yaml
执行内容:
  - 对候选/选中的方案包的 tasks.md（必要时 proposal.md）做只读扫描
  - 依据 G2 EHRB（关键词检测 + 语义分析）判断是否包含高风险/不可逆操作信号

输出要求:
  - 若发现风险信号：在候选列表/选中包摘要中明确标注“⚠️EHRB 风险”，并说明将如何处理（执行前必须确认；必要时降级为交互确认）
  - 若未发现：说明“未发现明显 EHRB 信号（以实际执行前检查为准）”
```

### 步骤4: 检查方案包类型

<package_type_analysis>
方案包类型判定要点:
1. 读取 proposal.md 内容
2. 识别方案包类型（implementation/overview）
3. 根据类型决定后续处理路径
</package_type_analysis>

```yaml
读取: proposal.md 判断类型

implementation 类型: 继续执行开发实施
overview 类型: 按"Overview 类型处理"规则执行
```

### 步骤5: 开发实施

```yaml
执行规则: 读取并执行 references/stages/develop.md
```

### 步骤6: 流程级验收

```yaml
执行规则: 按 G9 "流程级验收规则" 执行（验收内容详见 G9）

遗留方案包扫描:
  执行规则: 按 G7 "遗留方案包扫描" 执行
  扫描时机: 流程即将结束时
  显示条件: 检测到≥1个遗留方案包
  详细规则: 参考 references/rules/package.md "遗留方案包处理"

完成后: 按 G3 场景内容规则（完成）输出执行命令结果（含验收报告）
执行: 按 G7 状态重置协议执行
```

---

## Overview 类型处理

> 规则引用: 按 [references/rules/package.md](../rules/package.md) "Overview 类型方案包生命周期" 规则执行

```yaml
检测到 overview 类型方案包时:
  按 G3 场景内容规则（确认）输出

  内容要素: 方案包类型说明、操作选项（归档/查看/取消）

  用户选择处理:
    归档: 执行方案包迁移至 archive/
    查看: 显示 proposal.md 内容，再次询问
    取消: 按 G7 状态重置协议执行
```

---

## 不确定性处理

- plan/ 目录不存在 → 按 [G3 场景内容规则](../rules/output.md)（错误）输出，提示无方案包
- 方案包验证失败 → 输出具体缺失项，建议修复或重新规划
- 方案包类型无法识别 → 默认按 implementation 类型处理

---

## 用户选择处理

> 本章节定义 ~exec 命令需要用户确认的场景，供 G3 输出格式统一提取。

### 场景: 方案包选择（多个方案包）

```yaml
内容要素:
  - 方案包列表: plan/ 目录下的方案包清单（名称、创建时间、类型）
  - 方案包摘要: 每个方案包的简要描述

选项:
  选择方案包N: 选择对应序号的方案包执行
  取消: 按 G7 状态重置协议执行
```

### 场景: Overview类型方案包处理

> 规则引用: 按 [references/rules/package.md](../rules/package.md) "用户选择处理 - Overview类型方案包处理" 执行

### 场景: 流程级验收完成

```yaml
内容要素:
  - 验收状态: 通过/部分通过/失败
  - 交付物摘要: 方案包、代码变更、知识库状态
  - 需求符合性: 已完成任务/未完成任务
  - 问题汇总: 警告和信息性记录（如有）
  - 后续动作: 建议同步知识库（如 `~upgrade`）、归档方案包（如 `migrate_package.py`/`~clean`）、必要时 `~validate`

输出格式: 按 G3 场景内容规则（完成）输出
```
