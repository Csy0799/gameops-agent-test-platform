# gameops-agent-test-platform

## 项目背景

`gameops-agent-test-platform` 是一个面向测试开发 / SDET 实习简历展示的后端项目。项目核心场景是“游戏运营活动配置与质量保障平台”，用于逐步沉淀活动配置、质量校验、接口测试、性能测试与测试报告能力。

当前已完成 Day 1 到 Day 3：

- Day 1：FastAPI 基础服务、健康检查、统一响应结构和基础测试。
- Day 2：活动配置 API，支持创建、查询、列表、发布和回滚。
- Day 3：奖励领取、用户钱包、奖励流水、幂等校验和 daily limit 校验。
- Day 4：掉落概率规则校验、Monte Carlo 模拟和保底规则提示。
- Day 5：Agent 工作流、LLM Provider 架构、风险拦截和人工审核。

暂未实现 Agent、JMeter、Docker、CI 等后续功能。

## 技术栈

- Python 3.9+
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy
- SQLite
- Pytest
- Pytest-Cov
- HTTPX
- Allure Pytest

## 本地启动方式

创建并激活虚拟环境：

```bash
python -m venv .venv
.venv\Scripts\activate
```

安装依赖：

```bash
python -m pip install -e .
```

启动服务：

```bash
uvicorn app.main:app --reload
```

健康检查：

```bash
curl http://127.0.0.1:8000/api/health
```

期望返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "status": "ok"
  }
}
```

## 测试运行方式

运行全部测试：

```bash
python -m pytest -q
```

运行覆盖率测试：

```bash
python -m pytest --cov=app
```

## 活动配置模块

Day 2 新增游戏运营活动配置 API，支持活动创建、查询、列表、发布和回滚。当前模块处理活动配置生命周期，不包含奖励领取之外的后续测试平台能力。

活动状态：

- `draft`：草稿，活动创建后的默认状态。
- `published`：已发布，允许玩家领取奖励。
- `rolled_back`：已回滚，不允许继续领取奖励。

本地开发默认使用 SQLite，数据库文件为项目根目录下的 `gameops.db`。

### Day 2 API

- `POST /api/activities`：创建活动
- `GET /api/activities/{activity_id}`：查询单个活动
- `GET /api/activities`：查询活动列表
- `POST /api/activities/{activity_id}/publish`：发布活动
- `POST /api/activities/{activity_id}/rollback`：回滚活动

创建活动示例：

```bash
curl -X POST http://127.0.0.1:8000/api/activities \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Spring Festival Login Event",
    "start_time": "2026-06-01T00:00:00",
    "end_time": "2026-06-10T23:59:59",
    "reward_pool_gold": 10000,
    "reward_pool_diamond": 500,
    "drop_item_id": "item_1001",
    "drop_probability": 0.25,
    "daily_limit": 3,
    "pity_threshold": 10,
    "risk_level": "low"
  }'
```

## 奖励领取模块

Day 3 新增奖励领取模块，覆盖用户钱包、奖励流水、奖池扣减、daily limit 和幂等校验。

领取规则：

- 只有 `published` 状态活动可以领取。
- 当前时间必须在活动 `start_time` 和 `end_time` 之间。
- 同一用户同一活动当天成功领取次数不能超过 `daily_limit`。
- 奖池不足时拒绝领取。
- 首次领取成功后，活动奖池扣减、用户钱包增加、奖励流水写入在同一个数据库事务中完成。

### 幂等 Key 设计

客户端调用 `POST /api/rewards/claim` 时必须传入 `idempotency_key`。该 key 在 `RewardRecord` 中唯一。

- 第一次请求成功：写入奖励流水，返回 `duplicated=false`。
- 相同 `idempotency_key` 重复请求：不会重复扣奖池、不会重复加钱包，返回第一次领取结果并标记 `duplicated=true`。

### 一致性说明

奖励领取成功时会在同一个 SQLAlchemy session 事务中完成：

- `Activity.reward_pool_gold` 扣减固定奖励金币。
- `UserWallet.gold` 增加固定奖励金币。
- `RewardRecord` 写入成功流水。

如果过程中出现业务错误或数据库异常，会执行 rollback，避免奖池、钱包和流水出现部分成功。

### Day 3 API

- `POST /api/rewards/claim`：领取奖励
- `GET /api/users/{user_id}/wallet`：查询用户钱包，不存在时返回零余额钱包
- `GET /api/rewards/records`：查询奖励流水列表

领取奖励示例：

```bash
curl -X POST http://127.0.0.1:8000/api/rewards/claim \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "activity_id": 1,
    "idempotency_key": "claim-user-001-activity-1-001"
  }'
