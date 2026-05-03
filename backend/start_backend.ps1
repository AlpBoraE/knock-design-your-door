param(
  [Nullable[int]]$Port = $null,
  [switch]$Reload
)

$ErrorActionPreference = "Stop"
$ProjectBackend = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectBackend

Write-Host "KNOCK backend starter"

$existingUvicorn = Get-CimInstance Win32_Process -Filter "name = 'python.exe'" |
  Where-Object {
    $_.CommandLine -like '*uvicorn app.main:app*' -or
    $_.CommandLine -like '*uvicorn.exe*app.main:app*'
  }

foreach ($proc in $existingUvicorn) {
  Write-Host "Stopping old uvicorn process $($proc.ProcessId)"
  Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
}

$candidatePorts = if ($Port) { @($Port) } else { @(8000, 8010) }
$portsToClear = $candidatePorts | Select-Object -Unique
$portConnections = foreach ($portToClear in $portsToClear) {
  Get-NetTCPConnection -LocalPort $portToClear -ErrorAction SilentlyContinue
}
foreach ($connection in $portConnections) {
  $owner = $connection.OwningProcess
  if ($owner -and $owner -ne $PID) {
    $ownerProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $owner" -ErrorAction SilentlyContinue
    $commandLine = if ($ownerProcess) { $ownerProcess.CommandLine } else { "" }
    if ($commandLine -like '*uvicorn app.main:app*' -or $commandLine -like '*uvicorn.exe*app.main:app*') {
      Write-Host "Stopping old KNOCK backend process $owner using port $($connection.LocalPort)"
      Stop-Process -Id $owner -Force -ErrorAction SilentlyContinue
    } else {
      Write-Host "Port $($connection.LocalPort) is used by another process ($owner). Leaving it alone."
    }
  }
}

if (-not $Port) {
  foreach ($candidate in $candidatePorts) {
    $inUse = Get-NetTCPConnection -LocalPort $candidate -ErrorAction SilentlyContinue
    if (-not $inUse) {
      $Port = $candidate
      break
    }
  }

  if (-not $Port) {
    throw "Ports 8000 and 8010 are both in use by other processes. Run .\\stop_backend.ps1 or choose a free port with -Port."
  }
}

Write-Host "Port: $Port"

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
  Write-Host "Creating virtual environment..."
  python -m venv .venv
}

Write-Host "Installing/updating dependencies..."
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

$uvicornArgs = @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "$Port")
if ($Reload) {
  $uvicornArgs += "--reload"
}

Write-Host "Starting backend at http://127.0.0.1:$Port"
Write-Host "Frontend should open at http://127.0.0.1:5500"
Write-Host "Press Ctrl+C to stop."
& .\.venv\Scripts\python.exe @uvicornArgs
