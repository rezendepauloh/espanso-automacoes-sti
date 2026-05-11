# Arquivo: rodar_testes.ps1
# Orquestrador central da suíte de testes unitários STI

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$CaminhoScripts = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) ".."

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "          ORQUESTRADOR DE TESTES UNITÁRIOS" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Diretório de scripts: $CaminhoScripts" -ForegroundColor Gray

$todosPassaram = $true

# -------------------------------------------------------------
# 🐍 1. EXECUTA TESTES PYTHON (NLP & TEMPLATES)
# -------------------------------------------------------------
Write-Host "`r`n[PYTHON] Executando testes unitários..." -ForegroundColor White
$caminhoPyTest = Join-Path $CaminhoScripts "tests\test_nlp_and_templates.py"

if (Test-Path $caminhoPyTest) {
    # Altera Cwd para a pasta de testes para evitar problemas de path relativo
    $processInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processInfo.FileName = "python"
    $processInfo.Arguments = "`"$caminhoPyTest`" -v"
    $processInfo.RedirectStandardOutput = $false
    $processInfo.RedirectStandardError = $false
    $processInfo.UseShellExecute = $false
    $processInfo.CreateNoWindow = $false
    
    $process = [System.Diagnostics.Process]::Start($processInfo)
    $process.WaitForExit()
    
    if ($process.ExitCode -eq 0) {
        Write-Host "[🐍 PYTHON] SUCESSO - Todos os testes unitários Python passaram!" -ForegroundColor Green
    } else {
        Write-Host "[🐍 PYTHON] FALHA - Um ou mais testes Python falharam (Código de Saída: $($process.ExitCode))." -ForegroundColor Red
        $todosPassaram = $false
    }
} else {
    Write-Host "FALHA: Script de teste Python não encontrado em: $caminhoPyTest" -ForegroundColor Red
    $todosPassaram = $false
}

# -------------------------------------------------------------
# 🐚 2. EXECUTA TESTES POWERSHELL (LIBRARY & PDF)
# -------------------------------------------------------------
Write-Host "`r`n[POWERSHELL] Executando testes unitários..." -ForegroundColor White
$caminhoPsTest = Join-Path $CaminhoScripts "tests\test_library.ps1"

if (Test-Path $caminhoPsTest) {
    # Executa de forma isolada com Bypass
    $exitCode = 0
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$caminhoPsTest"
    if ($LASTEXITCODE -ne 0) {
         $exitCode = $LASTEXITCODE
    }
    
    if ($exitCode -eq 0) {
        Write-Host "[🐚 POWERSHELL] SUCESSO - Todos os testes unitários PowerShell passaram!" -ForegroundColor Green
    } else {
        Write-Host "[🐚 POWERSHELL] FALHA - Um ou mais testes PowerShell falharam (Código de Saída: $exitCode)." -ForegroundColor Red
        $todosPassaram = $false
    }
} else {
    Write-Host "FALHA: Script de teste PowerShell não encontrado em: $caminhoPsTest" -ForegroundColor Red
    $todosPassaram = $false
}

# -------------------------------------------------------------
# 📊 RELATÓRIO FINAL CONSOLIDADO
# -------------------------------------------------------------
Write-Host "`r`n==================================================" -ForegroundColor Cyan
if ($todosPassaram) {
    Write-Host "🎉 EXCELENTE: 100% de todas as ferramentas e corretores estão íntegros e funcionando perfeitamente! 🎉" -ForegroundColor Green
} else {
    Write-Host "❌ ATENÇÃO: Uma ou mais falhas foram detectadas na suíte de testes. Verifique as mensagens acima. ❌" -ForegroundColor Red
}
Write-Host "==================================================" -ForegroundColor Cyan

if ($todosPassaram) {
    exit 0
} else {
    exit 1
}
