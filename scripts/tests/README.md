# 🧪 Suíte de Testes Automatizados — Espanso Automações STI

Suíte de testes desenvolvida no padrão arquitetural unificado (idêntico ao do **Pop!_OS Workstation Setup**, **Paulo Investimentos** e **Sistema Concursos**).

Garante que qualquer alteração em regras do Espanso, formulários YAML, algoritmos de NLP, templates HTML ou scripts de automação ocorra com **regressão zero** e **100% de confiabilidade**.

---

## 🏗 Arquitetura e Estrutura de Pastas

```text
scripts/tests/
├── run_all.py                      # 🚀 Orquestrador e executor unificado ANSI colorido
├── rodar_testes.ps1                # 🐚 Wrapper para execução via PowerShell / Windows
├── test_library.ps1                # 📦 Suíte pura de asserções da biblioteca PowerShell
├── unit/                           # 🔧 Testes Unitários
│   ├── __init__.py
│   ├── test_cross_platform.py      # Diretrizes e validação multiplataforma (Linux/Windows)
│   ├── test_syntax.py              # Validação AST/Parser (Python, Bash, PowerShell, YAML, JSON)
│   ├── test_nlp_and_templates.py   # Testes de NLP, Spacy, dicionário, datas e comarcas
│   └── test_powershell_lib.py      # Execução e verificação das asserções do PowerShell via unittest
└── integration/                    # 🚀 Testes de Integração
    ├── __init__.py
    ├── test_forms_and_matches.py   # Coerência entre forms/*.yml, match/*.yml e templates
    └── test_kando_and_scripts.py   # Validação de chamadas Kando, gatilhos e configurações do Espanso
```

---

## ⚡ Como Executar os Testes

### 🐧 No Linux / Bash:
Execute diretamente o orquestrador unificado Python:
```bash
python3 scripts/tests/run_all.py
```
*(ou se estiver na pasta `scripts/tests`: `./run_all.py`)*

### 🪟 No Windows ou via PowerShell (`pwsh`):
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/tests/rodar_testes.ps1
```

---

## 📊 Suítes Cobertas

1. **🔧 Unitários (`unit/`)**:
   - `test_syntax.py`:
     - Compilação AST limpa de todos os scripts Python (`py_compile`).
     - Validação estática de sintaxe de todos os scripts Bash (`bash -n`).
     - Validação estática do AST de todos os scripts PowerShell via `Parser::ParseFile`.
     - Parsing rigoroso de todos os arquivos YAML (`forms/`, `match/`, `config/`).
     - Integridade e integridade do dicionário central `dicionario.json`.
   - `test_nlp_and_templates.py`:
     - Correção contextual com modelo NLP (`fix_text_with_ai`).
     - Expansão de siglas institucionais (MPMS, STI, SAJMP).
     - Formatação de datas e cálculo de dias úteis para viagens.
     - Pluralização e concatenação inteligente de comarcas.
     - Verificação física da existência de templates HTML de respostas rápidas e suporte a celular.
   - `test_powershell_lib.py`:
     - Validação de limpeza inteligente de PDFs (`Clean-PdfText`).
     - Validação de regras de substituição ortográfica do PowerShell (`Invoke-TextCorrection`).

2. **🚀 Integração (`integration/`)**:
   - `test_forms_and_matches.py`:
     - Integridade dos esquemas JSON/YAML (`schema` e `template`) de todos os formulários.
     - Mapeamento 1:1 entre placeholders Jinja2 e propriedades dos formulários.
     - Estrutura dos arquivos de regras do Espanso (`matches`).
     - Verificação de referências a scripts externos e formulários vinculados.
   - `test_kando_and_scripts.py`:
     - Validação do acionador de atalhos Wayland/Linux `chamar_gatilho.sh` (+x e sintaxe).
     - Verificação de que todos os atalhos disparados pelo Kando existem como gatilhos ativos no Espanso.
     - Validação das configurações multiplataforma do Espanso (`default.yml`, `linux.yml`, `windows.yml`).
