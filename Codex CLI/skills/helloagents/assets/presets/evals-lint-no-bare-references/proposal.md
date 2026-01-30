# 变更提案: evals-lint-no-bare-references

## 元信息
```yaml
类型: 新功能
方案类型: implementation
优先级: P1
状态: 草稿
创建: (自动生成)
```

---

## 1. 需求

### 背景
HelloAGENTS 的文档体系（`skills/**/references/` 等）中会出现 `references/...` 形式的路径引用。为避免出现“裸露引用”（不在 fenced code block 中、也不是 Markdown 链接目标），需要一个可重复、可自动化的 lint 检查。

### 目标
- 新增/维护一个 `evals` lint 校验：扫描指定 `references/` 目录下的 Markdown，定位裸露的 `references/...` 文本引用（非代码块内）。
- 对每个命中项输出：文件路径、行号、命中片段，并给出可执行的修复建议。
- 该 lint 校验以 `evals/run_e2e.py --only lint` 为统一入口，作为本地/CI 的快速回归点。

### 约束条件
```yaml
语言/依赖: 仅 Python 标准库
输出: 终端可读（逐条列出问题 + 汇总），退出码可用于 CI（0=通过，1=失败）
忽略规则: fenced code block 内不检测；Markdown 链接目标中的 references/... 不算裸露
```

### 验收标准
- [ ] `python3 -X utf8 evals/run_e2e.py --only lint` 在无问题时退出码为 0
- [ ] 出现问题时：逐条输出 `file:line: snippet`，并给出“如何改成链接/代码块”的建议，退出码为 1
- [ ] `evals/run_e2e.py --only lint` 为 lint SSOT 入口，并在失败时给出清晰定位
- [ ] `evals/README.md` 说明如何运行该检查

---

## 2. 方案

### 技术方案
1. 遍历 `--path` 目录下的 `*.md` 文件。
2. 逐行解析：维护 `in_fence` 状态（遇到以 ``` 开头的行切换）。
3. 在 `in_fence=false` 时用正则匹配 `references/...`：
   - 允许例外：`[text](references/...)` 这种 Markdown 链接目标视为合规。
4. 输出问题清单与汇总，按命中数决定退出码。

### 影响范围
```yaml
涉及模块:
  - Codex CLI/evals/: 新增 lint 脚本与文档说明
  - Codex CLI/evals/run_e2e.py: 可选集成 --only lint
预计变更文件: 2-4
```

### 风险评估
| 风险 | 等级 | 应对 |
|------|------|------|
| 误报（链接/代码块判断错误） | 中 | 增加忽略规则 + self-test 用例 |
| 漏报（复杂 Markdown 结构） | 低 | 先覆盖 80% 常见场景；后续迭代完善 |
