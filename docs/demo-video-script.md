# Demo Video Script — PennyGuard（作业 327885）

- **学生**：Yiyang BU（卜毅扬），学号 **60392800**，Group 43（单人 solo）
- **成品要求**：**一个** `.mp4`，**时长 ≤ 10 分钟**。三块内容必须都讲到（讨论帖 646809）：
  1. 产品演示 + **前后行为对比**；
  2. **原创软件工程思路**（单纯"记账"这个业务需求不算）；
  3. **可追溯性 + agent 治理与人工监督**。
- **保密规则**：画面和讲解里都不要出现、不要念出任何 API key、端点密钥或 `.env` 内容；镜头里只走离线默认路径；真实大模型 live 路径口头描述即可，不需要在镜头前调用。

## 这份稿子怎么看（先读这一节）

每一段都分成四块，格式固定：

- **【操作】**：中文写的鼠标、键盘动作——点哪里、打开哪个文件、终端敲什么命令。照做就行。
- **【英文讲稿】**：引用块（`>` 开头）里的英文，是你对着镜头**直接念**的台词。
- **【中文意思】**：紧跟在英文讲稿下面，是这句英文的中文释义，帮你理解自己在念什么；**录的时候仍然念上面的英文**，不用念中文。
- **【提示】**：中文备注，告诉你鼠标/手指要指到屏幕上的哪个位置、哪句话是重点。

> 命令代码块（```powershell）里的内容在终端原样敲；英文讲稿照念；其余中文都是给你自己看的操作说明。

---

## 一、录前准备（开录前 10 分钟做完）

### 1. 打开项目文件夹
1. 启动 **VS Code**。
2. 左上角菜单 `File → Open Folder`，选择这个文件夹：
   ```
   C:\Users\26424\Desktop\软件工程 周一\pennyguard
   ```
3. 打开底部终端：顶部菜单 `Terminal → New Terminal`，或按 `` Ctrl + ` ``（反引号，Tab 键上方那个键）。
4. 看终端最前面的路径，确认停在 `...\pennyguard`；提示符最好带 `(.venv)`。

### 2. 清空旧账本（让演示从空数据开始）
在底部终端粘贴下面这行，回车：
```powershell
Remove-Item -Recurse -Force .pennyguard -ErrorAction SilentlyContinue
```

### 3. 先跑一遍测试，确认全绿
在终端粘贴，回车：
```powershell
$env:PYTHONPATH = "src"
.venv\Scripts\python.exe -m pytest test/offline/ -v
```
结尾要看到这一行横幅：
```
============================= 37 passed in 4.xxs ==============================
```
如果只看到一排绿点、没看到这行字，再敲 `echo $LASTEXITCODE`，显示 `0` 就代表通过。

### 4. 确认屏幕上没有密钥
终端敲下面这句，回车，结果应该是**空白**：
```powershell
echo $env:LLM_API_KEY
```
录制全程不要设置、不要展示任何 key。

### 5. 提前把要讲的文件在标签栏打开
在左侧资源管理器里，按下面顺序点开，录的时候直接切标签，不用现场找：
- `README.md`
- `src/pennyguard/guardrail.py`、`src/pennyguard/budget.py`
- `docs/architecture/invariants.md`
- `test/offline/test_guardrail.py`、`test/offline/test_budget.py`
- `docs/architecture/adr/001-guarded-hybrid-classifier.md`
- `docs/architecture/evaluation-table.md`
- `src/pennyguard/prompt.py`
- `docs/architecture/runtime-policy-catalog.md`
- `docs/req/requirements.yaml`
- `docs/architecture/trace-matrix.md`
- `AGENTS.md`、`Prompt.md`
- `docs/ai-use-log.yaml`、`docs/review-memo.md`、`docs/bug-diary.md`
- `transcripts/60392800-YiyangBU.md`
- `.opencode/permissions.jsonc`
- `.github/workflows/ci.yml`、`scripts/` 文件夹
- `docs/debt-register.md`、`docs/architecture/risk-list.md`

