# Cria uma variável que diz quem está chamando o script. 
# Se não informarmos nada, o padrão será "Espanso".
param(
    [string]$Origem = "Espanso"
)

# Força a saída do PowerShell para UTF-8 (corrige os acentos)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Importa o dicionário combinando a pasta real do script com o nome do arquivo
. "$PSScriptRoot\dicionario.ps1"

# Pega o texto do clipboard (Raw para manter as quebras de linha)
$texto = Get-Clipboard -Raw

if (![string]::IsNullOrWhiteSpace($texto)) {
    
    $texto = $texto.ToLower()
    $texto = [regex]::Replace($texto, '(?:^|[.:!?]\s+)(\p{Ll})', { param($m) $m.Value.ToUpper() })
    
    $chavesOrdenadas = $global:meuDicionario.Keys | Sort-Object Length -Descending

    foreach ($chave in $chavesOrdenadas) {
        $valor = $global:meuDicionario[$chave]
        $texto = [regex]::Replace($texto, "(?i)\b$chave\b", $valor)
    }

    # ======== AQUI ENTRA A SUA IDEIA DO IF ========
    
    if ($Origem -eq "Kando") {
        # Se for o Kando: Salva no clipboard e aperta Ctrl+V sozinho
        Set-Clipboard -Value $texto
        Start-Sleep -Milliseconds 150
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.SendKeys]::SendWait('^v')
    } 
    else {
        # Se for o Espanso: Imprime silenciosamente para o Espanso colar
        Write-Host -NoNewline $texto
    }
}