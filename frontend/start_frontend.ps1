param(
  [int]$Port = 5500
)

$ErrorActionPreference = "Stop"
$ProjectFrontend = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectFrontend

$existing = Get-CimInstance Win32_Process -Filter "name = 'python.exe'" |
  Where-Object { $_.CommandLine -like "*http.server $Port*" }

foreach ($proc in $existing) {
  Write-Host "Stopping old frontend server $($proc.ProcessId)"
  Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
}

$portConnections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
foreach ($connection in $portConnections) {
  $owner = $connection.OwningProcess
  if ($owner -and $owner -ne $PID) {
    Write-Host "Stopping process $owner using port $Port"
    Stop-Process -Id $owner -Force -ErrorAction SilentlyContinue
  }
}

Write-Host "Starting frontend at http://127.0.0.1:$Port"
Write-Host "Press Ctrl+C to stop."
python -m http.server $Port --bind 127.0.0.1

