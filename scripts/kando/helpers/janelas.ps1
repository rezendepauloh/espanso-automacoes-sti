param(
    [string]$Acao
)

# Chama a mesma biblioteca que usamos no Espanso (100% segura e nativa)
Add-Type -AssemblyName System.Windows.Forms

# Pausa para o Kando sumir da tela (essencial)
Start-Sleep -Milliseconds 300

if ($Acao -eq "Maximizar") {
    # Simula ALT + ESPAÇO, espera um tiquinho, e aperta X (MaXimizar)
    [System.Windows.Forms.SendKeys]::SendWait('%{SPACE}')
    Start-Sleep -Milliseconds 50
    [System.Windows.Forms.SendKeys]::SendWait('x')
}
elseif ($Acao -eq "Minimizar") {
    # Simula ALT + ESPAÇO, e aperta N (MiNimizar)
    [System.Windows.Forms.SendKeys]::SendWait('%{SPACE}')
    Start-Sleep -Milliseconds 50
    [System.Windows.Forms.SendKeys]::SendWait('n')
}
elseif ($Acao -eq "Restaurar") {
    # Simula ALT + ESPAÇO, e aperta R (Restaurar)
    [System.Windows.Forms.SendKeys]::SendWait('%{SPACE}')
    Start-Sleep -Milliseconds 50
    [System.Windows.Forms.SendKeys]::SendWait('r')
}