#!/usr/bin/env bash
set -euo pipefail
command -v jmeter >/dev/null 2>&1 || { echo "jmeter command not found. Please install Apache JMeter and add its bin directory to PATH."; exit 1; }
mkdir -p reports/jmeter
rm -rf reports/jmeter/activity_create_html reports/jmeter/activity_create.jtl
jmeter -n -t jmeter/activity_create_load_test.jmx -l reports/jmeter/activity_create.jtl -e -o reports/jmeter/activity_create_html
echo "Report: reports/jmeter/activity_create_html/index.html"
