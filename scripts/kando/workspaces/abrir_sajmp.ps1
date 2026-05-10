# Força o PowerShell a encontrar o caminho real da pasta do script
$CaminhoAtual = Split-Path -Parent $MyInvocation.MyCommand.Path

# Importa a biblioteca (mesma pasta)
. "$CaminhoAtual\biblioteca.ps1"

# Importa o config (pasta anterior)
. "$CaminhoAtual\..\config.ps1"

# Caminho do arquivo de log
$caminhoLog = Join-Path $CaminhoAtual "log_saj.log"

# Limpa/Cria o arquivo de log para esta nova execução
"--- Nova Execução do Script abrir_sajmp.ps1 ($(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')) ---" | Out-File -FilePath $caminhoLog -Encoding utf8

function Write-Log {
    param([string]$Mensagem)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    $linhaLog = "[$timestamp] $Mensagem"
    Write-Host $Mensagem -ForegroundColor Cyan
    Add-Content -Path $caminhoLog -Value $linhaLog
}

Write-Log "Iniciando script abrir_sajmp.ps1..."
Write-Log "Mensagem original: Não mexa o mouse ou teclado até terminar!"

# Define as funções da API do Windows para controle, diagnóstico e injeção de janelas (Win32UtilsV3)
# Alteramos o nome para Win32UtilsV3 para garantir recarregamento de tipos no mesmo processo do PowerShell
$csharpCode = @"
using System;
using System.Text;
using System.Runtime.InteropServices;
using System.Collections.Generic;

namespace Win32API
{
    public class Win32UtilsV3
    {
        [DllImport("user32.dll")]
        public static extern bool SetForegroundWindow(IntPtr hWnd);

        [DllImport("user32.dll")]
        public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

        [DllImport("user32.dll")]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool IsIconic(IntPtr hWnd);

        [DllImport("kernel32.dll")]
        public static extern IntPtr GetConsoleWindow();

        [DllImport("user32.dll")]
        private static extern bool EnumWindows(EnumWindowsProc enumProc, IntPtr lParam);

        [DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        private static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);

        [DllImport("user32.dll", CharSet = CharSet.Auto)]
        private static extern int GetClassName(IntPtr hWnd, StringBuilder lpClassName, int nMaxCount);

        [DllImport("user32.dll")]
        private static extern bool IsWindowVisible(IntPtr hWnd);

        [DllImport("user32.dll")]
        public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out int lpdwProcessId);

        [DllImport("user32.dll")]
        [return: MarshalAs(UnmanagedType.Bool)]
        private static extern bool EnumChildWindows(IntPtr window, EnumWindowProc callback, IntPtr lParam);

        [DllImport("user32.dll", EntryPoint = "SendMessage", CharSet = CharSet.Auto)]
        public static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, string lParam);

        [DllImport("user32.dll", EntryPoint = "SendMessage")]
        public static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);

        private delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
        private delegate bool EnumWindowProc(IntPtr hWnd, IntPtr lParam);

        public class WindowInfo
        {
            public IntPtr Handle { get; set; }
            public string Title { get; set; }
            public string ClassName { get; set; }
            public int ProcessId { get; set; }
        }

        public class ChildWindowInfo
        {
            public IntPtr Handle { get; set; }
            public string ClassName { get; set; }
            public string Text { get; set; }
        }

        public static List<WindowInfo> GetVisibleWindows()
        {
            List<WindowInfo> windows = new List<WindowInfo>();
            EnumWindows(delegate (IntPtr hWnd, IntPtr lParam) {
                if (IsWindowVisible(hWnd)) {
                    StringBuilder sbTitle = new StringBuilder(512);
                    GetWindowText(hWnd, sbTitle, sbTitle.Capacity);
                    string title = sbTitle.ToString();

                    if (!string.IsNullOrEmpty(title)) {
                        StringBuilder sbClass = new StringBuilder(256);
                        GetClassName(hWnd, sbClass, sbClass.Capacity);
                        
                        int pid = 0;
                        GetWindowThreadProcessId(hWnd, out pid);

                        windows.Add(new WindowInfo {
                            Handle = hWnd,
                            Title = title,
                            ClassName = sbClass.ToString(),
                            ProcessId = pid
                        });
                    }
                }
                return true;
            }, IntPtr.Zero);
            return windows;
        }

        public static List<ChildWindowInfo> GetChildWindows(IntPtr parent)
        {
            List<ChildWindowInfo> children = new List<ChildWindowInfo>();
            EnumChildWindows(parent, delegate (IntPtr hWnd, IntPtr lParam) {
                StringBuilder sbClass = new StringBuilder(256);
                GetClassName(hWnd, sbClass, sbClass.Capacity);
                string className = sbClass.ToString();

                StringBuilder sbText = new StringBuilder(512);
                GetWindowText(hWnd, sbText, sbText.Capacity);
                string text = sbText.ToString();

                children.Add(new ChildWindowInfo {
                    Handle = hWnd,
                    ClassName = className,
                    Text = text
                });
                return true;
            }, IntPtr.Zero);
            return children;
        }
    }
}
"@

