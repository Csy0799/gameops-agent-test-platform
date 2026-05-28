#!/usr/bin/env bash
set -euo pipefail
command -v jmeter >/dev/null 2>&1 || { echo "jmeter command not found. Please install Apache JMeter and add its bin directory to PATH."; exit 1; }
mkdir -p reports/jmeter
rm -rf reports/jmeter/agent_generate_html reports/jmeter/agent_generate.jtl
jmeter -n -t jmeter/agent_generate_load_test.jmx -l reports/jmeter/agent_generate.jtl -e -o reports/jmeter/agent_generate_html
echo "Report: reports/jmeter/agent_generate_html/index.html"
