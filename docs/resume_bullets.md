# Resume Bullets

## 1. 游戏测开版

项目名：GameOps Agent Test Platform｜游戏运营 Agent 自动化测试与压测平台

### 中文精简版

- 基于 FastAPI 实现游戏运营活动配置、奖励领取、虚拟货币钱包、掉率校验和 Agent 审核流程。
- 使用 pytest + Allure + coverage 构建自动化测试体系，覆盖幂等、防重复发奖、奖池扣减和审核留痕。
- 使用 JMeter 设计活动创建、奖励领取、Agent 生成和概率校验接口压测方案。

### 中文详细版

- 设计活动配置 API，覆盖 draft/published/rolled_back 状态流转，并通过 pytest 验证非法状态转换。
- 实现奖励领取链路，使用 idempotency_key 防止重复发奖，保证钱包增加、奖池扣减、奖励流水写入一致。
- 实现掉率和保底规则校验工具，使用 Monte Carlo 模拟输出期望掉率、实际掉率、偏差和 warning。
- 实现 Agent workflow，将自然语言活动需求转为配置，高风险活动进入持久化 Review Queue。
- 使用 JMeter 对活动创建、奖励领取、Agent 生成和概率校验接口进行压测方案设计并输出 HTML 报告。

### English Short Version

- Built a FastAPI-based GameOps QA platform covering activity configuration, reward claim, wallet, drop-rate validation, and Agent review.
- Created pytest, Allure, and coverage test suites for idempotency, reward consistency, risk review, and audit logs.
- Designed JMeter load tests for activity creation, reward claim, Agent generation, and probability validation APIs.

### English Detailed Version

- Implemented activity lifecycle APIs with draft, published, and rolled_back states and regression tests for invalid transitions.
- Built reward claim workflow with idempotency_key to prevent duplicate payouts and keep wallet, reward pool, and records consistent.
- Added probability validation using Monte Carlo simulation for expected rate, actual rate, deviation, tolerance, and warnings.
- Implemented Agent workflow with FakeLLMProvider, guardrail checks, risk routing, and persistent human review queue.
- Designed JMeter performance plans and scripts to generate HTML reports for core GameOps APIs.

### 面试关键词

游戏运营、虚拟货币、奖励流水、幂等、掉率、保底、Agent 审核、JMeter、Allure。

## 2. 非游戏互联网测开版

项目名：OpsFlow Agent Test Platform｜运营配置与权益发放自动化测试平台

### 中文精简版

- 实现运营配置与权益发放后端服务，覆盖额度、钱包、流水和幂等 key。
- 构建接口自动化、集成回归、coverage 和 Allure 报告体系。
- 接入 OperationLog 和 CI，提升问题定位、缺陷复现和自动化验收能力。

### 中文详细版

- 抽象活动配置为运营配置场景，实现创建、发布、回滚和查询接口。
- 设计权益领取链路，使用 idempotency_key 防止重复请求导致重复发放。
- 使用 OperationLog 记录关键操作，支持按 operation_type、target_type 和 actor 查询。
- 使用 pytest fixture 构建稳定测试数据库隔离机制，避免 Windows SQLite 文件句柄问题。
- 使用 GitHub Actions 自动运行 pytest 和 coverage，并上传测试报告 artifact。

### English Short Version

- Built an operations configuration and benefit-claim QA platform with quota, wallet, records, and idempotency checks.
- Created API, integration, regression, coverage, and Allure test reporting.
- Added OperationLog and CI workflow for traceability, debugging, and automated validation.

### English Detailed Version

- Modeled operational campaigns with create, publish, rollback, and query APIs.
- Designed benefit claim workflow using idempotency_key to prevent duplicate grants.
- Added OperationLog audit trail for critical operations with query and cleanup APIs.
- Built stable pytest fixtures with in-memory SQLite and StaticPool to avoid Windows file lock issues.
- Added GitHub Actions to run pytest and coverage and upload report artifacts.

### 面试关键词

权益发放、幂等 key、额度一致性、接口自动化、pytest、OperationLog、CI。

## 3. AI 应用测试版

项目名：AgentOps QA Platform｜Agent 工作流质量保障平台

### 中文精简版

- 设计 LLM Provider 抽象，默认使用 FakeLLM 保证 Agent 测试稳定可复现。
- 实现 Guardrail、工具调用、风险判断和 Human-in-the-loop 审核流程。
- 使用 pytest 覆盖 Agent workflow、危险指令拦截、审核持久化和操作审计。

### 中文详细版

- 设计 BaseLLMProvider，预留 OpenAI-compatible Provider，测试环境默认 FakeLLMProvider。
- 实现自然语言需求到结构化配置的 Agent workflow，串联规则校验、概率模拟和风控。
- 实现危险指令 Guardrail，拦截 SQL 执行、绕过审核、无限奖励等中英文危险词。
- 实现持久化 Review Queue，高风险输出必须人工 approve 后才创建 draft 配置。
- 使用 Allure 按 Agent Workflow、Guardrail、Human Review 等 feature 展示测试报告。

### English Short Version

- Designed an LLM Provider abstraction with FakeLLM for stable and reproducible Agent testing.
- Implemented guardrails, tool calls, risk checks, and human-in-the-loop review workflow.
- Covered Agent workflows, dangerous instruction rejection, review persistence, and audit logs with pytest.

### English Detailed Version

- Designed BaseLLMProvider with an OpenAI-compatible extension point while defaulting tests to FakeLLMProvider.
- Built an Agent workflow that turns natural language requirements into structured configs with rule validation and probability simulation.
- Added guardrails to reject dangerous Chinese and English instructions before configuration generation.
- Implemented persistent Review Queue so high-risk outputs require human approval before draft activity creation.
- Used Allure features and stories to present Agent workflow, guardrail, and human review test coverage.

### 面试关键词

LLM Provider、FakeLLM、Guardrail、Human-in-the-loop、工具调用、审计日志、Agent 测试。
