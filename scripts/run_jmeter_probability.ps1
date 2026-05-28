$ErrorActionPreference = "Stop"
if (-not (Get-Command jmeter -ErrorAction SilentlyContinue)) {
    Write-Error "jmeter command not found. Please install Apache JMeter and add its bin directory to PATH."
}
New-Item -ItemType Directory -Force -Path "reports/jmeter" | Out-Null
Remove-Item -Recurse -Force "reports/jmeter/probability_validate_html" -ErrorAction SilentlyContinue
Remove-Item -Force "reports/jmeter/probability_validate.jtl" -ErrorAction SilentlyContinue
jmeter -n -t "jmeter/probability_validate_load_test.jmx" -l "reports/jmeter/probability_validate.jtl" -e -o "reports/jmeter/probability_validate_html"
Write-Host "Report: reports/jmeter/probability_validate_html/index.html"
