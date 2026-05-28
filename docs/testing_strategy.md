# Testing Strategy

## 1. Testing Goals

The test suite validates the GameOps activity configuration and QA platform from service-level rules to API-level workflows. The current goal is to make the project suitable for SDET portfolio demonstration: stable tests, reproducible local execution, coverage reports, and Allure test reports.

## 2. Test Layers

- Unit tests: Validate service-level logic such as probability simulation, LLM provider selection, and operation log cleanup.
- API tests: Validate FastAPI endpoints, unified response structure, validation errors, and persistence behavior.
- Integration tests: Cover multi-step flows such as activity publish, reward claim, Agent pending review, and review approval.
- Regression tests: Lock down historical risk scenarios such as duplicate reward claims, dangerous instruction rejection, and review queue persistence.
- Agent workflow tests: Validate FakeLLM generation, guardrail checks, risk routing, and human review behavior.

## 3. Covered Modules

- Health Check
- Activity Management
- Reward Claim
- Idempotency
- Probability Validation
- Agent Workflow
- Guardrail
- Human Review
- OperationLog

## 4. Key Quality Risks

- Duplicate reward payout
- Reward pool being deducted more than once
- Invalid activity state transitions
- Incorrect probability configuration
- High-risk Agent output being persisted without review
- Dangerous instructions not being blocked
- Review records being lost after service reload
- Missing operation audit logs

## 5. Run Tests

```bash
python -m pytest -q
```

Windows:

```powershell
.\scripts\run_tests.ps1
```

## 6. Coverage Report

```bash
python -m pytest --cov=app --cov-report=term-missing --cov-report=html
```

Windows:

```powershell
.\scripts\run_coverage.ps1
```

Open:

```text
htmlcov/index.html
```

## 7. Allure Report

```bash
python -m pytest --alluredir=reports/allure-results
```

If Allure CLI is installed:

```bash
allure serve reports/allure-results
```

Windows:

```powershell
.\scripts\run_allure.ps1
```

## 8. Current Limitations

- Tests use SQLite in memory and do not cover production database behavior.
- Concurrency is not deeply tested yet.
- Allure report generation depends on local Allure CLI installation for browser rendering.
- Performance testing is not included in Day 7.

## 9. Follow-up Plan

- JMeter performance tests
- CI automated test execution
- Unity client end-to-end tests
