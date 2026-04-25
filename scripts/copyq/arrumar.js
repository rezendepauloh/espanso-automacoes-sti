// CopyQ Script: Arrumar Texto
// Este script chama o arrumar.ps1 para processar o item selecionado

var text = str(clipboard());
if (text) {
    // Detecta o usuário atual para o caminho ser universal (Casa/Trabalho)
    var home = Env("USERPROFILE");
    var scriptPath = home + "\\AppData\\Roaming\\espanso\\scripts\\arrumar.ps1";
    
    // Comando para rodar o PowerShell
    var command = "powershell.exe -WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -File \"" + scriptPath + "\" -Origem Kando";
    
    // Executa e o script PowerShell já cuidará de atualizar o clipboard e colar
    execute(command);
}
