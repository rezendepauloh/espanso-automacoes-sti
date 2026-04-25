# Arquivo: minuscula.ps1
param(
    [string]$Origem = "Espanso"
)

. "$PSScriptRoot\lib\utils.ps1"
Setup-Encoding

$texto = Get-ClipboardText

if (![string]::IsNullOrWhiteSpace($texto)) {
    $texto = $texto.ToLower()
    Handle-Output -Texto $texto -Origem $Origem
}