### 6. 环境收尾
- 关掉微信、邮件、系统通知，避免弹窗录进视频；
- 确认麦克风能用（录屏时要开录音）；
- 把编辑器和终端字号调大一点，让评委能看清命令和代码。

## 二、录屏工具操作（Windows 自带 Xbox Game Bar，不用装软件）

1. 鼠标先点一下 **VS Code 窗口**，让它在最前面。
2. 按 **`Win + G`**，屏幕上会弹出游戏栏小组件（带一个圆点录制按钮）。
3. 在小组件上点**麦克风图标**，允许录音；不开就只有画面、没有你的声音。
4. 开始录制：按 **`Win + Alt + R`**（或点那个圆点）。
5. 停止录制：再按一次 **`Win + Alt + R`**。
6. 录好的 `.mp4` 自动存在：
   ```
   C:\Users\26424\Videos\Captures
   ```

**注意两点：**
- Game Bar 只能录**当前这个应用窗口**，录不到桌面和文件资源管理器，所以所有操作都在 VS Code 里完成（终端 + 编辑器标签切换），不要切到别的窗口。
- 如果提示"无法录制此窗口"，再装免费的 OBS Studio 录全屏；需要的话再单独要 OBS 分步设置。
- 建议先试录 1 分钟回放，确认画面清楚、声音正常、终端文字看得清，再正式录。

## 三、时间分配（总时长控制在 9 分半以内，留 30 秒余量）

| 段落 | 时间 | 对应必含块 |
|---|---|---|
| 0. 开场报身份 | 0:00–0:40 | 准备 |
| 1. 产品演示：离线正常流程 | 0:40–2:30 | 块 1 |
| 2. 前后对比：安全边界起作用 | 2:30–4:00 | 块 1 |
| 3. 原创软件工程思路 | 4:00–6:10 | 块 2 |
| 4. 可追溯性：需求 → 组件 → 测试 → 监控 | 6:10–7:40 | 块 3 |
| 5. agent 治理与人工监督 | 7:40–9:00 | 块 3 |
| 6. 债务、风险、收尾 | 9:00–9:30 | 收尾 |

---

## 第 0 段｜开场报身份（0:00–0:40）

**【操作】**
- 鼠标点左侧资源管理器里的 `README.md`，让它显示在编辑区；
- 滚动到文件最开头，露出标题和作者/学号/组别那几行。

**【英文讲稿】**
> "Hello, this is Yiyang BU, student ID 60392800, Group 43, solo submission for CS5351. The project is PennyGuard: a local command-line expense tool that uses an AI component to suggest a budget category, while deterministic code constrains every AI output. It was built from scratch; no code, naming, or document was reused from any prior group repository."

**【中文意思】**：大家好，我是 Yiyang BU，学号 60392800，第 43 组，CS5351 的单人提交。项目叫 PennyGuard，是一个本地命令行记账工具：用 AI 组件来建议预算类目，但由确定性代码约束 AI 的每一处输出。它是从零搭建的，没有复用之前任何小组仓库里的代码、命名或文档。

**【提示】**
- 鼠标点到 README 头部的作者、学号、组别行；
- 再点到"咨询层 / 权威层"那段概述。

## 第 1 段｜产品演示：离线正常流程（0:40–2:30）

**【操作】**
- 鼠标点底部终端面板，让光标停在终端里；
- 逐条粘贴下面命令，每敲一条按一次回车：
  ```powershell
  $env:PYTHONPATH = "src"
  .venv\Scripts\python.exe -m pennyguard.app add --description "Coffee and toast" --amount 12.50 --date 2026-11-23
  .venv\Scripts\python.exe -m pennyguard.app add --description "MTR ticket" --amount 6.00 --date 2026-11-23
  .venv\Scripts\python.exe -m pennyguard.app add --description "AMZN MKTPL ORDER" --amount 39.90 --date 2026-11-23
  .venv\Scripts\python.exe -m pennyguard.app list
  .venv\Scripts\python.exe -m pennyguard.app status
  .venv\Scripts\python.exe -m pennyguard.app eval
  ```

