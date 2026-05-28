$ErrorActionPreference = "Stop"
if (-not (Get-Command jmeter -ErrorAction SilentlyContinue)) {
    Write-Error "jmeter command not found. Please install Apache JMeter and add its bin directory to PATH."
}
New-Item -ItemType Directory -Force -Path "reports/jmeter" | Out-Null
Remove-Item -Recurse -Force "reports/jmeter/activity_create_html" -ErrorAction SilentlyContinue
Remove-Item -Force "reports/jmeter/activity_create.jtl" -ErrorAction SilentlyContinue
jmeter -n -t "jmeter/activity_create_load_test.jmx" -l "reports/jmeter/activity_create.jtl" -e -o "reports/jmeter/activity_create_html"
Write-Host "Report: reports/jmeter/activity_create_html/index.html"
