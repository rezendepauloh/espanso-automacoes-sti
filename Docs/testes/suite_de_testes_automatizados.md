# 🧪 Suíte de Testes Automatizados

> **Padrão de qualidade e testes contínuos para validação de sintaxe, formulários e integração cross-platform.**

---

## 🚀 Como Executar os Testes

### No Windows (PowerShell):
```powershell
pwsh scripts/tests/rodar_testes.ps1
```
Ou diretamente via Python:
```powershell
python scripts/tests/run_all.py
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
├── rodar_testes.ps1                       # Wrapper multiplataforma em PowerShell
├── test_library.ps1                       # Testes de funções puras do PowerShell (utils.ps1)
│
├── unit/                                  # Testes Unitários
│   ├── test_cross_platform.py             # Validação de barras /, caminhos %CONFIG% e SO
│   ├── test_python_syntax.py              # Compilação e AST de todos os .py
│   ├── test_pwsh_syntax.py                # Validação sintática de arquivos .ps1
│   ├── test_yaml_syntax.py                # Validação de parse de todos os .yml
│   └── test_json_syntax.py                # Validação de dicionario.json
│
└── integration/                           # Testes de Integração
    └── test_forms_and_matches.py          # Checagem de integridade schema vs template
```

