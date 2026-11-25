# 🧪 Suíte de Testes Automatizados

> **Padrão de qualidade e testes contínuos para validação de sintaxe, formulários, integração cross-platform e GUIs nativas.**

---

## 🚀 Como Executar os Testes

### No Windows (PowerShell):
```powershell
# Suíte completa (Python + PowerShell + xUnit C# .NET 8):
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/tests/rodar_testes.ps1 -IncludeDotnet

# Apenas suíte Python:
python scripts/tests/run_all.py

# Apenas suíte C# xUnit (gui/windows):
dotnet test gui/windows/StiForms.sln
```

### No Linux / Pop!_OS (Bash):
```bash
python3 tests/run_all.py
```

---

## 🗂️ Estrutura da Suíte de Testes

```text
scripts/tests/
├── run_all.py                             # Runner principal ANSI colorido com cronometragem
├── rodar_testes.ps1                       # Wrapper PowerShell (-IncludeDotnet para rodar xUnit)
├── test_library.ps1                       # Testes de funções puras do PowerShell (utils.ps1)
│
├── unit/                                  # Testes Unitários
│   ├── test_cross_platform.py             # Validação de barras /, caminhos %CONFIG% e SO
│   ├── test_syntax.py                     # Compilação AST Python, Bash, PowerShell, YAML e JSON
│   └── test_windows_gui_and_sync.py       # Validação de gui/windows, sync.ps1 e sync_kando_windows.py
│
└── integration/                           # Testes de Integração
    ├── test_forms_and_matches.py          # Checagem de integridade schema vs template e scripts
    └── test_kando_and_scripts.py          # Validação de chamadas Kando e configs Espanso

gui/windows/StiForms.Tests/                # Suíte xUnit (.NET 8)
└── StiFormsCoreTests.cs                   # EnvStore, FormLoader, RuleEngine, Validator, CF_HTML e PdfCleaner
```
