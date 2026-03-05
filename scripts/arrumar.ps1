# Força a saída do PowerShell para UTF-8 (corrige os acentos)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Pega o texto do clipboard (Raw para manter as quebras de linha)
$texto = Get-Clipboard -Raw

if (![string]::IsNullOrWhiteSpace($texto)) {
    # Transforma tudo em minúsculo primeiro
    $texto = $texto.ToLower()
    
    # Expressão regular para capitalizar a primeira letra de cada frase
    $texto = [regex]::Replace($texto, '(?:^|[.:!?]\s+)(\p{Ll})', { param($m) $m.Value.ToUpper() })
    
    # Escreve o resultado de volta para o Espanso
    Write-Host -NoNewline $texto
}