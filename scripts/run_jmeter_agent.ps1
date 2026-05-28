$ErrorActionPreference = "Stop"
if (-not (Get-Command jmeter -ErrorAction SilentlyContinue)) {
    Write-Error "jmeter command not found. Please install Apache JMeter and add its bin directory to PATH."
}
New-Item -ItemType Directory -Force -Path "reports/jmeter" | Out-Null
Remove-Item -Recurse -Force "reports/jmeter/agent_generate_html" -ErrorAction SilentlyContinue
Remove-Item -Force "reports/jmeter/agent_generate.jtl" -ErrorAction SilentlyContinue
jmeter -n -t "jmeter/agent_generate_load_test.jmx" -l "reports/jmeter/agent_generate.jtl" -e -o "reports/jmeter/agent_generate_html"
Write-Host "Report: reports/jmeter/agent_generate_html/index.html"
