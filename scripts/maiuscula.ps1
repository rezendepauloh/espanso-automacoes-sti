# Cria uma variável que diz quem está chamando o script. 
# Se não informarmos nada, o padrão será "Espanso".
param(
    [string]$Origem = "Espanso"
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$texto = Get-Clipboard -Raw

if (![string]::IsNullOrWhiteSpace($texto)) {
    
    if ($Origem -eq "Kando") {
        # Se for o Kando: Salva no clipboard e aperta Ctrl+V sozinho
        Set-Clipboard -Value $texto.ToUpper()
        Start-Sleep -Milliseconds 150
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.SendKeys]::SendWait('^v')
    } 
    else {
        # Se for o Espanso: Imprime silenciosamente para o Espanso colar
        Write-Host -NoNewline $texto.ToUpper()
    }
}