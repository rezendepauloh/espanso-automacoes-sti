# ====================================================================
# EXECUTOR MESTRE ADMINISTRATIVO (PowerShell)
# ====================================================================
# Recebe os parâmetros coletados pelo Espanso Dynamic Forms (EDF) via Python
# e executa os scripts correspondentes com privilégio elevado (RunAs).
# ====================================================================

param(
    [Parameter(Mandatory = $true)]
    [string]$ScriptType,

    [Parameter(Mandatory = $false)]
    [string]$computer_name,

    [Parameter(Mandatory = $false)]
    [string]$output_folder,

    [Parameter(Mandatory = $false)]
    [int]$timeout_sec,

    [Parameter(Mandatory = $false)]
    [string]$skip_major_data,

    [Parameter(Mandatory = $false)]
    [string]$users_to_purge
)

# 1) Determinar caminhos relativos de configuração
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ConfigPath = "$ScriptDir\..\kando\config.ps1"

# Importa as configurações do config.ps1 para resolver os caminhos das pastas de scripts
if (Test-Path $ConfigPath) {
    . $ConfigPath
} else {
    # Fallback se config.ps1 não estiver na pasta esperada
    $ConfigPathFallback = "$env:APPDATA\espanso\scripts\kando\config.ps1"
    if (Test-Path $ConfigPathFallback) {
        . $ConfigPathFallback
    } else {
        Write-Error "Arquivo de configuração 'config.ps1' não pôde ser localizado."
        exit 1
    }
}

# 2) Validar e definir caminhos dos scripts alvos
$targetFolder = ""
$targetScript = ""
$scriptArgs = ""

switch ($ScriptType) {
    "analisador" {
        $targetFolder = $pastaScripts1
        $targetScript = Join-Path $targetFolder "Analisador de Dispositivos de Maquina.ps1"
        
        # Constrói argumentos
        $argList = @()
        if ($computer_name) {
            $argList += "-ComputerName `"$computer_name`""
        }
        if ($output_folder) {
            $argList += "-OutputFolder `"$output_folder`""
        }
        if ($timeout_sec) {
            $argList += "-TimeoutSec $timeout_sec"
        }
        if ($skip_major_data -eq "Sim") {
            $argList += "-SkipMajorData"
        }
        $scriptArgs = $argList -join " "
    }

    "manutencao" {
        $targetFolder = $pastaScripts2
        $targetScript = Join-Path $targetFolder "MaintenanceAndCleanup.ps1"
        
        # Constrói argumentos
        if ($computer_name) {
            $scriptArgs = "-ComputerName `"$computer_name`""
        } else {
            $scriptArgs = "" # Local
        }
    }

    "removeruser" {
        $targetFolder = $pastaScripts3
        $targetScript = Join-Path $targetFolder "Remove-RemoteUserProfiles.ps1"
        
        # Processa e formata usuários para array nativo do PowerShell: @('user1', 'user2')
        if ($users_to_purge) {
            $cleanedUsers = $users_to_purge -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
            $formattedUsers = ($cleanedUsers | ForEach-Object { "'$_'" }) -join ","
            $scriptArgs = "-ComputerName `"$computer_name`" -UsersToPurge @($formattedUsers)"
        } else {
            $scriptArgs = "-ComputerName `"$computer_name`""
        }
    }

    default {
        Write-Error "Tipo de script administrativo '$ScriptType' desconhecido."
        exit 1
    }
}

# 3) Validar existência física do script alvo antes de prosseguir
if (-not (Test-Path $targetScript)) {
    [System.Windows.Forms.MessageBox]::Show("Script não encontrado em: $targetScript", "Erro STI", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error) | Out-Null
    exit 1
}

# 4) Preparar comando codificado em Base64 para evitar problemas com aspas e espaços
$CommandToRun = "& '$targetScript' $scriptArgs"
$Bytes = [System.Text.Encoding]::Unicode.GetBytes($CommandToRun)
$Base64 = [Convert]::ToBase64String($Bytes)

# 5) Executar no Windows Terminal (wt.exe) ou fallback para Powershell clássico em modo elevado (RunAs)
$argWt = "-w new -d `"$targetFolder`" pwsh.exe -NoExit -NoProfile -ExecutionPolicy Bypass -EncodedCommand $Base64"

try {
    # Tenta abrir no Windows Terminal (que o usuário usa) de modo elevado
    Start-Process wt.exe -ArgumentList $argWt -Verb RunAs -ErrorAction Stop
}
catch {
    # Fallback se o wt.exe falhar ou não estiver disponível no PATH, usando a janela clássica do PowerShell
    try {
        $argClassic = "-NoExit -NoProfile -ExecutionPolicy Bypass -EncodedCommand $Base64"
        Start-Process pwsh.exe -ArgumentList $argClassic -WorkingDirectory $targetFolder -Verb RunAs
    }
    catch {
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.MessageBox]::Show("Não foi possível iniciar o console elevado.`nErro: $_", "Erro de Execução", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error) | Out-Null
        exit 1
    }
}


