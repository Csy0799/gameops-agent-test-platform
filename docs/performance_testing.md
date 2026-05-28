# Performance Testing

## 1. Goals

Day 8 adds a JMeter-based performance testing plan for core SDET portfolio scenarios. The goal is to demonstrate API load testing, HTML report generation, metric interpretation, and post-test data consistency checks.

## 2. Why These APIs

- `/api/rewards/claim`: high-risk path involving idempotency, wallet updates, reward pool deduction, and reward records.
- `/api/activities`: activity configuration creation path.
- `/api/agent/generate_activity`: Agent workflow path covering FakeLLM, guardrail, probability simulation, and review routing.
- `/api/tools/probability/validate`: CPU-oriented Monte Carlo simulation path.

## 3. JMeter Plans

- `jmeter/activity_create_load_test.jmx`: 20 threads, 10s ramp-up, 5 loops.
- `jmeter/reward_claim_load_test.jmx`: 50 threads, 10s ramp-up, 5 loops.
- `jmeter/agent_generate_load_test.jmx`: 20 threads, 10s ramp-up, 3 loops.
- `jmeter/probability_validate_load_test.jmx`: 20 threads, 10s ramp-up, 3 loops.

## 4. Install JMeter

Download Apache JMeter from the official website, unzip it, and add the `bin` directory to `PATH`.

Verify:

```bash
jmeter --version
```

## 5. Start FastAPI

```bash
uvicorn app.main:app --reload
```

## 6. Prepare Test Data

CSV files live in `jmeter/data/`.

For reward claim tests, confirm `activity_id` in `reward_claim_payloads.csv` exists and is published. The file intentionally includes a repeated `idempotency_key` to validate duplicated request behavior.

## 7. Run One Load Test

Windows:

```powershell
.\scripts\run_jmeter_reward.ps1
```

Linux/Mac:

```bash
bash scripts/run_jmeter_reward.sh
```

## 8. Run All Load Tests

Windows:

```powershell
.\scripts\run_jmeter_all.ps1
```

Linux/Mac:

```bash
bash scripts/run_jmeter_all.sh
```

## 9. View HTML Reports

Open:

```text
reports/jmeter/*_html/index.html
```

## 10. Key Metrics

- Samples: total number of requests.
- Average: average response time.
- Median: 50th percentile response time.
- 90% Line: P90 latency.
- 95% Line: P95 latency.
- 99% Line: P99 latency.
- Min / Max: fastest and slowest response time.
- Error %: failed request ratio.
- Throughput: requests per second or per minute.
- Received KB/sec: response bandwidth.
- Sent KB/sec: request bandwidth.

## 11. Post-Test Data Consistency Checks

After reward claim load tests:

- Query user wallets: `GET /api/users/{user_id}/wallet`
- Query reward records: `GET /api/rewards/records`
- Query operation logs: `GET /api/operation-logs`
- Verify duplicated `idempotency_key` did not issue rewards twice.
- Verify `reward_pool_gold` deduction matches successful unique reward records.

## 12. Limitations

- Local SQLite is not suitable for real high-concurrency writes.
- These tests demonstrate method and reveal basic bottlenecks.
- Production load tests should use MySQL/PostgreSQL, proper connection pools, monitoring, and stronger concurrency control.

## 13. Follow-up Plan

- MySQL load testing.
- Redis idempotency lock.
- Prometheus/Grafana metrics.
- CI smoke performance tests.
- Unity client end-to-end load testing.
