# Força o PowerShell a encontrar o caminho real da pasta do script
$CaminhoAtual = Split-Path -Parent $MyInvocation.MyCommand.Path

# Importa a biblioteca (mesma pasta)
. "$CaminhoAtual/biblioteca.ps1"

# Importa o config (pasta anterior)
. "$CaminhoAtual/../config.ps1"

# pwsh.exe -WindowStyle Hidden -NoProfile -File "$env:APPDATA/espanso/scripts/kando/workspaces/pastas_estudos.ps1"
Write-Host "Não mexa o mouse ou teclado até terminar!" -ForegroundColor Cyan -BackgroundColor Black

# Montamos o dicionário (Alias = Caminho). 
# O [ordered] garante que a primeira da lista sempre será a janela mãe!
$minhasPastas = [ordered]@{
    "Download"   = "$env:USERPROFILE\Downloads"
    "Aulas"      = $pastaAulas
}

# Chamamos a função passando o nosso cardápio
Abrir-PastasEmAbas -Pastas $minhasPastas

# Carrega a biblioteca gráfica do Windows
Add-Type -AssemblyName System.Windows.Forms

# Monta o "window.alert" com Botão OK e Ícone de Informação (Azulzinho)
[System.Windows.Forms.MessageBox]::Show(
    "As pastas de Chamados foram carregadas com sucesso.", 
    "Automação Concluída", 
    [System.Windows.Forms.MessageBoxButtons]::OK, 
    [System.Windows.Forms.MessageBoxIcon]::Information
) | Out-Null