**【英文讲稿】**
> "The default path runs fully offline. With no API key configured, the system selects the deterministic rule-based fallback and constructs no LLM client. Each record shows its category, its provenance source, and the guardrail reason code. The `status` command accumulates spending per category using exact decimal arithmetic. The `eval` command replays the fixed ten-fixture set and reports faithfulness, relevance, and a zero safety-escape count."

**【中文意思】**：默认路径完全离线运行。在没有配置 API key 的情况下，系统会选用确定性的规则兜底方案，不创建任何大模型客户端。每条记录都会显示它的类目、来源出处和护栏原因码。`status` 命令用精确的十进制运算按类目汇总支出。`eval` 命令会重跑固定的十条测试用例，报告忠实度、相关性，以及安全逃逸次数为零。

**【提示】**
- 指每条 `add` 输出里的 `[rule]` 来源标签和 `(OK)` 原因码；
- 指 `status` 里的 within_budget 行；
- 指 `eval` 结果里的 `safety_escape_count: 0`。

## 第 2 段｜前后对比：安全边界如何起作用（2:30–4:00）

**【操作】**
- 左侧点开 `src/pennyguard/guardrail.py`；
- 在标签上点右键 → `Split Right`（向右拆分），再在右边打开 `docs/architecture/invariants.md`，两个文件并排；
- 之后再切到 `test/offline/test_guardrail.py` 和 `test/offline/test_budget.py`。

**【英文讲稿 · 改之前（无护栏会怎样）】**
> "Without a deterministic boundary, an advisory model could return a category outside the intended list, propose a different amount, or mark an over-budget record as compliant. Those are exactly the failures this project blocks."

**【中文意思】**：如果没有这道确定性边界，一个只负责建议的模型可能返回清单之外的类目、提出不同的金额，或者把超预算的记录标记为合规。这些正是本项目要拦住的错误。

**【英文讲稿 · 改之后（护栏混合体怎么做）】**
> "PennyGuard splits an advisory layer from an authority layer. The model-facing categorizer produces a candidate only. The deterministic guardrail runs four checks: structural validation, whitelist closure, amount conservation, and then the budget policy alone decides compliance. An out-of-whitelist label is rejected and replaced with the reserved `other`; any model-supplied amount is discarded and the input amount is kept; a model compliance signal cannot flip an over-budget flag."

**【中文意思】**：PennyGuard 把"建议层"和"权威层"分开。面向模型的分类器只产出一个候选结果。确定性护栏执行四道检查：结构校验、白名单闭合、金额守恒，之后由预算策略独自判定是否合规。白名单之外的标签会被拒绝，并替换成保留类目 `other`；模型给出的任何金额都会被丢弃，保留原始输入金额；模型的合规信号不能翻转超预算标记。

**【提示】**
- 在 `guardrail.py` 里指到 `validate_candidate`，以及原因码 `NOT_IN_WHITELIST`、`MALFORMED_RESPONSE`、`AMOUNT_OVERRIDE_IGNORED`；
- 指金额守恒检查：记录金额等于输入金额；
- 在 `budget.py` 里指 `BudgetPolicy.evaluate`：合规状态由它独自决定，模型侧包没有写预算的接口；
- 打开两个测试文件，点名负面测试：白名单外拒绝、金额守恒、畸形响应降级、合规覆盖拒绝。

## 第 3 段｜原创软件工程思路（4:00–6:10）

**【操作】**
- 依次切标签：`adr/001-guarded-hybrid-classifier.md` → `evaluation-table.md` → `prompt.py` → `runtime-policy-catalog.md`。

**【英文讲稿】**
> "The business need — sorting expenses — is not the contribution. The engineering contribution is how the AI component is constrained and made maintainable and auditable."

