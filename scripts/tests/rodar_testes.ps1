# Arquivo: scripts/tests/rodar_testes.ps1
# Wrapper PowerShell para a Suíte Unificada de Testes do Espanso Automações STI
param(
    [switch]$IncludeDotnet
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$TestsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $TestsDir "../..")
$RunAllPy = Join-Path $TestsDir "run_all.py"

# Detecta interpretador Python real (ignorando o atalho falso da Microsoft Store em WindowsApps)
function Resolve-RealPython {
    foreach ($cmdName in @("python", "python3")) {
        $cmds = Get-Command $cmdName -All -ErrorAction SilentlyContinue
        foreach ($c in $cmds) {
            if ($c.Source -and ($c.Source -notlike "*\WindowsApps\*")) {
                return @{ Exe = $c.Source; Args = @() }
            }
        }
    }
    $pyLauncher = Get-Command "py" -ErrorAction SilentlyContinue
    if ($pyLauncher -and ($pyLauncher.Source -notlike "*\WindowsApps\*")) {
        return @{ Exe = $pyLauncher.Source; Args = @("-3") }
    }
    return $null
}

$pyInfo = Resolve-RealPython
if (-not $pyInfo) {
    Write-Host "ERRO: Interpretador Python real (python, python3 ou py) não encontrado no PATH." -ForegroundColor Red
    exit 1
}

& $pyInfo.Exe @($pyInfo.Args) "$RunAllPy"
$pyExit = $LASTEXITCODE

if ($IncludeDotnet -and $pyExit -eq 0) {
    $SlnPath = Join-Path $RepoRoot "gui/windows/StiForms.sln"
    if ((Test-Path $SlnPath) -and (Get-Command "dotnet" -ErrorAction SilentlyContinue)) {
        Write-Host "`n🧪 Executando testes xUnit da GUI Windows (.NET 8)..." -ForegroundColor Cyan
        & dotnet test "$SlnPath"
        exit $LASTEXITCODE
    }
}

exit $pyExit
