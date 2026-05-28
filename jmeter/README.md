# JMeter Load Tests

This directory contains JMeter plans for the GameOps Agent Test Platform.

## Test Plans

- `activity_create_load_test.jmx`: load test for `POST /api/activities`
- `reward_claim_load_test.jmx`: load test for `POST /api/rewards/claim`
- `agent_generate_load_test.jmx`: load test for `POST /api/agent/generate_activity`
- `probability_validate_load_test.jmx`: load test for `POST /api/tools/probability/validate`

## Prerequisites

- FastAPI service is running: `uvicorn app.main:app --reload`
- Apache JMeter is installed
- JMeter `bin` directory is added to `PATH`
- Before running reward claim load tests, make sure the CSV `activity_id` exists and the activity is `published`

## Windows Examples

```powershell
.\scripts\run_jmeter_activity.ps1
.\scripts\run_jmeter_reward.ps1
.\scripts\run_jmeter_agent.ps1
.\scripts\run_jmeter_probability.ps1
.\scripts\run_jmeter_all.ps1
```

## Linux/Mac Examples

```bash
bash scripts/run_jmeter_activity.sh
bash scripts/run_jmeter_reward.sh
bash scripts/run_jmeter_agent.sh
bash scripts/run_jmeter_probability.sh
bash scripts/run_jmeter_all.sh
```

## Report Paths

- `reports/jmeter/activity_create_html/index.html`
- `reports/jmeter/reward_claim_html/index.html`
- `reports/jmeter/agent_generate_html/index.html`
- `reports/jmeter/probability_validate_html/index.html`

## Common Errors

- `jmeter command not found`: install Apache JMeter and add `bin` to `PATH`
- `output folder already exists`: rerun the provided scripts, they clean old report folders
- `connection refused`: start FastAPI first
- `activity not found` or `only published activity can be claimed`: create and publish the activity referenced by `reward_claim_payloads.csv`
- duplicated `idempotency_key`: wallet does not increase again; this is expected idempotency behavior
