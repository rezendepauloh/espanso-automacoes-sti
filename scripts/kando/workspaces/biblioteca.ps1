function Limpar-Ambiente {
    Write-Host "Iniciando limpeza do ambiente..." -ForegroundColor Green -BackgroundColor Black

    # --- 1. SALVAR E FECHAR OFFICE ---
    Write-Host "Salvando e fechando documentos do Office de forma segura..." -ForegroundColor Cyan -BackgroundColor Black
    
    $codigoSalvarOffice = {
        # --- FECHAR EXCEL ---
        # Só tenta fazer algo se o processo do Excel existir
        if (Get-Process -Name "excel" -ErrorAction SilentlyContinue) {
            try {
                $excel = [System.Runtime.InteropServices.Marshal]::GetActiveObject("Excel.Application")
                Write-Host "Entrou no Excel" -ForegroundColor Cyan -BackgroundColor Black
                
                $excel.DisplayAlerts = $false 
                
                foreach ($wb in $excel.Workbooks) {
                    Write-Host "Vendo a planilha: $($wb.Name)" -ForegroundColor Cyan -BackgroundColor Black

                    if ([string]::IsNullOrEmpty($wb.Path)) {
                        $nome = "Planilha_Salva_$(Get-Date -Format 'yyyyMMdd_HHmmss').xlsx"
                        $caminho = Join-Path $env:USERPROFILE "Downloads\$nome"

                        Write-Host "Tentando salvar planilha nova em: $caminho" -ForegroundColor Cyan -BackgroundColor Black
                        $wb.SaveAs($caminho)
                        Write-Host "Planilha nova salva com sucesso!" -ForegroundColor Green -BackgroundColor Black
                    } else {
                        Write-Host "Salvando alterações na planilha existente..." -ForegroundColor Cyan -BackgroundColor Black
                        $wb.Save()
                        Write-Host "Planilha existente salva com sucesso!" -ForegroundColor Green -BackgroundColor Black
                    }
                }
                $excel.Quit()
                [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
            } catch { 
                Write-Host "Erro ao manipular o Excel: $_" -ForegroundColor Red -BackgroundColor Black
            }
        }

        # --- FECHAR WORD ---
        # Só tenta fazer algo se o processo do Word existir
        if (Get-Process -Name "winword" -ErrorAction SilentlyContinue) {
            try {
                $word = [System.Runtime.InteropServices.Marshal]::GetActiveObject("Word.Application")
                Write-Host "Entrou no Word" -ForegroundColor Cyan -BackgroundColor Black
                
                $word.DisplayAlerts = 0 
                
                foreach ($doc in $word.Documents) {
                    Write-Host "Vendo o documento: $($doc.Name)" -ForegroundColor Cyan -BackgroundColor Black

                    if ([string]::IsNullOrEmpty($doc.Path)) {
                        $nome = "Documento_Salvo_$(Get-Date -Format 'yyyyMMdd_HHmmss').docx"
                        $caminho = Join-Path $env:USERPROFILE "Downloads\$nome"
                        
                        Write-Host "Tentando salvar documento novo em: $caminho" -ForegroundColor Cyan -BackgroundColor Black
                        
                        # Salvando como DOCX (formato 16)
                        $doc.SaveAs2([string]$caminho, 16)
                        
                        Write-Host "Documento novo salvo com sucesso!" -ForegroundColor Green -BackgroundColor Black
                    } else {
                        Write-Host "Salvando alterações no documento existente..." -ForegroundColor Cyan -BackgroundColor Black
                        $doc.Save()
                        Write-Host "Documento existente salvo com sucesso!" -ForegroundColor Green -BackgroundColor Black
                    }
                }
                $word.Quit()
                [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
            } catch { 
                Write-Host "ERRO CRÍTICO NO WORD: $_" -ForegroundColor Red -BackgroundColor Black
            }
        }
    }

    # Executa o bloco acima usando o PowerShell nativo do Windows
    powershell.exe -NoProfile -ExecutionPolicy Bypass -Command $codigoSalvarOffice

    # --- 2. FECHAR PROCESSOS (ALIASES E ESCUDO FAMILIAR) ---
    $processos = [ordered]@{
        "msedge" = "Microsoft Edge"
        "msedgewebview2" = "Edge WebView2"
        "msedgedriver" = "Motor Selenium Edge"
        "firefox" = "Mozilla Firefox"
        "chrome" = "Google Chrome"
        "msteams" = "Microsoft Teams 01"
        "Teams" = "Microsoft Teams 02"
        "ms-teams" = "Microsoft Teams 03"
        "mmc" = "Active Directory (MMC)"
        "Microsoft.ConfigurationManagement" = "SCCM"
        "sajapp" = "SAJMP"
        "olk" = "Novo Outlook"
        "FoxitPDFEditor" = "Foxit PDF"
        "Notepad" = "Bloco de Notas"
        "Time" = "Relógio do Windows"
        "RemoteDesktopManager" = "Remote Desktop Manager"
        "WindowsTerminal" = "Windows Terminal"
        #"pwsh" = "PowerShell 7"
    }

    Write-Host "Gerando escudo de proteção (Script e Janela Pai)..." -ForegroundColor Cyan -BackgroundColor Black
    
    # Descobre quem somos nós ($meuPid) e qual o título do nosso terminal atual ($meuTitulo)
    $meuPid = $PID
    $meuPaiPid = (Get-CimInstance Win32_Process -Filter "ProcessId = $PID").ParentProcessId
    $meuTitulo = $Host.UI.RawUI.WindowTitle

    foreach ($chave in $processos.Keys) {
        $processosEncontrados = Get-Process -Name $chave -ErrorAction SilentlyContinue
        
        if ($processosEncontrados) {
            # Variável para evitar o "flood" (spam) de dezenas de mensagens iguais do WebView2
            $jaAvisou = $false 

            foreach ($proc in $processosEncontrados) {
                
                # A SUA IDEIA AQUI: O Escudo de Título da Janela!
                # Ele verifica se a janela tem o emoji com a palavra Modo, ou se é igual ao título atual
                $temTituloProtegido = ($proc.MainWindowTitle -and ($proc.MainWindowTitle -match "🛠️ Modo" -or $proc.MainWindowTitle -eq $meuTitulo))
                
                # ESCUDO: Se o processo na mira for o script atual, o pai, ou tiver o título sagrado, pula!
                if ($proc.Id -eq $meuPid -or $proc.Id -eq $meuPaiPid -or $temTituloProtegido) {
                    Write-Host "  -> Poupando o $($processos[$chave]) (Escudo de Título/PID ativado)." -ForegroundColor Cyan
                    continue
                }
                
                # Avisa na tela que achou o processo (apenas 1 vez por aplicativo, para o log ficar limpo)
                if (-not $jaAvisou) {
                    Write-Host "Processo $($processos[$chave]) encontrado. Fechando..." -ForegroundColor Yellow -BackgroundColor Black
                    
                    # Se for Edge ou WebView2, avisa só uma vez, porque eles abrem 50 de uma vez.
                    if ($chave -match "msedge") { $jaAvisou = $true }
                }

                # O TIRO SILENCIOSO: Mata o processo. Se ele já morreu em cascata, o SilentlyContinue esconde o erro vermelho!
                Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            }
        }
    }

    Write-Host "Apagando a memória de abas do Edge da última sessão..." -ForegroundColor Cyan
    # O Edge guarda o histórico de abas abertas nesta pasta 'Sessions' do perfil Default
    $pastaSessoes = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Sessions"

    if (Test-Path $pastaSessoes) {
      # Apaga todos os arquivos de sessão restaurada sem dó
      Remove-Item -Path "$pastaSessoes\*" -Recurse -Force -ErrorAction SilentlyContinue
    }

    # --- 3. EXPLORADOR DE ARQUIVOS (A OPÇÃO NUCLEAR) ---
    Write-Host "Limpando janelas do Explorador de Arquivos (Modo Nuclear)..." -ForegroundColor Cyan -BackgroundColor Black
    
    if (Get-Process -Name explorer -ErrorAction SilentlyContinue) {
        Write-Host "  -> Reiniciando o processo raiz (explorer.exe)..." -ForegroundColor Yellow -BackgroundColor Black
        
        # O tiro de misericórdia. Derruba a interface inteira do Windows e todas as pastas junto.
        Stop-Process -Name explorer -Force
        
        # Dá um tempo para o Windows recarregar a Barra de Tarefas e a Área de Trabalho sozinho
        Write-Host "  -> Aguardando a interface do Windows voltar..." -ForegroundColor DarkGray -BackgroundColor Black
        Start-Sleep -Seconds 3
        
        # Trava de segurança: Se por acaso o Windows 11 for preguiçoso e não recarregar a barra sozinho, o script empurra.
        if (-not (Get-Process -Name explorer -ErrorAction SilentlyContinue)) {
            Start-Process "explorer.exe"
            Start-Sleep -Seconds 2
        }
        
        Write-Host "  -> Explorador reiniciado e memória limpa com sucesso!" -ForegroundColor Green -BackgroundColor Black
    }


    # --- 4. SNIPER ANTI-TELEMETRIA (Otimização de Performance) ---
    Write-Host "Abatendo processos de Telemetria da Microsoft..." -ForegroundColor Cyan -BackgroundColor Black
    
    # 1. Mata o processo que consome Disco e CPU (CompatTelRunner)
    if (Get-Process CompatTelRunner -ErrorAction SilentlyContinue) {
        Write-Host "  -> Matando CompatTelRunner.exe..." -ForegroundColor Yellow -BackgroundColor Black
        Stop-Process -Name "CompatTelRunner" -Force -ErrorAction SilentlyContinue
    }

    # 2. Tenta parar o Serviço de Telemetria (DiagTrack)
    # Nota: Parar serviços geralmente exige que o PowerShell esteja rodando como Administrador.
    # O "SilentlyContinue" garante que, se não estiver como Admin, o script apenas ignora e segue a vida sem dar erro vermelho na tela.
    Stop-Service -Name "DiagTrack" -Force -ErrorAction SilentlyContinue
    
    Write-Host "  -> Telemetria neutralizada (dentro dos privilégios atuais)." -ForegroundColor Green -BackgroundColor Black

    Write-Host "Aguardando estabilização do sistema..." -ForegroundColor Green -BackgroundColor Black
    Start-Sleep -Seconds 2
}

function Abrir-PastasEmAbas {
    param (
        # Aceita um dicionário (chave = Nome pro Log, valor = Caminho da pasta)
        [Parameter(Mandatory=$true)]
        [System.Collections.IDictionary]$Pastas
    )

    if ($Pastas.Count -eq 0) { return }

    # Define o arquivo de log local da biblioteca (Resolvido erro de Definition!)
    $PastaBiblioteca = $CaminhoAtual
    if (-not $PastaBiblioteca) {
        try {
            $PastaBiblioteca = Split-Path -Parent $MyInvocation.MyCommand.ScriptSourcePath -ErrorAction SilentlyContinue
        } catch {}
    }
    if (-not $PastaBiblioteca) { $PastaBiblioteca = $PSScriptRoot }
    if (-not $PastaBiblioteca) { $PastaBiblioteca = "c:\Users\paulogoncalves\AppData\Roaming\espanso\scripts\kando\workspaces" }
    $caminhoLogPastas = Join-Path $PastaBiblioteca "log_pastas.log"

    # Cria/Limpa o arquivo de log para esta execução
    "--- Nova Execução do Abrir-PastasEmAbas ($(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')) ---" | Out-File -FilePath $caminhoLogPastas -Encoding utf8

    function Write-FolderLog {
        param([string]$Mensagem)
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
        $linhaLog = "[$timestamp] $Mensagem"
        Write-Host "[LOG] $Mensagem" -ForegroundColor Gray
        Add-Content -Path $caminhoLogPastas -Value $linhaLog
    }

    Write-FolderLog "Iniciando abertura de pastas em abas..."
    foreach ($p in $Pastas.Keys) {
        Write-FolderLog "Pasta agendada -> Chave: $p, Caminho: $($Pastas[$p])"
    }

    # Carrega utilitários de Foco do Win32
    $csharpFocus = @"
using System;
using System.Runtime.InteropServices;

namespace Win32API
{
    public class FocusUtils
    {
        [DllImport("user32.dll")]
        public static extern bool SetForegroundWindow(IntPtr hWnd);

        [DllImport("user32.dll")]
        public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    }
}
"@

    try {
        Add-Type -TypeDefinition $csharpFocus -ErrorAction SilentlyContinue
    } catch {}

    $wshell = New-Object -ComObject WScript.Shell

    # Extrai as chaves (os nomes/alias) para podermos usar um índice numérico
    $chaves = @($Pastas.Keys)

    # Passo 1: Abre a PRIMEIRA pasta (cria a janela base)
    $primeiraChave = $chaves[0]
    $primeiroCaminho = $Pastas[$primeiraChave]

    Write-FolderLog "Passo 1: Abrindo a primeira janela do Explorer para: $primeiroCaminho"
    Start-Process "explorer.exe" -ArgumentList "`"$primeiroCaminho`""
    
    # Monitoramento Inteligente do Carregamento da Primeira Janela
    $limiteEspera = 10
    $inicioEspera = Get-Date
    $janelaBasePronta = $false
    $hwndExplorer = [System.IntPtr]::Zero
    
    Write-FolderLog "Aguardando carregamento da janela mãe..."
    while (((Get-Date) - $inicioEspera).TotalSeconds -lt $limiteEspera) {
        $shell = New-Object -ComObject Shell.Application
        $windows = $shell.Windows()
        
        Write-FolderLog "Varrendo janelas do Explorer ativas (Total: $($windows.Count))..."
        $matchEncontrado = $false
        
        foreach ($win in $windows) {
            $winHwnd = "Desconhecido"
            $winTitle = "Sem Título"
            $winPath = "Sem Caminho"
            $winState = -1
            $winBusy = $false
            
            try { $winHwnd = $win.HWND } catch {}
            try { $winTitle = $win.LocationName } catch {}
            try { $winPath = $win.Document.Folder.Self.Path } catch {}
            try { $winState = $win.ReadyState } catch {}
            try { $winBusy = $win.Busy } catch {}
            
            Write-FolderLog "  -> Janela HWND: $winHwnd | Título: '$winTitle' | Caminho Detectado: '$winPath' | ReadyState: $winState | Busy: $winBusy"
            
            if ($winPath -and ($winPath.ToLower() -eq $primeiroCaminho.ToLower()) -and ($winState -eq 4) -and (-not $winBusy)) {
                Write-FolderLog "  [SUCESSO] Encontrou a correspondência exata para a janela mãe!"
                $janelaBasePronta = $true
                try {
                    $hwndExplorer = [System.IntPtr]$win.HWND
                } catch {
                    $hwndExplorer = [System.IntPtr]::Zero
                }
                $matchEncontrado = $true
                break
            }
        }
        
        if ($matchEncontrado) { break }
        Start-Sleep -Milliseconds 400
    }
    
    # Se falhar em capturar o HWND mas o explorer abriu, pegamos o primeiro HWND disponível do explorer
    if ($hwndExplorer -eq [System.IntPtr]::Zero) {
        $shell = New-Object -ComObject Shell.Application
        $windows = $shell.Windows()
        if ($windows.Count -gt 0) {
            try {
                $hwndExplorer = [System.IntPtr]($windows[0].HWND)
                Write-FolderLog "  -> HWND recuperado do primeiro item do Shell: $hwndExplorer"
            } catch {}
        }
    }

    if ($janelaBasePronta) {
        Write-Host "  -> $primeiraChave aberta e carregada! (HWND: $hwndExplorer)" -ForegroundColor Green -BackgroundColor Black
    } else {
        Write-Host "  -> $primeiraChave aberta (prosseguindo sem confirmação)..." -ForegroundColor DarkGray -BackgroundColor Black
        Write-FolderLog "Aviso: Janela mãe não confirmou carregamento completo no tempo limite. HWND: $hwndExplorer"
    }

    # Passo 2: Abre as pastas seguintes (se existirem)
    if ($chaves.Count -gt 1) {
        for ($i = 1; $i -lt $chaves.Count; $i++) {
            $chaveAtual = $chaves[$i]
            $caminhoAtual = $Pastas[$chaveAtual]

            Write-Host "  -> Preparando nova aba para: $chaveAtual..." -ForegroundColor Yellow -BackgroundColor Black
            Write-FolderLog "Passo 2.$($i) - Navegando para a aba '$chaveAtual' ($caminhoAtual)"

            # Força o foco físico e em primeiro plano na janela real do Explorer
            if ($hwndExplorer -ne [System.IntPtr]::Zero) {
                Write-FolderLog "Focando na janela real do Explorer (HWND: $hwndExplorer) via SetForegroundWindow..."
                [Win32API.FocusUtils]::ShowWindow($hwndExplorer, 9) | Out-Null # SW_RESTORE
                [Win32API.FocusUtils]::SetForegroundWindow($hwndExplorer) | Out-Null
            } else {
                Write-FolderLog "Aviso: HWND do Explorer não disponível. Usando AppActivate genérico..."
                $wshell.AppActivate("Explorador de Arquivos") | Out-Null
                $wshell.AppActivate("File Explorer") | Out-Null
            }
            Start-Sleep -Milliseconds 300

            # Envia Ctrl + T (Nova Aba)
            Write-FolderLog "Enviando comando Ctrl+T (Nova Aba)..."
            $wshell.SendKeys("^t")
            
            # Procura pela nova aba aberta no Shell.Application para navegar nativamente
            $limiteAba = 2.5
            $inicioAba = Get-Date
            $novaAbaCom = $null
            
            Write-FolderLog "Aguardando nova aba registrar no COM..."
            while (((Get-Date) - $inicioAba).TotalSeconds -lt $limiteAba) {
                Start-Sleep -Milliseconds 200
                $shell = New-Object -ComObject Shell.Application
                $windows = $shell.Windows()
                
                foreach ($win in $windows) {
                    try {
                        # A nova aba deve estar na mesma janela ($hwndExplorer) e com o caminho de Início ou vazio
                        if ($hwndExplorer -ne [System.IntPtr]::Zero -and [System.IntPtr]$win.HWND -eq $hwndExplorer) {
                            $path = $win.Document.Folder.Self.Path
                            $title = $win.LocationName
                            if (-not $path -or ($path -eq "::{F874310E-B6B7-47DC-BC84-B9E6B38F5903}") -or ($title -eq "Início") -or ($title -eq "Home")) {
                                $novaAbaCom = $win
                                break
                            }
                        }
                    } catch {}
                }
                if ($novaAbaCom) { break }
            }

            if ($novaAbaCom) {
                Write-FolderLog "  [SUCESSO] Nova aba detectada no COM! Navegando nativamente para: $caminhoAtual"
                try {
                    $novaAbaCom.Navigate($caminhoAtual)
                } catch {
                    Write-FolderLog "  [ERRO] Falha ao navegar nativamente via COM: $_. Usando método SendKeys..."
                    $novaAbaCom = $null
                }
            }

            # Fallback caso não ache a nova aba via COM ou ocorra erro
            if (-not $novaAbaCom) {
                Write-FolderLog "  [FALLBACK] Usando método tradicional de simulação de teclas..."
                # Envia Ctrl + L (Focar na barra de endereço)
                Write-FolderLog "Enviando comando Ctrl+L (Focar barra de endereço)..."
                $wshell.SendKeys("^l")
                Start-Sleep -Milliseconds 400

                # Copia o caminho para a memória
                Write-FolderLog "Copiando caminho para a Área de Trabalho..."
                Set-Clipboard -Value $caminhoAtual

                # Envia Ctrl + V (Colar o caminho) e Enter (~)
                Write-FolderLog "Enviando Ctrl+V para colar e ENTER..."
                $wshell.SendKeys("^v")
                Start-Sleep -Milliseconds 300
                $wshell.SendKeys("~")
            }

            # Monitoramento Inteligente do Carregamento Real da nova aba antes de criar a próxima!
            $inicioEsperaAba = Get-Date
            $abaCarregada = $false
            
            Write-FolderLog "Aguardando carregamento da aba '$chaveAtual'..."
            while (((Get-Date) - $inicioEsperaAba).TotalSeconds -lt $limiteEspera) {
                $shell = New-Object -ComObject Shell.Application
                $windows = $shell.Windows()
                
                Write-FolderLog "Varrendo janelas do Explorer ativas (Total: $($windows.Count))..."
                $matchAbaEncontrado = $false
                
                foreach ($win in $windows) {
                    $winHwnd = "Desconhecido"
                    $winTitle = "Sem Título"
                    $winPath = "Sem Caminho"
                    $winState = -1
                    $winBusy = $false
                    
                    try { $winHwnd = $win.HWND } catch {}
                    try { $winTitle = $win.LocationName } catch {}
                    try { $winPath = $win.Document.Folder.Self.Path } catch {}
                    try { $winState = $win.ReadyState } catch {}
                    try { $winBusy = $win.Busy } catch {}
                    
                    Write-FolderLog "  -> Aba HWND: $winHwnd | Título: '$winTitle' | Caminho Detectado: '$winPath' | ReadyState: $winState | Busy: $winBusy"
                    
                    if ($winPath -and ($winPath.ToLower() -eq $caminhoAtual.ToLower()) -and ($winState -eq 4) -and (-not $winBusy)) {
                        Write-FolderLog "  [SUCESSO] Correspondência de aba carregada confirmada!"
                        $abaCarregada = $true
                        $matchAbaEncontrado = $true
                        break
                    }
                }
                
                if ($matchAbaEncontrado) { break }
                Start-Sleep -Milliseconds 400
            }

            if ($abaCarregada) {
                Write-Host "  -> $chaveAtual aberta e totalmente carregada!" -ForegroundColor Green -BackgroundColor Black
            } else {
                Write-Host "  -> $chaveAtual carregada (tempo limite atingido)..." -ForegroundColor DarkGray -BackgroundColor Black
                Write-FolderLog "Aviso: Aba '$chaveAtual' não confirmou o carregamento completo no tempo limite."
            }
            
            # Pequena pausa de estabilidade
            Start-Sleep -Milliseconds 300
        }
    }
    Write-FolderLog "Abertura de pastas concluída!"
}