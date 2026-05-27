# gameops-agent-test-platform

## 项目背景

`gameops-agent-test-platform` 是一个面向测试开发 / SDET 实习简历展示的后端项目。项目核心场景是“游戏运营活动配置与质量保障平台”，用于逐步沉淀活动配置、质量校验、接口测试、性能测试与测试报告能力。

当前已完成 Day 1 到 Day 3：

- Day 1：FastAPI 基础服务、健康检查、统一响应结构和基础测试。
- Day 2：活动配置 API，支持创建、查询、列表、发布和回滚。
- Day 3：奖励领取、用户钱包、奖励流水、幂等校验和 daily limit 校验。

暂未实现 Agent、概率校验、JMeter、Docker、CI 等后续功能。

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
