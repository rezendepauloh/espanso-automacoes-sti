# ==============================================================================
# Sincronizador de Ambiente Windows — Espanso + Kando + sti-forms.exe (.NET 8)
# ==============================================================================
# Uso:
#   pwsh -NoProfile -ExecutionPolicy Bypass -File sync.ps1 [-Build] [-SkipKando] [-NoRestart]
# ==============================================================================
[CmdletBinding()]
param(
    [switch]$Build,
    [switch]$SkipKando,
    [switch]$NoRestart,
    [switch]$RestoreKando
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$CsprojPath = Join-Path $RepoDir "gui/windows/StiForms/StiForms.csproj"
$InstallDir = Join-Path $env:LOCALAPPDATA "Programs/StiForms"
$ExePath = Join-Path $InstallDir "sti-forms.exe"
$EspansoDir = Join-Path $env:APPDATA "espanso"

Write-Host "🔄 Sincronizando Espanso Automações STI (Windows)..." -ForegroundColor Cyan

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

# 0. Modo de restauração rápida do Kando, se solicitado
if ($RestoreKando) {
    $syncPy = Join-Path $RepoDir "scripts/kando/sync_kando_windows.py"
    $pyInfo = Resolve-RealPython
    if (-not $pyInfo) {
        Write-Host "❌ Python real não encontrado no PATH." -ForegroundColor Red
        exit 1
    }
    & $pyInfo.Exe @($pyInfo.Args) "$syncPy" --repo-dir "$RepoDir" --restore
    exit $LASTEXITCODE
}

# 1. Compilar (opcional ou se ausente) e instalar sti-forms.exe em %LOCALAPPDATA%\Programs\StiForms\
if ($Build -or -not (Test-Path $ExePath)) {
    if (-not (Get-Command "dotnet" -ErrorAction SilentlyContinue)) {
        Write-Host "❌ .NET SDK não encontrado no PATH. Instale o .NET 8 SDK para compilar sti-forms.exe." -ForegroundColor Red
        exit 1
    }

    Write-Host "🛠️ Compilando sti-forms.exe (.NET 8 + WPF-UI Fluent Mica)..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null

    & dotnet publish "$CsprojPath" -c Release -r win-x64 --no-self-contained -o "$InstallDir"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Falha ao compilar sti-forms.exe." -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

if (Test-Path $ExePath) {
    Write-Host "✔ sti-forms.exe instalado em $ExePath" -ForegroundColor Green
} else {
    Write-Host "❌ Executável não encontrado após publish: $ExePath" -ForegroundColor Red
    exit 1
}

# 2. Garantir .env local (a partir do .env.example se não existir)
$EnvFile = Join-Path $RepoDir ".env"
$EnvExample = Join-Path $RepoDir ".env.example"
if (-not (Test-Path $EnvFile) -and (Test-Path $EnvExample)) {
    Copy-Item -Path $EnvExample -Destination $EnvFile
    Write-Host "📝 Arquivo .env criado a partir de .env.example (preencha com seus dados locais)." -ForegroundColor Yellow
} else {
    Write-Host "✔ Arquivo .env verificado" -ForegroundColor Green
}

# 3. Verificar vínculo do Espanso (%APPDATA%\espanso -> Repositório)
$ResolvedRepo = (Resolve-Path $RepoDir).Path.TrimEnd('\')
$ResolvedEspanso = if (Test-Path $EspansoDir) { (Resolve-Path $EspansoDir).Path.TrimEnd('\') } else { "" }

if ($ResolvedEspanso -ieq $ResolvedRepo) {
    Write-Host "✔ Espanso já aponta para $RepoDir" -ForegroundColor Green
} elseif (-not (Test-Path $EspansoDir)) {
    New-Item -ItemType Junction -Path $EspansoDir -Target $RepoDir | Out-Null
    Write-Host "✔ Junction criada: $EspansoDir -> $RepoDir" -ForegroundColor Green
} else {
    $Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $BackupEspanso = "${EspansoDir}.bak.${Stamp}"
    Move-Item -Path $EspansoDir -Destination $BackupEspanso
    New-Item -ItemType Junction -Path $EspansoDir -Target $RepoDir | Out-Null
    Write-Host "📦 Backup antigo salvo em $BackupEspanso e junction criada para $RepoDir" -ForegroundColor Green
}

# 4. Sincronizar Kando (%APPDATA%\Kando\menus.json) com backup automático
if (-not $SkipKando) {
    $SyncKandoPy = Join-Path $RepoDir "scripts/kando/sync_kando_windows.py"
    $pyInfo = Resolve-RealPython
    if ($pyInfo) {
        & $pyInfo.Exe @($pyInfo.Args) "$SyncKandoPy" --repo-dir "$RepoDir" --sti-forms-exe "$ExePath"
        if ($LASTEXITCODE -ne 0) {
            Write-Host "⚠️ Aviso ao sincronizar Kando (código $LASTEXITCODE)." -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️ Python real não encontrado no PATH; sincronização do Kando ignorada." -ForegroundColor Yellow
    }
}

# 5. Reiniciar Espanso em processo desacoplado (sem prender o terminal nos logs do daemon)
if (-not $NoRestart) {
    if (Get-Command "espanso" -ErrorAction SilentlyContinue) {
        Start-Process -FilePath "cmd.exe" -ArgumentList "/c espanso restart >nul 2>&1" -WindowStyle Hidden
        Write-Host "✔ Espanso reiniciando em segundo plano" -ForegroundColor Green
    }
}

Write-Host "🎉 Ambiente Windows sincronizado! Agora :ola no Espanso e os menus do Kando usam a GUI nativa WPF-UI Fluent Mica." -ForegroundColor Cyan
