# API Overview

All APIs use the unified response shape:

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

## Health

### GET /api/health

功能：服务健康检查。

响应示例：

```json
{"code":0,"message":"success","data":{"status":"ok"}}
```

关键测试点：HTTP 200、统一响应结构、status 为 ok。

## Activity

### GET /api/activities

功能：查询活动列表。

关键测试点：列表总数、创建顺序、统一响应结构。

### POST /api/activities

功能：创建 draft 活动。

请求示例：

```json
{
  "name": "Spring Event",
  "start_time": "2026-06-01T00:00:00",
  "end_time": "2026-06-08T00:00:00",
  "reward_pool_gold": 100000,
  "reward_pool_diamond": 0,
  "drop_item_id": "rare_box",
  "drop_probability": 0.2,
  "daily_limit": 3,
  "pity_threshold": 50,
  "risk_level": "medium"
}
```

关键测试点：概率边界、时间范围、daily_limit、奖池非负、默认 status=draft。

### GET /api/activities/{activity_id}

功能：查询指定活动。

关键测试点：存在返回成功，不存在返回明确错误。

### POST /api/activities/{activity_id}/publish

功能：发布 draft 活动。

关键测试点：发布成功、重复发布失败。

### POST /api/activities/{activity_id}/rollback

功能：回滚 published 活动。

关键测试点：published 可回滚，draft 不可回滚。

## Reward

### POST /api/rewards/claim

功能：领取奖励。

请求示例：

```json
{
  "user_id": "user_001",
  "activity_id": 1,
  "idempotency_key": "user_001_activity_1_001"
}
```

关键测试点：published 才能领取、daily_limit、奖池不足、重复 idempotency_key 不重复发奖。

### GET /api/users/{user_id}/wallet

功能：查询钱包，不存在时返回零余额钱包。

关键测试点：领取后 gold 增加，不存在用户行为一致。

### GET /api/rewards/records

功能：查询奖励流水。

关键测试点：领取成功后写入 RewardRecord。

## Probability

### POST /api/tools/probability/validate

功能：校验掉落概率并执行 Monte Carlo 模拟。

请求示例：

```json
{"probability":0.2,"sample_size":10000,"tolerance":0.02,"seed":42,"pity_threshold":50}
```

关键测试点：概率边界、seed 稳定性、tolerance、低概率 warning。

## Agent

### POST /api/agent/generate_activity

功能：从自然语言需求生成活动配置，低/中风险直接创建 draft，高风险进入 review queue。

请求示例：

```json
{"requirement":"创建一个周末世界Boss活动，掉落概率20%，每人每天最多领取3次，总金币预算1000000"}
```

关键测试点：FakeLLM 输出稳定、高风险 pending_review、危险指令 rejected。

### POST /api/agent/review/{review_id}

功能：approve / reject pending review。

请求示例：

```json
{"action":"approve"}
```

关键测试点：approve 创建 draft activity，reject 不创建，review 状态持久化。

### GET /api/agent/reviews

功能：Review Queue，默认查询 pending。支持 `status=pending|approved|rejected|all`。

关键测试点：已审核记录从 pending queue 隐藏，但 status=all 可查。

### GET /api/agent/reviews/{review_id}

功能：查询指定 review 详情。

关键测试点：存在返回配置和概率结果，不存在返回 not_found。

## OperationLog

### GET /api/operation-logs

功能：查询操作日志，支持 operation_type、target_type、actor、limit。

关键测试点：关键操作有留痕，过滤生效。

### POST /api/operation-logs/cleanup

功能：按保留天数清理过期日志。

请求示例：

```json
{"retention_days":365}
```

关键测试点：过期日志删除，未过期日志保留。

## Admin

### GET /admin/reviews

功能：简单 HTML Review Queue 页面。

关键测试点：显示 pending review，Approve / Reject 后刷新并从 pending queue 隐藏。
