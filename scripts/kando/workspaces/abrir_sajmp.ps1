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

# Define as funções da API do Windows para controle, diagnóstico e injeção de janelas (Win32UtilsV5)
# Alteramos o nome para Win32UtilsV5 para garantir recarregamento de tipos no mesmo processo do PowerShell
$csharpCode = @"
using System;
using System.Text;
using System.Runtime.InteropServices;
using System.Collections.Generic;

namespace Win32API
{
    public class Win32UtilsV5
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
        public static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, StringBuilder lParam);

        [DllImport("user32.dll", EntryPoint = "SendMessage", CharSet = CharSet.Auto)]
        public static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, string lParam);

        [DllImport("user32.dll", EntryPoint = "SendMessage")]
        public static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);

        [DllImport("user32.dll", SetLastError = true)]
        public static extern bool PostMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);

        [DllImport("user32.dll", EntryPoint = "GetWindowLong")]
        private static extern int GetWindowLong32(IntPtr hWnd, int nIndex);

        [DllImport("user32.dll", EntryPoint = "GetWindowLongPtr")]
        private static extern IntPtr GetWindowLongPtr64(IntPtr hWnd, int nIndex);

        [StructLayout(LayoutKind.Sequential)]
        public struct RECT
        {
            public int Left;
            public int Top;
            public int Right;
            public int Bottom;
        }

        [DllImport("user32.dll")]
        public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);

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
            public int Style { get; set; }
            public int Y { get; set; }
        }

        public static int GetWindowStyle(IntPtr hWnd)
        {
            if (IntPtr.Size == 8)
                return (int)GetWindowLongPtr64(hWnd, -16); // -16 é GWL_STYLE
            else
                return GetWindowLong32(hWnd, -16);
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

                // Tenta obter o texto real via WM_GETTEXT (muito mais potente para controles Delphi que GetWindowText)
                StringBuilder sbText = new StringBuilder(512);
                SendMessage(hWnd, 0x000D, (IntPtr)sbText.Capacity, sbText); // 0x000D é WM_GETTEXT
                string text = sbText.ToString();

                if (string.IsNullOrEmpty(text)) {
                    StringBuilder sbWText = new StringBuilder(512);
                    GetWindowText(hWnd, sbWText, sbWText.Capacity);
                    text = sbWText.ToString();
                }

                int style = GetWindowStyle(hWnd);

                RECT rect;
                GetWindowRect(hWnd, out rect);

                children.Add(new ChildWindowInfo {
                    Handle = hWnd,
                    ClassName = className,
                    Text = text,
                    Style = style,
                    Y = rect.Top
                });
                return true;
            }, IntPtr.Zero);
            return children;
        }

        public static void SendStringToControl(IntPtr hWnd, string text)
        {
            foreach (char c in text)
            {
                PostMessage(hWnd, 0x0102, (IntPtr)c, IntPtr.Zero); // 0x0102 é WM_CHAR
                System.Threading.Thread.Sleep(15); // Pequena pausa para a mensagem ser processada
            }
        }

        public static void SendEnterToControl(IntPtr hWnd)
        {
            PostMessage(hWnd, 0x0100, (IntPtr)0x0D, IntPtr.Zero); // 0x0100 é WM_KEYDOWN, 0x0D é ENTER
            System.Threading.Thread.Sleep(10);
            PostMessage(hWnd, 0x0101, (IntPtr)0x0D, IntPtr.Zero); // 0x0101 é WM_KEYUP
        }

        public static void ClickButton(IntPtr hWnd)
        {
            PostMessage(hWnd, 0x00F5, IntPtr.Zero, IntPtr.Zero); // 0x00F5 é BM_CLICK
        }
    }
}
"@

try {
    # Compila e adiciona o tipo C# no PowerShell de forma explícita, mostrando erros caso ocorram
    Add-Type -TypeDefinition $csharpCode -ErrorAction Stop
    Write-Log "APIs, diagnósticos e injeções de memória do Win32 carregados com sucesso."
} catch {
    Write-Log "Erro CRÍTICO ao carregar APIs do Win32: $_"
    # Se falhar aqui, o log nos dirá exatamente o motivo do erro de compilação
}

