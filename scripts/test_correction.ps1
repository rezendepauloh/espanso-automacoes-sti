# Test script for Invoke-TextCorrection
. "c:\Users\User\AppData\Roaming\espanso\scripts\lib\utils.ps1"
. "c:\Users\User\AppData\Roaming\espanso\scripts\dicionario.ps1"

$testText = "ola, tudo bem? aqui e o paulo do mpms. vc pode ver o problema no pc com windows? tbm preciso do pdf do sajmp"
$result = Invoke-TextCorrection -Texto $testText -Dicionario $global:meuDicionario

Write-Host "Original: $testText"
Write-Host "Result:   $result"