```

## 简历 Bullet 初稿

- 设计并实现基于 FastAPI + SQLAlchemy 的游戏运营活动配置与奖励领取后端服务，覆盖活动发布、回滚、钱包发奖、奖池扣减和奖励流水追踪。
- 引入 `idempotency_key` 幂等机制，防止客户端重试导致重复发奖，并通过 pytest 验证重复请求下钱包与奖池金额保持一致。
- 构建接口级自动化测试，覆盖活动配置校验、状态流转、奖励领取限制、异常路径和 Windows 下 SQLite 测试数据库隔离问题。

## 概率校验模块

Day 4 新增游戏掉落概率校验工具，用于发现活动配置中的掉率边界错误、模拟偏差风险和保底规则缺失问题。该模块不依赖数据库，也不修改活动或奖励领取链路。

校验能力：

- `probability` 必须在 `[0, 1]` 范围内。
- `sample_size` 必须大于 0。
- `tolerance` 必须大于 0。
- `pity_threshold` 如果存在，必须大于 0。
- 低概率且没有保底阈值时返回 warning。
- `probability=0` 且配置了保底阈值时返回 warning，提示保底是唯一获得途径，需要重点审核。

### Monte Carlo 模拟说明

接口会根据传入的 `probability`、`sample_size` 和 `seed` 进行 Monte Carlo 模拟，返回实际掉率、期望掉率、偏差值和是否通过容忍度检查。

固定 `seed` 用于保证自动化测试和本地复现稳定。`probability=0` 时实际掉率固定为 `0`，`probability=1` 时实际掉率固定为 `1`。

### Day 4 API

- `POST /api/tools/probability/validate`：校验掉落概率配置并返回模拟结果

概率校验示例：

```bash
curl -X POST http://127.0.0.1:8000/api/tools/probability/validate \
  -H "Content-Type: application/json" \
  -d '{
    "probability": 0.2,
    "sample_size": 100000,
    "tolerance": 0.01,
    "seed": 42,
    "pity_threshold": 20
  }'
```

返回示例：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "expected_probability": 0.2,
    "actual_probability": 0.20156,
    "deviation": 0.00156,
    "sample_size": 100000,
    "tolerance": 0.01,
    "pass": true,
    "warnings": []
  }
}
```

## 简历 Bullet 补充

- 实现游戏掉落概率校验工具，结合规则校验与 Monte Carlo 模拟输出结构化结果，覆盖掉率边界、样本量、容忍度和保底阈值风险。
- 使用固定随机种子保证概率模拟测试可复现，并通过 pytest 覆盖边界概率、低概率 warning、保底规则和 API 统一响应。

## Agent 工作流模块

Day 5 新增 Agent 工作流，用于把运营自然语言需求转成活动配置草稿，并串联规则校验、概率模拟、预算风控、危险指令拦截和 Human-in-the-loop 人工审核。

工作流不会自动发布活动。低/中风险需求会创建 `draft` 活动，高风险需求进入 `pending_review`，危险指令会直接 `rejected`。

```mermaid
flowchart TD
    A[User Requirement] --> B[Guardrail Check]
    B -->|Dangerous| R[Rejected]
    B -->|Safe| C[LLM Provider Generate Config]
    C --> D[Rule Validation]
    D --> E[Probability Simulation]
    E --> F[Risk Check]
    F -->|Low/Medium Risk| G[Create Draft Activity]
    F -->|High Risk| H[Human Review]
    H -->|Approve| G
    H -->|Reject| I[Rejected]
```

### LLM Provider 架构

Agent 依赖 `BaseLLMProvider` 抽象，而不是直接依赖 FakeLLM。

默认模式：

```bash
LLM_PROVIDER=fake
```

可选真实 LLM 模式：

```bash
LLM_PROVIDER=openai
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

当前项目测试环境永远使用 `FakeLLMProvider`，避免测试依赖网络和 API Key。`OpenAICompatibleProvider` 作为工程扩展点保留，用于展示项目具备接入真实模型的能力；如果缺少 `LLM_API_KEY`，会抛出清晰错误。

### FakeLLMProvider 设计

`FakeLLMProvider` 不调用外部 API，输出稳定，便于 pytest 验证。它会根据关键词生成活动配置，例如：

- “周末世界Boss / 世界BOSS”生成 `weekend_boss_event`。
- “金币预算1000000”生成金币奖池。
- “掉落概率20% / 掉率20%”生成 `drop_probability=0.2`。
- “每天最多领取3次”生成 `daily_limit=3`。
- 高预算、高掉率或钻石奖励会标记为 `risk_level=high`。

### Guardrail 危险指令拦截

以下危险词会直接 rejected，不进入配置生成：

- 中文：`直接执行SQL`、`执行SQL`、`绕过审核`、`无限奖励`、`删除数据库`
- 英文：`drop table`、`bypass review`、`unlimited reward`、`delete database`

### Human-in-the-loop 人工审核

以下情况进入 `pending_review`：

- `risk_level=high`
- `reward_pool_gold > 1000000`
- `drop_probability > 0.5`
- `reward_pool_diamond > 0`
- 概率模拟未通过 tolerance

pending review 会保存在内存 review store 中。`approve` 后创建 `draft` 活动，`reject` 后不创建活动。当前阶段不持久化 review store，pytest 会自动清理，避免测试污染。

### Day 5 API

- `POST /api/agent/generate_activity`：从自然语言需求生成活动草稿或进入审核
- `POST /api/agent/review/{review_id}`：人工审核 approve / reject

生成活动示例：

```bash
curl -X POST http://127.0.0.1:8000/api/agent/generate_activity \
  -H "Content-Type: application/json" \
  -d '{
    "requirement": "创建一个周末世界Boss活动，掉落概率20%，每人每天最多领取3次，总金币预算1000000"
  }'
```

审核示例：

```bash
curl -X POST http://127.0.0.1:8000/api/agent/review/review_xxx \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve"
  }'
```

## 简历 Bullet 补充 2

- 设计可扩展 LLM Provider 架构，默认使用 FakeLLM 保证测试稳定，同时预留 OpenAI-compatible Provider 作为真实模型接入扩展点。
- 实现运营活动 Agent 工作流，将自然语言需求转成活动配置，并串联规则校验、概率模拟、预算风控、危险指令拦截与人工审核。
- 构建 Human-in-the-loop 审核机制，高风险配置进入 pending review，人工 approve 后才创建 draft 活动，避免高风险活动自动落库。
