# Arquivo: scripts/lib/utils.ps1
# Lógicas compartilhadas para scripts PowerShell

function Setup-Encoding {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
}

function Get-ClipboardText {
    return Get-Clipboard -Raw
}

function Set-ClipboardAndPaste {
    param([string]$Texto)
    
    if (![string]::IsNullOrWhiteSpace($Texto)) {
        Set-Clipboard -Value $Texto
        Start-Sleep -Milliseconds 150
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.SendKeys]::SendWait('^v')
    }
}

function Write-ToEspanso {
    param([string]$Texto)
    Write-Host -NoNewline $Texto
}

function Invoke-TextCorrection {
    param(
        [string]$Texto,
        [hashtable]$Dicionario
    )

    if ([string]::IsNullOrWhiteSpace($Texto)) { return $Texto }

    # 1. Limpeza básica e normalização de espaços
    $Texto = $Texto.Trim()
    $Texto = $Texto -replace '\s+', ' ' 

    # 2. Primeira passada: Tudo para minúsculo para garantir consistência
    $Texto = $Texto.ToLower()

    # 3. Capitalização após pontuação (Início, ., !, ?)
    # Regex: Início da string OU sinais seguidos de espaços, captura a primeira letra minúscula
    $Texto = [regex]::Replace($Texto, '(?:^|[.:!?]\s+)(\p{Ll})', { param($m) $m.Value.ToUpper() })

    # 4. Correção de Pontuação Colada (Vírgulas e pontos sem espaço depois)
    $Texto = $Texto -replace ',(?!\s)', ', '
    $Texto = $Texto -replace '\.(?!\s|$|[0-9])', '. ' # Não separa números (ex: 1.5)

    # 5. Aplicação do Dicionário
    if ($Dicionario) {
        # Ordena chaves por tamanho descendente para evitar que 'ana' estrague 'análise'
        $chaves = $Dicionario.Keys | Sort-Object Length -Descending
        foreach ($chave in $chaves) {
            $valor = $Dicionario[$chave]
            # \b garante que só mude a palavra exata, não partes de palavras
            $Texto = [regex]::Replace($Texto, "(?i)\b$chave\b", $valor)
        }
    }

    return $Texto
}

function Handle-Output {
    param(
        [string]$Texto,
        [string]$Origem
    )
    
    if ($Origem -eq "Kando") {
        Set-ClipboardAndPaste -Texto $Texto
    } 
    else {
        Write-ToEspanso -Texto $Texto
    }
}
