# Pega o texto copiado
$texto = Get-Clipboard -Raw
if ([string]::IsNullOrWhiteSpace($texto)) { return }

# Padroniza as quebras de linha escondidas do PDF
$texto = $texto -replace "`r", ""
[string[]]$linhas = $texto -split "`n"
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

# Salva o texto perfeito e cola automaticamente
Set-Clipboard -Value $textoLimpo
Start-Sleep -Milliseconds 250
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait('^v')