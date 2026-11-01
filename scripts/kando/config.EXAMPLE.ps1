# ==========================================
# CONFIGURAÇÕES LOCAIS (NÃO VAI PRO GITHUB)
# ==========================================

$userHome = if ($env:USERPROFILE) { $env:USERPROFILE } else { $HOME }

# Caminhos do OneDrive / Documentos
$pastaProvas = "$userHome/Provas"
$pastaSharePoint = "$userHome/Documentos SharePoint"
$pastaContratos = "$userHome/Documentos SharePoint/General/Contratos"
$planilhaChamados = "$userHome/Documentos SharePoint/Chamados/Chamados.xlsx"
$pastaAulas = "$userHome/Aulas"

# Atalhos
$sajmpAtalho = if ($IsLinux -or [System.Environment]::OSVersion.Platform -eq "Unix") {
    "$userHome/.local/share/applications/sajmp.desktop"
} else {
    "C:/ProgramData/Microsoft/Windows/Start Menu/Programs/SAJMP.lnk"
}

# Caminho credenciais
$espansoRoaming = if ($IsLinux -or [System.Environment]::OSVersion.Platform -eq "Unix") {
    "$userHome/.config/espanso"
} else {
    "$env:APPDATA/espanso"
}
$credenciais = "$espansoRoaming/scripts/kando/credenciais/credenciais.xml"

# Pasta de Scripts PowerShell
$pastaScripts1 = "$userHome/Devices analysis"
$pastaScripts2 = "$userHome/Remote cleanup"
$pastaScripts3 = "$userHome/Remote Remove Users from Hosts"
