$ErrorActionPreference = "SilentlyContinue"

Write-Host "Stopping KNOCK backend processes..."

$uvicornProcs = Get-CimInstance Win32_Process -Filter "name = 'python.exe'" |
  Where-Object {
    $_.CommandLine -like '*uvicorn app.main:app*' -or
    $_.CommandLine -like '*uvicorn.exe*app.main:app*'
  }

foreach ($proc in $uvicornProcs) {
  Write-Host "Stopping uvicorn process $($proc.ProcessId)"
  Stop-Process -Id $proc.ProcessId -Force
}

foreach ($port in @(8000, 8010)) {
  $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
  foreach ($connection in $connections) {
    if ($connection.OwningProcess -and $connection.OwningProcess -ne 0) {
      $ownerProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $($connection.OwningProcess)"
      $commandLine = if ($ownerProcess) { $ownerProcess.CommandLine } else { "" }
      if ($commandLine -like '*uvicorn app.main:app*' -or $commandLine -like '*uvicorn.exe*app.main:app*') {
        Write-Host "Stopping KNOCK backend process $($connection.OwningProcess) using port $port"
        Stop-Process -Id $connection.OwningProcess -Force
      }
    }
  }
}

Write-Host "Done."
