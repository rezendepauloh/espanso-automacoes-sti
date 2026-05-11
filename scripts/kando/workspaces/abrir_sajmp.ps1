# Força o PowerShell a encontrar o caminho real da pasta do script
$CaminhoAtual = Split-Path -Parent $MyInvocation.MyCommand.Path

# Importa a biblioteca (mesma pasta)
. "$CaminhoAtual\biblioteca.ps1"

# Importa o config (pasta anterior)
. "$CaminhoAtual\..\config.ps1"

function Write-Log {
    param([string]$Mensagem)
    Write-Host "[SAJMP] $Mensagem" -ForegroundColor Cyan
}

# Define as funções da API do Windows para controle e injeção de janelas (Win32UtilsV5)
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

                StringBuilder sbText = new StringBuilder(512);
                SendMessage(hWnd, 0x000D, (IntPtr)sbText.Capacity, sbText); // WM_GETTEXT
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
                PostMessage(hWnd, 0x0102, (IntPtr)c, IntPtr.Zero); // WM_CHAR
                System.Threading.Thread.Sleep(15);
            }
        }

        public static void SendEnterToControl(IntPtr hWnd)
        {
            PostMessage(hWnd, 0x0100, (IntPtr)0x0D, IntPtr.Zero); // WM_KEYDOWN
            System.Threading.Thread.Sleep(10);
            PostMessage(hWnd, 0x0101, (IntPtr)0x0D, IntPtr.Zero); // WM_KEYUP
        }

        public static void ClickButton(IntPtr hWnd)
        {
            PostMessage(hWnd, 0x00F5, IntPtr.Zero, IntPtr.Zero); // BM_CLICK
        }
    }
}
"@

try {
    Add-Type -TypeDefinition $csharpCode -ErrorAction Stop
} catch {
    Write-Log "Aviso ao carregar APIs de foco: $_"
}

##########################
# SAJMP
##########################
Write-Log "Iniciando o SAJMP..."
Start-Process $sajmpAtalho

Write-Log "Aguardando a tela de login..."

# --- 2. Aguardar o SAJMP de forma dinâmica ---
$janelaPronta = $false
$limiteSegundos = 60
$inicio = Get-Date
$processoSAJ = $null
$hwndSAJ = [System.IntPtr]::Zero

while (((Get-Date) - $inicio).TotalSeconds -lt $limiteSegundos) {
    try {
        $pidsSAJ = @(Get-Process -Name saj, sajapp -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
        $windows = [Win32API.Win32UtilsV5]::GetVisibleWindows()
        
        # Filtra apenas a janela legítima de login do Delphi
        $janelasSAJ = $windows | Where-Object { 
            ($_.ProcessId -in $pidsSAJ) -and 
            ($_.ClassName -match "FormLogin" -or $_.Title -match "FormLogin")
        }
        
        if ($janelasSAJ) {
            $selecionada = $janelasSAJ[0]
            $hwndSAJ = $selecionada.Handle
            $processoSAJ = Get-Process -Id $selecionada.ProcessId -ErrorAction SilentlyContinue
            $janelaPronta = $true
            break
        }
    } catch {}
    
    Write-Host "." -NoNewline -ForegroundColor Green
    Start-Sleep -Seconds 1
}

if (-not $janelaPronta) {
    Write-Log "Tempo limite excedido aguardando o SAJ."
    exit
}

# Cria o objeto que simula o teclado
$wshell = New-Object -ComObject wscript.shell

# --- 3. PREENCHIMENTO E LOGIN (MÉTODO CAMPEÃO 🏆) ---
$credSAJ = Import-Clixml -Path $credenciais
$senhaDescriptografada = $credSAJ.GetNetworkCredential().Password

$loginEfetuado = $false

try {
    # 1. Minimizar o terminal para expor a tela do SAJ de forma limpa
    $consoleHwnd = [Win32API.Win32UtilsV5]::GetConsoleWindow()
    if ($consoleHwnd -ne [System.IntPtr]::Zero) {
        [Win32API.Win32UtilsV5]::ShowWindow($consoleHwnd, 6) # SW_MINIMIZE
        Start-Sleep -Milliseconds 400
    }

    # 2. Trazer a janela de login do SAJ para o primeiro plano
    if ($hwndSAJ -ne [System.IntPtr]::Zero) {
        if ([Win32API.Win32UtilsV5]::IsIconic($hwndSAJ)) {
            [Win32API.Win32UtilsV5]::ShowWindow($hwndSAJ, 9) # SW_RESTORE
        } else {
            [Win32API.Win32UtilsV5]::ShowWindow($hwndSAJ, 5) # SW_SHOW
        }
        [Win32API.Win32UtilsV5]::SetForegroundWindow($hwndSAJ) | Out-Null
    }

    if ($processoSAJ) {
        $wshell.AppActivate($processoSAJ.Id) | Out-Null
    } else {
        $wshell.AppActivate("SAJ - Sistema de Automação da Justiça") | Out-Null
    }
    Start-Sleep -Milliseconds 500

    # Coleta controles para mapeamento de coordenadas Y
    $children = [Win32API.Win32UtilsV5]::GetChildWindows($hwndSAJ)
    $editControles = $children | Where-Object { $_.ClassName -match "Edit" -or $_.ClassName -match "Campo" } | Sort-Object Y
    
    $campoSenha = $null
    if ($editControles -and $editControles.Count -ge 2) {
        $campoSenha = $editControles[1] # O segundo campo vertical (do meio) é sempre a Senha
    }

    if ($campoSenha) {
        $campoSenhaHwnd = $campoSenha.Handle
        Write-Log "Efetuando o preenchimento de login..."
        
        # Envia clique mecânico simulado direto na caixa de senha para travar o cursor nela de forma infalível
        [Win32API.Win32UtilsV5]::SendMessage($campoSenhaHwnd, 0x0201, [System.IntPtr]::Zero, [System.IntPtr]::Zero) | Out-Null # WM_LBUTTONDOWN
        Start-Sleep -Milliseconds 100
        [Win32API.Win32UtilsV5]::SendMessage($campoSenhaHwnd, 0x0202, [System.IntPtr]::Zero, [System.IntPtr]::Zero) | Out-Null # WM_LBUTTONUP
        
        Start-Sleep -Milliseconds 200
        
        # Digita a senha no campo focado e envia ENTER
        $wshell.SendKeys($senhaDescriptografada)
        Start-Sleep -Milliseconds 250
        $wshell.SendKeys("{ENTER}")
        $loginEfetuado = $true
    }
} catch {
    Write-Log "Aviso: Falha no preenchimento coordenado."
}

# --- 4. FALLBACK CLÁSSICO CEGO (Segurança Dupla) ---
if (-not $loginEfetuado) {
    if ($hwndSAJ -ne [System.IntPtr]::Zero) {
        [Win32API.Win32UtilsV5]::SetForegroundWindow($hwndSAJ) | Out-Null
    }
    $wshell.SendKeys("{TAB}")
    Start-Sleep -Milliseconds 250
    $wshell.SendKeys($senhaDescriptografada)
    Start-Sleep -Milliseconds 250
    $wshell.SendKeys("{ENTER}")
}

Write-Host "[SAJMP] Login enviado com sucesso!" -ForegroundColor Green