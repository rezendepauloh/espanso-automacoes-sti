# Arquivo: chamar_gatilho.ps1
# Script unificado e parametrizado para acionar atalhos do Espanso através do Kando (Windows e Linux)
param(
    [Parameter(Mandatory=$true)]
    [string]$Gatilho
)

if ($IsLinux -or [System.Environment]::OSVersion.Platform -eq "Unix") {
    # No Linux/Wayland, delega para o script Bash correspondente
    $BashScript = Join-Path $PSScriptRoot "chamar_gatilho.sh"
    if (Test-Path $BashScript) {
        & bash $BashScript $Gatilho
        exit $LASTEXITCODE
    }
}

# No Windows: Carrega a biblioteca nativa Windows Forms
Add-Type -AssemblyName System.Windows.Forms

# Simula o atalho CTRL + ALT + ESPAÇO para abrir a busca do Espanso (^ = CTRL, % = ALT)
[System.Windows.Forms.SendKeys]::SendWait('^% ')

# Aguarda 200 milissegundos para a barra de pesquisa aparecer
Start-Sleep -Milliseconds 200

# Digita o gatilho e aperta Enter para abrir o formulário
[System.Windows.Forms.SendKeys]::SendWait("$Gatilho{ENTER}")