**【中文意思】**：业务需求本身——给支出分类——并不是我们的贡献；工程上的贡献在于：如何约束这个 AI 组件，并让它可维护、可审计。

> "First, an advisory/authority split with a closed API surface. The `Categorizer` interface is the only contract the app uses; both the rule-based and LLM implementations conform to it. The model-facing package cannot import budget-mutating or ledger-mutating APIs; a structural test enumerates its exported names and confirms no write, delete, shell, or tool-call method exists."

**【中文意思】**：第一，建议层与权威层分离，并收紧对外接口。`Categorizer` 接口是应用唯一依赖的契约，规则实现和大模型实现都遵循它。面向模型的包不能导入修改预算或账本的接口；一个结构测试会枚举它对外暴露的名字，确认不存在任何写入、删除、Shell 或工具调用方法。

> "Second, a weighted architecture selection. Five candidates were scored against six drivers weighted by course priorities: safety boundary 0.25, offline determinism 0.20, genuine AI 0.15, cost and latency 0.15, maintainability 0.12, traceability 0.13. The guarded hybrid scored 4.55; model-direct write scored 2.30 and fails the boundary; rules-only scores 4.10 but lacks the AI component."

**【中文意思】**：第二，加权的架构选型。五个候选方案按六个驱动因素打分，权重按课程优先级设定：安全边界 0.25、离线确定性 0.20、真实 AI 成分 0.15、成本与延迟 0.15、可维护性 0.12、可追溯性 0.13。护栏混合体得分 4.55；模型直接写入得 2.30，且过不了安全边界；纯规则方案得 4.10，但缺少 AI 组件。

> "Third, a bounded, layered prompt assembly. The context is split into identity, standing constraints, whitelist knowledge, history, resumable state, and current task. The pipeline runs dedup, prioritize, budget, compact, assemble, and validate, under a 600-unit cap with a 480-unit compaction threshold. Constraints and the whitelist are exempt from truncation and re-injected verbatim after compaction; the LLM call has an 8-second hard timeout."

**【中文意思】**：第三，有上限、分层的提示词装配。上下文被分成身份、常驻约束、白名单知识、历史记录、可恢复状态和当前任务几个部分。流水线依次执行去重、优先级排序、额度控制、压缩、装配、校验，上限 600 个单位，压缩阈值 480。约束和白名单不参与截断，压缩后逐字重新注入；大模型调用有 8 秒硬性超时。

> "Fourth, a deterministic runtime policy catalog. Fourteen degraded paths each have a concrete action: no key, timeout, transport error, malformed payload, out-of-whitelist label, ignored model amount, missing or corrupt ledger, missing budget, over-budget prompt, empty eval set, unknown CLI command, boundary violation, and secret redaction. Fallbacks are observable through stable reason codes."

**【中文意思】**：第四，确定性的运行时策略目录。十四条降级路径各自有明确的处理动作：无 key、超时、传输错误、畸形载荷、白名单外标签、被忽略的模型金额、账本缺失或损坏、预算缺失、超预算提示、空评估集、未知命令、边界违规，以及密钥脱敏。兜底行为都通过稳定的原因码可观测。

**【提示】**
- 在评估表里指打分：护栏混合体 4.55；
- 在 `prompt.py` 里指常驻约束 `_STANDING_CONSTRAINTS` 和装配阶段；
- 在策略目录里指 RP-01 到 RP-14 各行。

## 第 4 段｜可追溯性：需求 → 组件 → 测试 → 监控（6:10–7:40）

**【操作】**
- 依次切标签：`docs/req/requirements.yaml` → `docs/architecture/trace-matrix.md` → `docs/architecture/invariants.md`；
- 可选：在终端快速跑一次测试：
  ```powershell
  .venv\Scripts\python.exe -m pytest test/offline/ -v
  ```

**【英文讲稿】**
> "Every requirement is machine-readable and maps to an enforcing component, a test or evidence artifact, and a runtime monitor. The registry has 25 requirements across seven types: functional, invariant, quality, performance, cost, governance, and security. Six are zero-tolerance invariants, each with a test that fails when the invariant is violated."

