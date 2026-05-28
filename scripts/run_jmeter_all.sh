#!/usr/bin/env bash
set -euo pipefail

bash scripts/run_jmeter_activity.sh
bash scripts/run_jmeter_reward.sh
bash scripts/run_jmeter_agent.sh
bash scripts/run_jmeter_probability.sh
