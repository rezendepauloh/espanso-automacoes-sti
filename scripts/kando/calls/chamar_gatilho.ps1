# Arquivo: chamar_gatilho.ps1
# Script unificado e parametrizado para acionar atalhos do Espanso através do Kando
param(
    [Parameter(Mandatory=$true)]
    [string]$Gatilho
)

# Carrega a biblioteca nativa Windows Forms
Add-Type -AssemblyName System.Windows.Forms

# Simula o atalho CTRL + ALT + ESPAÇO para abrir a busca do Espanso (^ = CTRL, % = ALT)
[System.Windows.Forms.SendKeys]::SendWait('^% ')

# Aguarda 200 milissegundos para a barra de pesquisa aparecer
Start-Sleep -Milliseconds 200

# Digita o gatilho e aperta Enter para abrir o formulário
[System.Windows.Forms.SendKeys]::SendWait("$Gatilho{ENTER}")