**【中文意思】**：每条需求都是机器可读的，并对应到一个执行它的组件、一个测试或证据产物，以及一个运行时监控。需求登记表共 25 条，分七类：功能、不变量、质量、性能、成本、治理、安全。其中六条是零容忍不变量，每条都配有一个在不变量被违反时会失败的测试。

> "Here are three chains. First, INV-001, closed whitelist: `guardrail.py`, the test `test_out_of_whitelist_rejected`, and the monitor reason `NOT_IN_WHITELIST`. Second, INV-003, deterministic compliance: `budget.py`, the test `test_ai_cannot_flip_compliance`, and the monitor `compliance_override_rejected`. Third, SEC-001, secret non-persistence: `config.py`, `ledger.py` and the redaction routine, the test `test_secret_not_persisted_or_leaked`, and the monitor `secret_redacted`."

**【中文意思】**：这里走三条追溯链。第一，INV-001 白名单闭合：`guardrail.py`，测试 `test_out_of_whitelist_rejected`，监控原因 `NOT_IN_WHITELIST`。第二，INV-003 合规确定性：`budget.py`，测试 `test_ai_cannot_flip_compliance`，监控 `compliance_override_rejected`。第三，SEC-001 密钥不落盘：`config.py`、`ledger.py` 及脱敏例程，测试 `test_secret_not_persisted_or_leaked`，监控 `secret_redacted`。

**【提示】**
- 指 trace-matrix 表里的行；指模块头部引用的需求/不变量编号；
- 展示 25 条需求、6 条不变量、37 个离线测试；强调每条不变量都配了一个"被违反时会失败"的测试。

## 第 5 段｜agent 治理与人工监督（7:40–9:00）

这一段按 **5.1 → 5.8** 的顺序走，**每一小步先切到对应文件标签，再念那一句英文**。不要一口气把八个标签全点开，讲到哪个切哪个。

### 5.1 agent 的定位与入口（先切 `AGENTS.md`）

**【操作】**
- 鼠标在左侧资源管理器点 `AGENTS.md`，编辑区停在文件最开头的标题行；
- 向下滚动到第 4 节 `Read / modify / freeze scope`，停在 `Frozen` 那一小段。

**【英文讲稿】**
> "The coding agent is a supervised assistant, not an unattended author. `AGENTS.md` is its single entry point."

**【中文意思】**：写代码的 agent 是受监督的助手，不是无人看管的作者。`AGENTS.md` 是它唯一的入口文件。

**【提示】**
- 指标题里的 "single entry point"；
- 指 `Frozen` 小节里列出的护栏、预算策略、权限和规则文件。

### 5.2 计划门禁（切到 `Prompt.md`）

**【操作】**
- 点标签切到 `Prompt.md`；
- 指 `Step 1 — Produce an execution plan (stop here for approval)` 这一行；
- 再快速扫一眼 `Step 2`、`Step 3`、`Step 4` 里的 human gate，以及底部 `Hard stop conditions`。

**【英文讲稿】**
> "`Prompt.md` instructs it to produce a plan and stop for human approval before any code."

**【中文意思】**：`Prompt.md` 要求它先拿出一份方案，在写任何代码之前先停下来，等人工批准。

**【提示】**
- 指正文里的 "stop" 和 "Wait for the human to approve" 字样；
- 强调：没批准之前不写源码。

### 5.3 权限模型与冻结路径（切到 `.opencode/permissions.jsonc`）

**【操作】**
- 点标签切到 `.opencode/permissions.jsonc`；
- 指顶部 `"default": { "read": false, "write": false }`；
- 指 `roles` 下面 plan / coding / verification 三个角色各自的读写白名单；
- 指 `frozen_paths` 列表。

