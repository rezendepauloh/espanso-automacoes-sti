# 🪟 GUI Nativa Windows — C# (.NET 8 + WPF-UI Fluent Mica)

Interface gráfica nativa para **Windows 10/11** em **C# 12 (.NET 8)** com **WPF-UI 4.3.0 (Fluent Mica)** e **YamlDotNet**, responsável por substituir tanto o `EDF.exe` (Espanso Dynamic Forms) quanto a cadeia legada de `PowerShell + SendKeys()` usada pelo **Kando**.

---

## 🏗️ Arquitetura (`gui/windows/`)

```text
gui/windows/
├── StiForms.sln                   # Solution .NET 8 (App + Testes)
├── StiForms/
│   ├── StiForms.csproj            # Output WinExe -> sti-forms.exe
│   ├── App.xaml(.cs)              # Roteador CLI (--form, --form-config, --action)
│   ├── MainWindow.xaml(.cs)       # Renderizador dinâmico Fluent Mica
│   ├── Models/FormSchema.cs       # Modelos YAML Schema / UI Schema
│   └── Services/
│       ├── EnvLoader.cs           # Leitor .env / .env.example e interpolação ${VAR}
│       ├── FormLoader.cs          # Loader de forms/*.yml + hora_hoje dinâmica
│       ├── RuleEngine.cs          # Motor SHOW/HIDE hierárquico (pai + filho)
│       ├── FormValidator.cs       # Validação required, integer, date e whitelist admin
│       ├── OutputFormatter.cs     # Saída ===FIELD:...=== / --json
│       ├── Win32Helper.cs         # GetForegroundWindow / SetForegroundWindow / SendInput
│       ├── ClipboardService.cs    # Clipboard nativo CF_HTML + UnicodeText
│       ├── PdfCleaner.cs          # Limpador de texto PDF nativo em C#
│       └── ActionRunner.cs        # Executor direto de ações do Kando (--action)
└── StiForms.Tests/                # Suíte xUnit para núcleo de formulários e Win32/HTML
```

---

## ⚡ Modos de Uso

### 1. Renderizador de Formulários (via Espanso / Python)
```powershell
sti-forms.exe --form-config C:\Users\...\espanso\forms\ola.yml
sti-forms.exe --form ola --dump-resolved
```
- Emite `===FIELD:<campo>=== ... ===END===` (ou JSON com `--json`) no `stdout` em UTF-8.
- Exit code `0` ao confirmar, `1` ao cancelar (`Esc` ou fechar janela).

### 2. Executor Direto do Kando (`--action`)
```powershell
sti-forms.exe --action ola --paste
sti-forms.exe --action ia_arrumar --paste
sti-forms.exe --action limpa_pdf --paste
sti-forms.exe --action analisador
```
- Captura o `HWND` da janela ativa antes de abrir o diálogo.
- Executa o script Python correspondente (ou `PdfCleaner` nativo), grava `CF_HTML` + texto puro na área de transferência, devolve o foco para a janela original e injeta `Ctrl+V` via Win32 `SendInput`.

---

## 🛠️ Compilação, Testes e Sincronização

```powershell
# Compilar, instalar em %LOCALAPPDATA%\Programs\StiForms\ e sincronizar Espanso + Kando:
pwsh -NoProfile -ExecutionPolicy Bypass -File sync.ps1 -Build

# Rodar testes unitários C# (xUnit):
dotnet test gui/windows/StiForms.sln
```