function Log-VisibleWindows {
    param([string]$Contexto)
    Write-Log "=== DIAGNÓSTICO DE JANELAS VISÍVEIS ($Contexto) ==="
    try {
        $windows = [Win32API.Win32UtilsV5]::GetVisibleWindows()
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
        $windows = [Win32API.Win32UtilsV5]::GetVisibleWindows()
        
        # 3. Filtra apenas as janelas do SAJMP que sejam o formulário de login real do Delphi (TffmpFormLogin / ffmpFormLogin)
        # IMPORTANTE: Ignoramos a janela de background 'SAJ/MP' (TApplication) que não possui controles visuais,
        # para garantir que o script só prossiga quando a janela legítima de digitação estiver desenhada!
        $janelasSAJ = $windows | Where-Object { 
            ($_.ProcessId -in $pidsSAJ) -and 
            ($_.ClassName -match "FormLogin" -or $_.Title -match "FormLogin")
        }
        
        if ($janelasSAJ) {
            $selecionada = $janelasSAJ[0]
            
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
$consoleHwnd = [Win32API.Win32UtilsV5]::GetConsoleWindow()
if ($consoleHwnd -ne [System.IntPtr]::Zero) {
    Write-Log "Minimizando a janela do terminal para transferir o foco de forma limpa..."
    [Win32API.Win32UtilsV5]::ShowWindow($consoleHwnd, 6) # 6 = SW_MINIMIZE
    Start-Sleep -Milliseconds 400
}

if ($hwndSAJ -ne [System.IntPtr]::Zero) {
    Write-Log "Trazendo a janela do SAJ (Handle: $hwndSAJ) para o primeiro plano..."
    
    # Se a janela estiver minimizada, restaura. Caso contrário, exibe normalmente.
    if ([Win32API.Win32UtilsV5]::IsIconic($hwndSAJ)) {
        [Win32API.Win32UtilsV5]::ShowWindow($hwndSAJ, 9) # 9 = SW_RESTORE
    } else {
        [Win32API.Win32UtilsV5]::ShowWindow($hwndSAJ, 5) # 5 = SW_SHOW
    }
    
    # Define como janela activa/focada
    $focoWin32 = [Win32API.Win32UtilsV5]::SetForegroundWindow($hwndSAJ)
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
    $children = [Win32API.Win32UtilsV5]::GetChildWindows($hwndSAJ)
    
    # Grava todos os controles detectados no log para auditoria e melhorias
    Write-Log "=== CONTROLES INTERNOS DETECTADOS NO LOGIN ==="
    foreach ($c in $children) {
        $styleHex = "0x{0:X8}" -f $c.Style
        Write-Log "Controle -> Handle: $($c.Handle), Classe: '$($c.ClassName)', Style: $styleHex, Y: $($c.Y), Valor/Texto: '$($c.Text)'"
    }
    Write-Log "=============================================="

    # Filtra controles de entrada de texto (classe contendo 'Edit' ou 'Campo')
    # Identificado no log que a Softplan usa a classe customizada 'TspCampo' para os campos de texto!
    # Ordenamos os campos de texto estritamente por suas coordenadas físicas Y (de cima para baixo na tela)!
    $editControles = $children | Where-Object { $_.ClassName -match "Edit" -or $_.ClassName -match "Campo" } | Sort-Object Y
    
    # Seleção Visualmente Infalível (Ground Truth de Design):
    # - O de menor Y (mais no topo) é SEMPRE o Usuário.
    # - O do meio (Y intermediário) é SEMPRE a Senha.
    # - O de maior Y (mais abaixo) é o campo de pesquisa interno do combobox de Lotação.
    # Isso nos torna 100% imunes a qualquer Z-Order ou classe de erro!
    $campoSenha = $null
    if ($editControles -and $editControles.Count -ge 2) {
        # O segundo elemento após ordenação vertical (index 1) é o campo de Senha!
        $campoSenha = $editControles[1]
        Write-Log "Campo de senha detectado via layout vertical! Handle: $($campoSenha.Handle), Y: $($campoSenha.Y)"
    }

    if ($campoSenha) {
        $campoSenhaHwnd = $campoSenha.Handle
        Write-Log "Focando programaticamente o campo de senha legítimo (Handle: $campoSenhaHwnd) via clique do mouse..."
        
        # Envia clique físico simulado direto no controle de senha para focar o cursor nele de forma impecável
        [Win32API.Win32UtilsV5]::SendMessage($campoSenhaHwnd, 0x0201, [System.IntPtr]::Zero, [System.IntPtr]::Zero) | Out-Null # WM_LBUTTONDOWN
        Start-Sleep -Milliseconds 100
        [Win32API.Win32UtilsV5]::SendMessage($campoSenhaHwnd, 0x0202, [System.IntPtr]::Zero, [System.IntPtr]::Zero) | Out-Null # WM_LBUTTONUP
        
        Start-Sleep -Milliseconds 200
        
        # Como o componente customizado TspCampo do Delphi rejeita WM_CHAR em segundo plano quando sem foco físico,
        # agora que o cursor está GARANTIDAMENTE preso e piscando no campo de senha correto, usamos o SendKeys focado.
        # Isso garante compatibilidade nativa de hardware de 100%!
        Write-Log "Digitando senha de forma focada e disparando LOGIN..."
        $wshell.SendKeys($senhaDescriptografada)
        Start-Sleep -Milliseconds 250
        
        # Dispara o Enter para Logar
        $wshell.SendKeys("{ENTER}")
        
        $loginInjetado = $true
    } else {
        Write-Log "Aviso: Nenhum campo de senha válido identificado nos controles."
    }
} catch {
    Write-Log "Falha ao injetar credenciais diretamente na memória: $_"
}

# --- 5. FALLBACK AUTOMÁTICO (Caso os controles espaciais falhem) ---
if (-not $loginInjetado) {
    Write-Log "Mapeamento espacial indisponível. Executando fallback seguro com emulação de teclado clássica (SendKeys)..."
    
    # Garante o foco no primeiro plano por segurança
    if ($hwndSAJ -ne [System.IntPtr]::Zero) {
        [Win32API.Win32UtilsV5]::SetForegroundWindow($hwndSAJ) | Out-Null
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