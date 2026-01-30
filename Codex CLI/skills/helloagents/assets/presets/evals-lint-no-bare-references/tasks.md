# 任务清单: evals-lint-no-bare-references

目录: `helloagents/plan/<package>/`

---

## 任务状态符号说明

| 符号 | 状态 | 说明 |
|------|------|------|
| `[ ]` | pending | 待执行 |
| `[√]` | completed | 已完成 |
| `[X]` | failed | 执行失败 |
| `[-]` | skipped | 已跳过 |
| `[?]` | uncertain | 待确认 |

---

## 执行状态
```yaml
总任务: 6
已完成: 0
完成率: 0%
```

---

## 任务列表

### 1. 新增 lint 脚本（标准库）

- [ ] 1.1 在 `evals/run_e2e.py` 中实现/维护 `--only lint` 的检查逻辑
  - 要求: 仅标准库；输出命中项与汇总；exit code 0/1
  - 验证:
    - `python3 -X utf8 evals/run_e2e.py --only lint`

- [ ] 1.2 实现 fenced code block 识别（``` 切换 in_fence）
  - 验证: 在自造的临时 md 用例中，代码块内的 `references/...` 不应被报出

- [ ] 1.3 实现 Markdown 链接目标豁免（`[x](references/...)` 不算裸露）
  - 验证: 在自造 md 用例中，链接目标不应被报出

### 2. 集成与文档

- [ ] 2.1 确认 `evals/run_e2e.py --only lint` 输出包含清晰定位（文件/行号/命中片段）
  - 验证:
    - `python3 -X utf8 evals/run_e2e.py --only lint`

- [ ] 2.2 更新 `evals/README.md`：补充如何运行 lint/如何解读输出
  - 验证:
    - `rg -n \"--only lint\" evals/README.md`

### 3. 回归验证

- [ ] 3.1 在仓库内挑选 1-2 个代表性 `references/*.md` 做试跑，确认输出可定位
  - 验证:
    - `python3 -X utf8 evals/run_e2e.py --only lint || true`
    - 若有命中：根据建议修复后再跑一次应通过（exit=0）

---

## 执行备注

| 任务 | 状态 | 备注 |
|------|------|------|
