# Força a saída do PowerShell para UTF-8 (corrige os acentos)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Importa o dicionário combinando a pasta real do script com o nome do arquivo
# O ponto e espaço no começo são obrigatórios!
. "$PSScriptRoot\dicionario.ps1"

# Pega o texto do clipboard (Raw para manter as quebras de linha)
$texto = Get-Clipboard -Raw

if (![string]::IsNullOrWhiteSpace($texto)) {
    
    $texto = $texto.ToLower()
    $texto = [regex]::Replace($texto, '(?:^|[.:!?]\s+)(\p{Ll})', { param($m) $m.Value.ToUpper() })
    
    # Usa a variável $global:meuDicionario que veio do outro arquivo
    $chavesOrdenadas = $global:meuDicionario.Keys | Sort-Object Length -Descending

    foreach ($chave in $chavesOrdenadas) {
        $valor = $global:meuDicionario[$chave]
        $texto = [regex]::Replace($texto, "(?i)\b$chave\b", $valor)
    }

    Write-Host -NoNewline $texto
    Set-Clipboard -Value $texto

    # Uma pausa minúscula de 150 milissegundos pro Windows registrar o novo texto
    Start-Sleep -Milliseconds 150 

    # Chama a biblioteca do Windows e aperta Ctrl + V (representado por ^v)
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.SendKeys]::SendWait('^v')
}