try {
    Add-Type -TypeDefinition $csharpCode -ErrorAction SilentlyContinue
    Write-Log "APIs, diagnósticos e injeções de memória do Win32 carregados com sucesso."
} catch {
    Write-Log "Aviso ao carregar APIs do Win32: $_"
}

function Log-VisibleWindows {
    param([string]$Contexto)
    Write-Log "=== DIAGNÓSTICO DE JANELAS VISÍVEIS ($Contexto) ==="
    try {
        $windows = [Win32API.Win32UtilsV3]::GetVisibleWindows()
        if ($windows) {
            foreach ($win in $windows) {
                Write-Log "Janela -> Handle: $($win.Handle), PID: $($win.ProcessId), Classe: '$($win.ClassName)', Título: '$($win.Title)'"
            }
        } else {
            Write-Log "Nenhuma janela visível encontrada."
        }
    } catch {
        Write-Log "Erro ao listar janelas: $_"
    }
    Write-Log "========================================="
}

##########################
# SAJMP
##########################
Write-Log "Iniciando SAJMP executando o atalho: $sajmpAtalho"
Start-Process $sajmpAtalho

Write-Log "Aguardando o SAJMP carregar a tela de login..."

# --- 2. Aguardar o SAJMP de forma dinâmica (Com Verificação de Janelas Ativas) ---
$janelaPronta = $false
$limiteSegundos = 60 # Tempo limite seguro
$inicio = Get-Date
$processoSAJ = $null
$hwndSAJ = [System.IntPtr]::Zero

# Loga estado inicial dos processos e janelas
$processosIniciais = Get-Process -Name saj, sajapp -ErrorAction SilentlyContinue
if ($processosIniciais) {
    foreach ($p in $processosIniciais) {
        Write-Log "Diagnóstico Inicial -> Processo ativo: '$($p.Name)', PID: $($p.Id)"
    }
} else {
    Write-Log "Diagnóstico Inicial -> Nenhum processo 'saj' ou 'sajapp' ativo ainda."
}
Log-VisibleWindows "Instante Inicial"

