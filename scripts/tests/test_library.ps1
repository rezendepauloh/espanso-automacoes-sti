# Arquivo: scripts/tests/test_library.ps1
# Suíte de testes unitários para a biblioteca de utilitários do PowerShell

# Importa as dependências relativas à pasta de testes
. "$PSScriptRoot\..\lib\utils.ps1"
. "$PSScriptRoot\..\lib\dicionario.ps1"

$global:testesFalhos = 0
$global:testesPassados = 0

function Assert-Equal {
    param(
        [object]$Actual,
        [object]$Expected,
        [string]$Message
    )
    if ($Actual -eq $Expected) {
        Write-Host "  [PASS] $Message" -ForegroundColor Green
        $global:testesPassados++
    } else {
        Write-Host "  [FAIL] $Message" -ForegroundColor Red
        Write-Host "    -> Esperado: '$Expected'" -ForegroundColor Yellow
        Write-Host "    -> Obtido:   '$Actual'" -ForegroundColor Yellow
        $global:testesFalhos++
    }
}

Write-Host "Iniciando Testes da Biblioteca PowerShell..." -ForegroundColor Cyan

# -------------------------------------------------------------
# TESTE 1: Carregamento do Dicionário JSON Centralizado
# -------------------------------------------------------------
Write-Host "`r`nExecutando Teste 1: Carregamento do Dicionário..." -ForegroundColor White
Assert-Equal -Actual $global:meuDicionario.Count -Expected 344 -Message "O dicionário centralizado deve conter as chaves mapeadas (Total: $($global:meuDicionario.Count))."
Assert-Equal -Actual $global:meuDicionario["mpms"] -Expected "MPMS" -Message "Chave 'mpms' deve mapear para 'MPMS'."
Assert-Equal -Actual $global:meuDicionario["sajmp"] -Expected "SAJMP" -Message "Chave 'sajmp' deve mapear para 'SAJMP'."

# -------------------------------------------------------------
# TESTE 2: Correção de Texto Ortográfica (Invoke-TextCorrection)
# -------------------------------------------------------------
Write-Host "`r`nExecutando Teste 2: Correção Ortográfica e Pontuação..." -ForegroundColor White
$original = "ola, tudo bem? aqui e o paulo do mpms. vc pode ver o pc com windows? tbm preciso do pdf do sajmp"
$resultado = Invoke-TextCorrection -Texto $original -Dicionario $global:meuDicionario

Assert-Equal -Actual ($resultado -like "*MPMS*") -Expected $true -Message "Deve capitalizar 'MPMS'."
Assert-Equal -Actual ($resultado -like "*Windows*") -Expected $true -Message "Deve capitalizar 'Windows'."
Assert-Equal -Actual ($resultado -like "*você*") -Expected $true -Message "Deve expandir 'vc' para 'você'."
Assert-Equal -Actual ($resultado -like "*também*") -Expected $true -Message "Deve expandir 'tbm' para 'também'."

# -------------------------------------------------------------
# TESTE 3: Limpeza Inteligente de PDF (Clean-PdfText)
# -------------------------------------------------------------
Write-Host "`r`nExecutando Teste 3: Limpeza de PDF..." -ForegroundColor White

# Caso A: Separação silábica com hífen na quebra de linha
$textoHifen = "O equipamen-`nto foi enviado à STI."
$limpoHifen = Clean-PdfText -Texto $textoHifen
Assert-Equal -Actual $limpoHifen -Expected "O equipamento foi enviado à STI." -Message "Deve juntar palavras cortadas por hífens."

# Caso B: Simples quebra de margem do PDF (deve juntar na mesma linha)
$textoMargem = "Esta é uma linha de texto`nque foi cortada pelo PDF de forma artificial."
$limpoMargem = Clean-PdfText -Texto $textoMargem
Assert-Equal -Actual $limpoMargem -Expected "Esta é uma linha de texto que foi cortada pelo PDF de forma artificial." -Message "Deve juntar linhas normais no mesmo parágrafo."

# Caso C: Novo parágrafo real (ponto final + letra maiúscula)
$textoParagrafos = "O processo foi deferido.`nO Promotor assinará digitalmente."
$limpoParagrafos = Clean-PdfText -Texto $textoParagrafos
# O Windows usa `r`n como quebra de linha padrão
$paragrafosEsperados = "O processo foi deferido.`r`n`r`nO Promotor assinará digitalmente."
Assert-Equal -Actual $limpoParagrafos -Expected $paragrafosEsperados -Message "Deve identificar parágrafo novo após ponto final e letra maiúscula."

# Caso D: Ignorar quebra de parágrafo em abreviações jurídicas
$textoAdv = "Nos termos do art.`n1º da referida lei."
$limpoAdv = Clean-PdfText -Texto $textoAdv
Assert-Equal -Actual $limpoAdv -Expected "Nos termos do art. 1º da referida lei." -Message "Deve ignorar pontuação de abreviação (art.) para evitar quebra de parágrafo artificial."

# -------------------------------------------------------------
# RESULTADO FINAL
# -------------------------------------------------------------
Write-Host "`r`n==================================================" -ForegroundColor White
if ($global:testesFalhos -eq 0) {
    Write-Host "SUCESSO: Todos os $($global:testesPassados) testes PowerShell passaram!" -ForegroundColor Green
} else {
    Write-Host "FALHA: $($global:testesFalhos) testes PowerShell falharam." -ForegroundColor Red
}
Write-Host "==================================================" -ForegroundColor White

# Retorna código de erro para o orquestrador se falhar
if ($global:testesFalhos -gt 0) {
    exit 1
} else {
    exit 0
}
