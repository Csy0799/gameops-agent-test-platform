#!/usr/bin/env bash
set -euo pipefail
command -v jmeter >/dev/null 2>&1 || { echo "jmeter command not found. Please install Apache JMeter and add its bin directory to PATH."; exit 1; }
mkdir -p reports/jmeter
rm -rf reports/jmeter/reward_claim_html reports/jmeter/reward_claim.jtl
jmeter -n -t jmeter/reward_claim_load_test.jmx -l reports/jmeter/reward_claim.jtl -e -o reports/jmeter/reward_claim_html
echo "Report: reports/jmeter/reward_claim_html/index.html"
