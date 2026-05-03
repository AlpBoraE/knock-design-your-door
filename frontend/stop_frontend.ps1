param(
  [int]$Port = 5500
)

$ErrorActionPreference = "SilentlyContinue"

Write-Host "Stopping KNOCK frontend server on port $Port..."

$existing = Get-CimInstance Win32_Process -Filter "name = 'python.exe'" |
  Where-Object { $_.CommandLine -like "*http.server $Port*" }

foreach ($proc in $existing) {
  Write-Host "Stopping frontend process $($proc.ProcessId)"
  Stop-Process -Id $proc.ProcessId -Force
}

Write-Host "Done."

