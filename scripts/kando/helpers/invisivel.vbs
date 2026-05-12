Set WshShell = CreateObject("WScript.Shell")

' Pega a ação que o Kando vai mandar (Cascata, Minimizar, etc)
acao = WScript.Arguments(0)

' Caminho do seu script PowerShell (dinâmico e portável)
userProfile = WshShell.ExpandEnvironmentStrings("%USERPROFILE%")
scriptPs1 = userProfile & "\AppData\Roaming\espanso\scripts\kando\helpers\janelas.ps1"

' Monta o comando. O número 0 no final é o que garante a invisibilidade total!
comando = "powershell.exe -NoProfile -File """ & scriptPs1 & """ -Acao " & acao

WshShell.Run comando, 0, False