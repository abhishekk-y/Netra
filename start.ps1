param([switch]$Local, [switch]$Install)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if ($Local) {
    $python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $python)) {
        python -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Python 3.12+ is required to create .venv.' }
    }
    $runArgs = @('scripts/run_local.py')
    if ($Install) { $runArgs += '--install' }
    & $python @runArgs
    exit $LASTEXITCODE
}
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw 'Install Docker Desktop, or run .\start.ps1 -Local -Install.' }
docker compose version
if ($LASTEXITCODE -ne 0) { throw 'Docker Compose v2 is required.' }
docker info --format '{{.ServerVersion}}'
if ($LASTEXITCODE -ne 0) { throw 'Start Docker Desktop, then retry. Local alternative: .\start.ps1 -Local -Install' }
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
docker compose up --build --detach --wait --wait-timeout 180
if ($LASTEXITCODE -ne 0) { throw 'Startup failed. Inspect docker compose logs.' }
Write-Host 'Netra: http://localhost:3000'
Write-Host 'API reference: http://localhost:8000/docs'
