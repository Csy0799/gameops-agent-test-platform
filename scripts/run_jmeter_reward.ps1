$ErrorActionPreference = "Stop"
if (-not (Get-Command jmeter -ErrorAction SilentlyContinue)) {
    Write-Error "jmeter command not found. Please install Apache JMeter and add its bin directory to PATH."
}
New-Item -ItemType Directory -Force -Path "reports/jmeter" | Out-Null
Remove-Item -Recurse -Force "reports/jmeter/reward_claim_html" -ErrorAction SilentlyContinue
Remove-Item -Force "reports/jmeter/reward_claim.jtl" -ErrorAction SilentlyContinue
jmeter -n -t "jmeter/reward_claim_load_test.jmx" -l "reports/jmeter/reward_claim.jtl" -e -o "reports/jmeter/reward_claim_html"
Write-Host "Report: reports/jmeter/reward_claim_html/index.html"
