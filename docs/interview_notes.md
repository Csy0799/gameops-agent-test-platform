# Interview Notes

## 1. 60 秒项目介绍

这是一个面向测试开发 / SDET 实习的 GameOps Agent Test Platform。它模拟游戏运营活动配置、奖励领取、掉率校验和 Agent 审核流程。我重点实现了活动状态流转、奖励幂等、防重复发奖、奖池和钱包一致性、概率模拟、Guardrail、Human-in-the-loop 审核、OperationLog 审计，以及 pytest、Allure、coverage、JMeter、Docker 和 GitHub Actions 交付链路。

## 2. 3 分钟项目介绍

项目从游戏运营活动出发：运营配置活动后，玩家领取奖励，系统要防止重复领取和数据不一致。后续我加入了概率校验工具，用 Monte Carlo 模拟发现掉率风险；再加入 Agent workflow，把自然语言需求转成配置，并通过 Guardrail 和 Review Queue 防止高风险活动自动落库。最后补齐测试和交付体系，包括 pytest 自动化测试、coverage、Allure、JMeter 压测计划、Docker 和 GitHub Actions。

## 3. 项目架构怎么讲

FastAPI 做 API 层，service 层承载业务逻辑，SQLAlchemy + SQLite 做本地持久化。Activity、Reward、Agent、Review、OperationLog 是核心域。测试层用 pytest + TestClient，测试数据库用内存 SQLite + StaticPool，避免 Windows 文件句柄问题。

## 4. 数据库表怎么讲

Activity 记录活动配置；UserWallet 记录用户余额；RewardRecord 记录奖励流水和 idempotency_key；AgentReviewRecord 持久化高风险审核；OperationLog 记录关键操作审计。

## 5. 幂等性怎么讲

领取奖励时客户端传 idempotency_key。第一次请求会加钱包、扣奖池、写流水；重复 key 请求直接返回第一次结果，不重复发奖。

## 6. 为什么需要 idempotency_key

网络重试、客户端重复点击、服务超时重放都可能导致重复请求。idempotency_key 是请求级唯一标识，可以区分“同一次请求重试”和“同一用户的另一次合法领取”。

## 7. 为什么不能用 user_id + activity_id 做唯一键

因为 daily_limit 允许同一用户同一活动每天领取多次。如果用 user_id + activity_id 唯一，会阻止合法多次领取。idempotency_key 更适合表达一次请求。

## 8. daily_limit 怎么实现

查询 RewardRecord 中同一 user_id、activity_id、当天 status=success 的记录数，达到 activity.daily_limit 后拒绝领取。

## 9. 钱包、奖池、奖励流水如何保证一致

在同一个 SQLAlchemy session 里完成钱包增加、奖池扣减、RewardRecord 写入。发生异常时 rollback，避免部分成功。

## 10. OperationLog 和 RewardRecord 区别

RewardRecord 是业务流水，描述发了什么奖励。OperationLog 是审计日志，描述谁做了什么操作、结果如何、目标对象是什么。

## 11. Review Queue 为什么要持久化

内存 review 在服务 reload 后会丢失，用户也可能忘记 review_id。持久化后可以通过 pending queue 查询，已审核记录也能保留审计。

## 12. FakeLLMProvider 为什么适合测试环境

FakeLLM 输出稳定、不依赖网络、不需要 API Key。它让 Agent workflow 测试可重复，避免真实 LLM 随机性影响自动化测试。

## 13. Guardrail 怎么设计

先做关键词黑名单，覆盖中英文危险词，如 drop table、绕过审核、无限奖励。命中后直接 rejected，不进入 LLM 生成。

## 14. Human-in-the-loop 为什么重要

高金币预算、高掉率、钻石奖励或概率模拟失败都可能有业务风险，不能自动落库，需要人工审核后再创建 draft activity。

## 15. Monte Carlo 概率校验怎么讲

用固定 seed 进行随机模拟，比较实际掉率和期望掉率的 deviation，如果超过 tolerance 就失败。固定 seed 保证测试稳定。

## 16. pytest fixture 怎么设计

client fixture 使用 FastAPI TestClient，覆盖 get_db 到内存 SQLite。每个测试 create_all/drop_all，dependency_overrides 清理，保证隔离。

## 17. Windows SQLite PermissionError 怎么解释

文件型 SQLite 在 Windows 下容易因为连接未释放导致 tmp_path 删除失败。项目改用 `sqlite:///:memory:` + StaticPool，避免文件句柄。

## 18. coverage / Allure 怎么讲