**【英文讲稿】**
> "The permission model defaults to no read and no write; every allowed path is an explicit whitelist. Guardrail, budget policy, and permission and rules files are frozen paths that need an ADR and human approval to change."

**【中文意思】**：权限模型默认不可读、不可写，所有放行路径都是显式写进白名单的。护栏、预算策略以及权限和规则文件属于冻结路径，要改动必须有一份 ADR 并经过人工批准。

**【提示】**
- 指 `GR-01`（不在白名单内的路径一律拒绝）和 `GR-02`（冻结路径任何 agent 角色都不能写）。

### 5.4 六道 CI 阻断门禁（切到 `.github/workflows/ci.yml`，再展开 `scripts/`）

**【操作】**
- 点标签切到 `.github/workflows/ci.yml`，从上往下依次指六个 `Gate` 名称；
- 然后在左侧展开 `scripts/` 文件夹，点一下里面的五个门禁脚本，让评委看到脚本实体。

**【英文讲稿】**
> "Six CI blocking gates: test approval, static analysis, schema, semantic evaluation, regression, and AI-use log freshness."

**【中文意思】**：有六道 CI 阻断门禁：测试批准配对、静态分析（编译/依赖/边界）、需求结构规范、语义评估回放、回归测试，以及 AI 使用日志新鲜度。

**【提示】** 六个 Gate 对应关系，念的时候可以对一下：
- Gate 1 — Test approval pairing check（测试批准配对）
- Gate 2 — Static analysis（静态分析 + 边界检查）
- Gate 3 — Requirements schema validation（结构规范）
- Gate 4 — Semantic evaluation replay（语义评估）
- Gate 5 — Regression suite（回归测试）
- Gate 6 — AI-use log freshness（日志新鲜度）

### 5.5 AI 使用日志（切到 `docs/ai-use-log.yaml`）

**【操作】**
- 点标签切到 `docs/ai-use-log.yaml`；
- 随便指一条 `AU-` 条目，展开看里面的 `files_touched`、`intervention`、`decision` 三个字段。

**【英文讲稿】**
> "An AI-use log: every code or prompt change appends an entry; a change touching `src/` or `prompts/` without a log update is blocked."

**【中文意思】**：每次改代码或提示词都要在日志里追加一条记录；如果改动触及 `src/` 或 `prompts/` 却没更新日志，门禁会把它拦下。

**【提示】** 这里正好对应 5.4 里的 Gate 6。

### 5.6 标注会话记录（切到 `transcripts/60392800-YiyangBU.md`）

**【操作】**
- 点标签切到 `transcripts/60392800-YiyangBU.md`；
- 先指顶部的标注图例：`APPROVED` / `REDIRECTED` / `REJECTED` / `INTERRUPTED` / `QUESTIONED`；
- 再滚到下面的六阶段表格，逐行指阶段名称。

**【英文讲稿】**
> "An annotated transcript across six stages: requirements classification, architecture candidate generation and evaluation, pre-code plan approval, build, verification compliance, and revision on test evidence, marked with APPROVED, REDIRECTED, REJECTED, INTERRUPTED, and QUESTIONED."

**【中文意思】**：一份跨六个阶段的标注会话记录：需求分类、架构候选生成与评估、写码前方案批准、构建、验证合规、按测试证据修订；每条都标了 APPROVED（批准）、REDIRECTED（改向）、REJECTED（拒绝）、INTERRUPTED（打断）、QUESTIONED（存疑）。

**【提示】** 六阶段顺序：需求分类 → 架构候选评估 → 写码前批准 → 构建 → 验证合规 → 按证据修订。

### 5.7 评审 memo（切到 `docs/review-memo.md`，一句带过）

**【操作】**
- 点标签切到 `docs/review-memo.md`；
- 指 `MEMO-001` 和 `MEMO-002` 末尾的 `Verdict: APPROVE`。

**【中文意思】**：每一轮改动都有一份评审 memo，记录规格对齐、架构对齐、代码与测试质量、安全和效率，最后给出 APPROVE / CHANGES REQUIRED / REJECT 裁决；本项目两份 memo 都是 APPROVE。

