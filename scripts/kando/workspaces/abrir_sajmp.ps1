# Força o PowerShell a encontrar o caminho real da pasta do script
$CaminhoAtual = Split-Path -Parent $MyInvocation.MyCommand.Path

# Importa a biblioteca (mesma pasta)
. "$CaminhoAtual\biblioteca.ps1"

# Importa o config (pasta anterior)
. "$CaminhoAtual\..\config.ps1"

Write-Host "Não mexa o mouse ou teclado até terminar!" -ForegroundColor Cyan -BackgroundColor Black

##########################
# SAJMP
##########################
Write-Host "Iniciando SAJMP..." -ForegroundColor Green -BackgroundColor Black
Start-Process $sajmpAtalho

Write-Host "Aguardando o SAJMP carregar a tela de login..." -ForegroundColor Green -BackgroundColor Black
# IMPORTANTE: Se o seu computador for muito rápido, pode diminuir esse tempo. 
# Se for mais lento para abrir o SAJ, aumente para 6 ou 7 segundos.
Start-Sleep -Seconds 8 

# Cria o objeto que simula o teclado
$wshell = New-Object -ComObject wscript.shell

# --- 4. Forçar o foco na janela do SAJMP ---
$processoSAJ = Get-Process saj -ErrorAction SilentlyContinue
if ($processoSAJ) {
    Write-Host "Puxando a janela do SAJMP para frente..." -ForegroundColor Yellow -BackgroundColor Black
    $wshell.AppActivate($processoSAJ.Id)
    Start-Sleep -Milliseconds 500 # Meio segundo para o Windows trazer a janela
}

Write-Host "Buscando credencial segura..." -ForegroundColor Green -BackgroundColor Black
$credSAJ = Import-Clixml -Path $credenciais
$senhaDescriptografada = $credSAJ.GetNetworkCredential().Password

Write-Host "Digitando credenciais..." -ForegroundColor Green -BackgroundColor Black

# Aperta TAB para pular do campo de Usuário para o campo de Senha
$wshell.SendKeys("{TAB}")
Start-Sleep -Milliseconds 200 # Pausa rapidinha imitando um humano

# Digita a senha (Lembre de colocar a sua senha aqui)
$wshell.SendKeys($senhaDescriptografada)
Start-Sleep -Milliseconds 200

# Aperta o Enter para logar
$wshell.SendKeys("{ENTER}")