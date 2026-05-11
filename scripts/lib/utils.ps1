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

function Clean-PdfText {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Texto
    )

    if ([string]::IsNullOrWhiteSpace($Texto)) { return $Texto }

    # Padroniza as quebras de linha escondidas do PDF
    $Texto = $Texto -replace "`r", ""
    [string[]]$linhas = $Texto -split "`n"
    $textoLimpo = ""

    for ($i = 0; $i -lt $linhas.Count; $i++) {
        $linhaAtual = $linhas[$i].Trim()
        if ($linhaAtual -eq "") { continue }

        # Verifica se a palavra foi cortada no meio (separação silábica com hífen)
        $separacaoSilabica = $false
        if ($linhaAtual -match "[-–]$") {
            $linhaAtual = $linhaAtual.Substring(0, $linhaAtual.Length - 1)
            $separacaoSilabica = $true
        }

        $textoLimpo += $linhaAtual

        # Analisa a próxima linha para decidir se junta ou separa o parágrafo
        if ($i -lt ($linhas.Count - 1)) {
            $proximaLinha = $linhas[$i+1].Trim()
            
            if ($proximaLinha -eq "") {
                $textoLimpo += "`r`n`r`n"
                $i++ 
            } else {
                # 1. A linha atual termina com pontuação forte? (Ignorando abreviações jurídicas)
                $terminaComPontuacao = ($linhaAtual -match "[.;:!?]$") -and ($linhaAtual -notmatch "(?i)\b(art|arts|inc|fls|n|nº|doc|pg|pag|pág)\.$")
                
                # 2. A próxima linha começa com um marcador clássico de leis/editais?
                $regexMarcadores = "^(?i)(Art\.|§|Parágrafo|CAPÍTULO|TÍTULO|SEÇÃO|CONSIDERANDO|RESOLVE|O PROCURADOR|[IVXLCDM]+\s*[-–]|[a-z]\)|[A-Z]\s*[-–]|\d+\.)"
                $proximaComecaComMarcador = $proximaLinha -match $regexMarcadores
                $proximaComecaComMaiuscula = $proximaLinha -match "^[A-Z0-9]"
                
                # A MÁGICA DA DECISÃO:
                if (($terminaComPontuacao -and $proximaComecaComMaiuscula) -or $proximaComecaComMarcador) {
                    # É um novo parágrafo real! Separa com 2 quebras de linha.
                    $textoLimpo += "`r`n`r`n"
                } else {
                    # É só uma quebra de margem do PDF. Junta na mesma frase.
                    if (-not $separacaoSilabica) {
                        $textoLimpo += " "
                    }
                }
            }
        }
    }

    # Limpa espaços duplos que possam ter sobrado
    $textoLimpo = $textoLimpo -replace " {2,}", " "
    return $textoLimpo
}