pytest-cov 输出终端和 HTML 覆盖率，Allure 根据 feature/story/title 展示测试报告，适合简历和面试演示。

## 19. JMeter 压测怎么讲

针对活动创建、奖励领取、Agent 生成、概率校验四类接口设计 JMeter 计划。重点看 Throughput、Average、P95/P99、Error Rate，并做压测后数据一致性校验。

## 20. Docker / CI 怎么讲

Dockerfile 支持容器启动 FastAPI。GitHub Actions 在 push/PR 时安装依赖、运行 pytest、coverage，并上传报告 artifact。

## 21. 如果迁移到 MySQL/Redis 怎么做

SQLAlchemy URL 改为 MySQL/PostgreSQL，加入 Alembic 迁移。幂等 key 可以加 Redis 分布式锁或数据库唯一约束配合事务。

## 22. 如果接真实 OpenAI-compatible LLM 怎么做

实现 OpenAICompatibleProvider 的 generate 方法，从 LLM_API_KEY、LLM_BASE_URL、LLM_MODEL 读取配置，要求输出 JSON schema，并加超时、重试、fallback。

## 23. 如果做 Unity Demo 怎么接入

Unity 客户端可以调用活动列表、奖励领取、钱包查询、概率校验展示接口。重点展示客户端触发领取后服务端幂等和钱包变化。

## 24. 面试官可能追问的 30 个问题和参考回答

1. Q: 项目是不是生产级？ A: 不是，是 portfolio/demo，但按真实质量保障链路拆模块。
2. Q: 最大风险是什么？ A: 重复发奖和数据不一致，所以重点做幂等和事务测试。
3. Q: 为什么用 SQLite？ A: 本地演示轻量；真实压测建议 MySQL/PostgreSQL。
4. Q: 为什么不是 user_id + activity_id 幂等？ A: daily_limit 允许多次领取。
5. Q: 重复 key 返回什么？ A: 返回第一次结果，duplicated=true。
6. Q: Agent 会直接发布活动吗？ A: 不会，只创建 draft。
7. Q: 高风险怎么判定？ A: risk_level high、高预算、高掉率、钻石奖励、概率模拟失败。
8. Q: Guardrail 漏判怎么办？ A: 后续可以规则库、模型分类器和人工审核兜底。
9. Q: OperationLog 写失败怎么办？ A: 当前捕获异常，不阻断主业务。
10. Q: RewardRecord 和 OperationLog 会重复吗？ A: 不重复，业务流水和审计日志职责不同。
11. Q: 测试隔离怎么做？ A: 每个测试内存库，create_all/drop_all。
12. Q: Allure 有什么价值？ A: 报告按 feature/story 展示，更适合评审和演示。
13. Q: JMeter 为什么不进 CI？ A: 当前是本地性能方案，CI 先做功能测试。
14. Q: 概率模拟稳定吗？ A: 固定 seed，测试稳定。
15. Q: FakeLLM 是不是写死？ A: 是稳定测试替身，但 workflow 依赖抽象 provider。
16. Q: OpenAI provider 能跑吗？ A: 当前保留接口，不在测试中真实调用。
17. Q: pending review 重启丢吗？ A: 不丢，写入 AgentReviewRecord。
18. Q: approve 后记录删除吗？ A: 不删除，只更新状态。
19. Q: 如何检查压测一致性？ A: 查钱包、流水、活动奖池和 OperationLog。
20. Q: 为什么设置 coverage fail_under 60？ A: 避免早期演示被过高门槛阻塞。
21. Q: API 错误结构统一吗？ A: 业务错误返回 code 非 0、message、data null。
22. Q: 如何扩展真实数据库？ A: 配置化 DATABASE_URL + Alembic。
23. Q: 如何做并发安全？ A: 数据库锁、Redis 锁、唯一约束和事务隔离。
24. Q: daily_limit 是按自然日吗？ A: 当前按 UTC 日期，可扩展时区配置。
25. Q: JMeter 数据怎么准备？ A: CSV 参数化，reward 需要 published activity。
26. Q: Review 页面为什么简单？ A: 当前重点是后端和测试能力，不做复杂前端。
27. Q: CI 上传什么？ A: coverage HTML 和 Allure results artifact。
28. Q: 项目亮点是什么？ A: 从业务风险反推测试设计，而不只是 CRUD。
29. Q: 还有什么不足？ A: 无真实并发锁、无生产 DB、无可观测监控。
30. Q: 下一步做什么？ A: Unity Demo、Dashboard、MySQL/Redis、真实 LLM、CI 性能 smoke。
