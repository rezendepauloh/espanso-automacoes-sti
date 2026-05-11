# Chama a biblioteca do Windows para simular teclas
Add-Type -AssemblyName System.Windows.Forms

# Simula o atalho CTRL + ALT + ESPAÇO (^ = CTRL, % = ALT)
[System.Windows.Forms.SendKeys]::SendWait('^% ')

# Aguarda 200 milissegundos para a barra de pesquisa do Espanso aparecer
Start-Sleep -Milliseconds 200

# Digita o gatilho e aperta Enter para abrir o formulário
[System.Windows.Forms.SendKeys]::SendWait(':devolu{ENTER}')