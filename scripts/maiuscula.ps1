[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$texto = Get-Clipboard -Raw

if (![string]::IsNullOrWhiteSpace($texto)) {
    Write-Host -NoNewline $texto.ToUpper()
}