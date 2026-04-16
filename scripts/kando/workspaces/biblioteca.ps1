function Abrir-PastasEmAbas {
    param (
        # Aceita um dicionário (chave = Nome pro Log, valor = Caminho da pasta)
        [Parameter(Mandatory=$true)]
        [System.Collections.IDictionary]$Pastas
    )

    if ($Pastas.Count -eq 0) { return }

    Write-Host "Abrindo pastas de trabalho agrupadas em abas..." -ForegroundColor Cyan -BackgroundColor Black
    $wshell = New-Object -ComObject WScript.Shell

    # Extrai as chaves (os nomes/alias) para podermos usar um índice numérico
    $chaves = @($Pastas.Keys)

    # Passo 1: Abre a PRIMEIRA pasta (cria a janela base)
    $primeiraChave = $chaves[0]
    $primeiroCaminho = $Pastas[$primeiraChave]

    Start-Process "explorer.exe" -ArgumentList "`"$primeiroCaminho`""
    Write-Host "  -> $primeiraChave aberto" -ForegroundColor Cyan -BackgroundColor Black
    
    # Pausa generosa para a janela base carregar e ganhar o foco
    Start-Sleep -Seconds 4

    # Passo 2: Abre as pastas seguintes (se existirem)
    if ($chaves.Count -gt 1) {
        for ($i = 1; $i -lt $chaves.Count; $i++) {
            $chaveAtual = $chaves[$i]
            $caminhoAtual = $Pastas[$chaveAtual]

            # Envia Ctrl + T (Nova Aba)
            $wshell.SendKeys("^t")
            Start-Sleep -Seconds 2

            # Envia Ctrl + L (Focar na barra de endereço)
            $wshell.SendKeys("^l")
            Start-Sleep -Milliseconds 600

            # Copia o caminho para a memória (Zero erros de digitação!)
            Set-Clipboard -Value $caminhoAtual

            # Envia Ctrl + V (Colar o caminho)
            $wshell.SendKeys("^v")
            Start-Sleep -Milliseconds 600

            # Envia Enter
            $wshell.SendKeys("~")
            Write-Host "  -> $chaveAtual aberto" -ForegroundColor Cyan -BackgroundColor Black
            
            # Pausa antes da próxima aba
            Start-Sleep -Seconds 1
        }
    }
    
    # Pausa final para estabilização da interface
    Start-Sleep -Seconds 1
}