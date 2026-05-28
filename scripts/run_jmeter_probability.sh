#!/usr/bin/env bash
set -euo pipefail
command -v jmeter >/dev/null 2>&1 || { echo "jmeter command not found. Please install Apache JMeter and add its bin directory to PATH."; exit 1; }
mkdir -p reports/jmeter
rm -rf reports/jmeter/probability_validate_html reports/jmeter/probability_validate.jtl
jmeter -n -t jmeter/probability_validate_load_test.jmx -l reports/jmeter/probability_validate.jtl -e -o reports/jmeter/probability_validate_html
echo "Report: reports/jmeter/probability_validate_html/index.html"
