# Pega o texto copiado
$texto = Get-Clipboard -Raw
if ([string]::IsNullOrWhiteSpace($texto)) { return }

# Importa a biblioteca de utilitários
. "$PSScriptRoot\..\lib\utils.ps1"

# Limpa o texto usando a função centralizada
$textoLimpo = Clean-PdfText -Texto $texto

# Salva o texto perfeito e cola automaticamente
Set-ClipboardAndPaste -Texto $textoLimpo