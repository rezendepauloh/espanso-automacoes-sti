# Arquivo: arrumar.ps1
param(
    [string]$Origem = "Espanso"
)

# Importa utilitários e dicionário
. "$PSScriptRoot\..\lib\utils.ps1"
. "$PSScriptRoot\..\lib\dicionario.ps1"

Setup-Encoding

# Pega o texto do clipboard
$texto = Get-ClipboardText

if (![string]::IsNullOrWhiteSpace($texto)) {
    # Toda a inteligência foi movida para a biblioteca central
    $textoProcessado = Invoke-TextCorrection -Texto $texto -Dicionario $global:meuDicionario
    
    # Trata a saída baseada na origem
    Handle-Output -Texto $textoProcessado -Origem $Origem
}