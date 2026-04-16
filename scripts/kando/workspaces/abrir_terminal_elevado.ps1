# Força o PowerShell a encontrar o caminho real da pasta do script
$CaminhoAtual = Split-Path -Parent $MyInvocation.MyCommand.Path

# Importa a biblioteca (mesma pasta)
. "$CaminhoAtual\biblioteca.ps1"

# Importa o config (pasta anterior)
. "$CaminhoAtual\..\config.ps1"

$pastaRaiz = $env:USERPROFILE

$argWt = '-w new -d "' + $pastaRaiz + '" ; new-tab -d "' + $pastaScripts1 + '" ; new-tab -d "' + $pastaScripts2 + '" ; new-tab -d "' + $pastaScripts3 + '"'

Start-Process wt.exe -ArgumentList $argWt -Verb RunAs