while (((Get-Date) - $inicio).TotalSeconds -lt $limiteSegundos) {
    try {
        # 1. Obtém os IDs dos processos ativos com nome 'saj' ou 'sajapp'
        $pidsSAJ = @(Get-Process -Name saj, sajapp -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
        
        # 2. Busca todas as janelas visíveis na tela do usuário
        $windows = [Win32API.Win32UtilsV3]::GetVisibleWindows()
        
        # 3. Filtra apenas as janelas do SAJMP (pertencentes a esses PIDs) que sejam o formulário de login real do Delphi
        # Usamos classes e títulos descobertos via log diagnóstico: 'TffmpFormLogin', 'ffmpFormLogin' ou 'SAJ/MP'
        $janelasSAJ = $windows | Where-Object { 
            ($_.ProcessId -in $pidsSAJ) -and 
            ($_.ClassName -match "FormLogin" -or $_.Title -match "FormLogin" -or $_.Title -eq "SAJ/MP")
        }
        
        if ($janelasSAJ) {
            # Prioriza o formulário de login de fato (onde digitamos as credenciais) sobre a janela principal do Delphi (TApplication)
            $selecionada = $janelasSAJ | Where-Object { $_.ClassName -match "FormLogin" } | Select-Object -First 1
            if (-not $selecionada) {
                $selecionada = $janelasSAJ[0]
            }
            
            $hwndSAJ = $selecionada.Handle
            $processId = $selecionada.ProcessId
            
            Write-Log "Sucesso! Janela real de login detectada!"
            Write-Log "Detalhes -> Handle: $hwndSAJ, Classe: '$($selecionada.ClassName)', Título: '$($selecionada.Title)', Processo ID (PID): $processId"
            
            $processoSAJ = Get-Process -Id $processId -ErrorAction SilentlyContinue
            if ($processoSAJ) {
                Write-Log "Mapeamento correto do processo: '$($processoSAJ.Name)' (PID: $($processoSAJ.Id))"
            }
            
            $janelaPronta = $true
            break
        }
    } catch {
        Write-Log "Erro na listagem dinâmica de janelas do loop: $_"
    }
    
    # Mostra progresso no terminal
    Write-Host "." -NoNewline -ForegroundColor Green
    Start-Sleep -Seconds 1
}

if (-not $janelaPronta) {
    Write-Log "Aviso: A janela do SAJ não foi detectada pelo script após $limiteSegundos segundos."
    Log-VisibleWindows "Timeout de Espera"
}

# Cria o objeto que simula o teclado
$wshell = New-Object -ComObject wscript.shell

# --- 3. Forçar o foco na janela do SAJMP ---
# 3.1. Minimizar o terminal para evitar que ele fique na frente do SAJ
$consoleHwnd = [Win32API.Win32UtilsV3]::GetConsoleWindow()
if ($consoleHwnd -ne [System.IntPtr]::Zero) {
    Write-Log "Minimizando a janela do terminal para transferir o foco de forma limpa..."
    [Win32API.Win32UtilsV3]::ShowWindow($consoleHwnd, 6) # 6 = SW_MINIMIZE
    Start-Sleep -Milliseconds 400
}

if ($hwndSAJ -ne [System.IntPtr]::Zero) {
    Write-Log "Trazendo a janela do SAJ (Handle: $hwndSAJ) para o primeiro plano..."
    
    # Se a janela estiver minimizada, restaura. Caso contrário, exibe normalmente.
    if ([Win32API.Win32UtilsV3]::IsIconic($hwndSAJ)) {
        [Win32API.Win32UtilsV3]::ShowWindow($hwndSAJ, 9) # 9 = SW_RESTORE
    } else {
        [Win32API.Win32UtilsV3]::ShowWindow($hwndSAJ, 5) # 5 = SW_SHOW
    }
    
    # Define como janela activa/focada
    $focoWin32 = [Win32API.Win32UtilsV3]::SetForegroundWindow($hwndSAJ)
    Write-Log "Resultado do SetForegroundWindow via Win32: $focoWin32"
}

# 3.3. Garantia dupla com AppActivate usando o PID (se obtido)
if ($processoSAJ) {
    $focouApp = $false
    for ($i = 0; $i -lt 5; $i++) {
        if ($wshell.AppActivate($processoSAJ.Id)) {
            $focouApp = $true
            break
        }
        Start-Sleep -Milliseconds 200
    }
    Write-Log "Resultado do AppActivate via WScript (PID: $($processoSAJ.Id)): $focouApp"
} else {
    # Tenta AppActivate pelo Título da Janela caso o processo não tenha sido mapeado
    $focouTitulo = $wshell.AppActivate("SAJ - Sistema de Automação da Justiça")
    Write-Log "Resultado do AppActivate via WScript pelo título: $focouTitulo"
}

# Pausa de segurança de 1 segundo para o Windows estabilizar os campos de login
Write-Log "Aguardando 1 segundo para estabilização da interface..."
Start-Sleep -Seconds 1

Write-Log "Buscando credencial segura..."
$credSAJ = Import-Clixml -Path $credenciais
$senhaDescriptografada = $credSAJ.GetNetworkCredential().Password

$loginInjetado = $false

# --- 4. PREENCHIMENTO DIRETO NA MEMÓRIA DO CONTROLE (Ultra Seguro e Silencioso!) ---
try {
    Write-Log "Analisando controles internos da janela do SAJ (Child Windows)..."
    $children = [Win32API.Win32UtilsV3]::GetChildWindows($hwndSAJ)
    
    # Grava todos os controles detectados no log para auditoria e melhorias
    Write-Log "=== CONTROLES INTERNOS DETECTADOS NO LOGIN ==="
    foreach ($c in $children) {
        Write-Log "Controle -> Handle: $($c.Handle), Classe: '$($c.ClassName)', Valor/Texto: '$($c.Text)'"
    }
    Write-Log "=============================================="

    # Filtra controles de entrada de texto (classe contendo 'Edit' ou 'Campo')
    # Identificado no log que a Softplan usa a classe customizada 'TspCampo' para os campos de texto!
    $editControles = $children | Where-Object { $_.ClassName -match "Edit" -or $_.ClassName -match "Campo" }
    
    # Filtra o botão de login (classe contendo 'Button' ou 'Btn' E que tenha o texto contendo 'Entrar')
    # Identificado no log que a Softplan usa a classe 'TspButton' com o texto '&Entrar'!
    $botaoEntrar = $children | Where-Object { 
        ($_.ClassName -match "Button" -or $_.ClassName -match "Btn") -and 
        ($_.Text -match "Entrar")
    } | Select-Object -First 1

    # Em formulários de login do Delphi convencionais:
    # 1º controle 'Edit' = Usuário (já preenchido pelo sistema)
    # 2º controle 'Edit' = Senha
    if ($editControles -and $editControles.Count -ge 2) {
        $campoSenhaHwnd = $editControles[1].Handle # Seleciona o Handle da Senha
        
        Write-Log "Injetando a senha diretamente no controle de senha (Handle: $campoSenhaHwnd) via WM_SETTEXT..."
        
        # WM_SETTEXT = 0x000C (Seta o texto do controle de forma direta na memória do Windows)
        $resultadoSet = [Win32API.Win32UtilsV3]::SendMessage($campoSenhaHwnd, 0x000C, [System.IntPtr]::Zero, $senhaDescriptografada)
        
        # Se retornou sucesso (geralmente 1 para WM_SETTEXT)
        if ($resultadoSet -ne [System.IntPtr]::Zero) {
            Write-Log "Senha injetada na memória do controle com sucesso!"
            
            # Se identificamos o botão 'Entrar', disparamos o clique direto em background
            if ($botaoEntrar) {
                Write-Log "Disparando clique direto no botão 'Entrar' (Handle: $($botaoEntrar.Handle)) via BM_CLICK..."
                # BM_CLICK = 0x00F5 (Dispara o evento de clique físico em nível de API de janela)
                [Win32API.Win32UtilsV3]::SendMessage($botaoEntrar.Handle, 0x00F5, [System.IntPtr]::Zero, [System.IntPtr]::Zero) | Out-Null
            } else {
                # Se não achou o botão, dispara um ENTER diretamente na caixa de senha
                Write-Log "Botão 'Entrar' não mapeado. Disparando tecla ENTER na caixa de texto via WM_CHAR..."
                # WM_CHAR = 0x0102, 13 = ENTER (ASCII)
                [Win32API.Win32UtilsV3]::SendMessage($campoSenhaHwnd, 0x0102, [System.IntPtr]13, [System.IntPtr]::Zero) | Out-Null
            }
            $loginInjetado = $true
        }
    }
} catch {
    Write-Log "Falha ao injetar credenciais diretamente na memória: $_"
}

# --- 5. FALLBACK AUTOMÁTICO (Caso o SAJ use controles customizados sem Handle) ---
if (-not $loginInjetado) {
    Write-Log "Injeção de memória indisponível. Executando fallback seguro com emulação de teclado (SendKeys)..."
    
    # Garante o foco no primeiro plano por segurança
    if ($hwndSAJ -ne [System.IntPtr]::Zero) {
        [Win32API.Win32UtilsV3]::SetForegroundWindow($hwndSAJ) | Out-Null
    }
    
    Write-Log "Digitando credenciais via teclado virtual..."
    
    # Aperta TAB para pular do campo de Usuário para o campo de Senha
    $wshell.SendKeys("{TAB}")
    Start-Sleep -Milliseconds 250
    
    # Digita a senha
    $wshell.SendKeys($senhaDescriptografada)
    Start-Sleep -Milliseconds 250
    
    # Aperta Enter
    $wshell.SendKeys("{ENTER}")
}

Write-Log "Teclas enviadas / login disparado com sucesso! Execução concluída."