**【提示】** 这一步不用展开长讲，让评委看到有逐轮评审记录即可。

### 5.8 人工抓到的问题（切到 `docs/bug-diary.md`）

**【操作】**
- 点标签切到 `docs/bug-diary.md`（如果某个缺陷在 transcript 里讲过，也可以切回 transcript 对应条目）；
- 逐条指六个缺陷记录。

**【英文讲稿】**
> "Finally, here are issues the human caught that the agent did not flag on its own: a plain-scalar colon that broke YAML parsing; an integer/string schema mismatch; an unmatched bracket visible only at collection; native exceptions bypassing the degradation contract; the CLI `SystemExit` contract; and a lexicon synonym gap that was fixed in the fallback table rather than by relaxing the whitelist."

**【中文意思】**：最后，这些是人工发现、agent 自己没有标出的问题：纯标量里的冒号导致 YAML 解析失败；整数与字符串的模式不匹配；只有在收集阶段才暴露的括号不配对；原生异常绕过了降级契约；CLI 的 `SystemExit` 契约；以及一处词典同义词缺口——最终是在兜底表里修复，而不是放宽白名单。

**【提示】**
- 讲清两类 AI 不要混淆：写代码的 coding agent（被监督、被记录）≠ 产品里那个可选的运行时 LLM（被护栏约束）；
- 指 transcript 里的介入标注和这六类人工抓到的问题。

## 第 6 段｜债务、风险、收尾（9:00–9:30）

**【操作】**
- 切到 `docs/debt-register.md`，再切 `docs/architecture/risk-list.md`。

**【英文讲稿】**
> "Known gaps are tracked, not hidden: a small evaluation corpus, prompt rot, frozen-code maintainability, hidden provider dependencies, and solo-author cognitive debt. Each has a mitigation and a review trigger. Future work is to expand the evaluation corpus, add a provider adapter test behind the live seam, and revisit retrieval-augmented categorization only if the label space grows. Thank you."

**【中文意思】**：已知缺口都被记录在案、没有隐瞒：评估语料偏小、提示词腐化、冻结代码的可维护性、隐藏的提供方依赖，以及单人作者的认知负担。每条都有缓解措施和复核触发条件。未来工作包括扩充评估语料、在 live 接缝后补一个提供方适配器测试，并且只有在类目空间扩大时才重新考虑检索增强分类。谢谢大家。

**【提示】**
- 结尾可指一下 README 里复现离线测试、live 测试和全套测试的命令，以及仓库链接（账号 `jack2004-1`）。

---

## 录完自查清单（中文核对）

- [ ] 是**一个** `.mp4`，**总时长 < 10 分钟**；
- [ ] 开场报了姓名、学号、组别、单人提交；
- [ ] 三块必含都讲到：前后对比、原创 SE 思路、可追溯性 + 治理监督；
- [ ] 画面里没有任何密钥 / `.env`；
- [ ] 声音清楚，命令、代码、表格能看清；
- [ ] 结尾测试横幅是 `37 passed`。

## 证据对照表（给评委看每块对应仓库哪里）

| 必含块 | 仓库对应位置 |
|---|---|
| 产品演示 + 前后对比 | `src/pennyguard/app.py`、`guardrail.py`、`budget.py`、`test/offline/test_guardrail.py`、`test/offline/test_budget.py` |
| 原创 SE 思路 | `adr/001-guarded-hybrid-classifier.md`、`evaluation-table.md`、`prompt.py`、`runtime-policy-catalog.md`、`permission-model.md` |
| 可追溯性 | `requirements.yaml`、`trace-matrix.md`、`invariants.md`、模块头部编号引用、离线测试 |
| agent 治理 | `AGENTS.md`、`Prompt.md`、`ai-use-log.yaml`、`review-memo.md`、`transcripts/60392800-YiyangBU.md`、`ci.yml`、`scripts/` |
