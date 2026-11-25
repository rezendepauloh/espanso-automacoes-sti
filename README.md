# 🛸 Espanso, Kando & CopyQ — Automações STI (MPMS)

> **Suíte multiplataforma de produtividade, formulários dinâmicos nativos e automação de chamados técnicos para Windows 10/11 (`.NET 8 + WPF-UI Fluent Mica`) e Linux Pop!_OS COSMIC (`Rust + libcosmic`).**

---

## 🎯 Visão Geral

O **Espanso Automações STI** acelera o atendimento técnico da Secretaria de Tecnologia da Informação (MPMS) com expansões contextuais, formulários dinâmicos nativos, corretor linguístico com NLP e integração direta com o menu radial **Kando** e o **CopyQ**.

### Pilares Arquiteturais

1. **Interfaces Gráficas Nativas (Zero Electron, Zero `SendKeys()`):**
   - **Windows 10/11 (`gui/windows/`):** [`sti-forms.exe`](gui/windows/README.md) em **C# 12 (.NET 8) + WPF-UI 4.3 (Fluent Mica)** + **YamlDotNet**, com suporte nativo a clipboard `CF_HTML`, restauração de foco `HWND` e colagem via Win32 `SendInput`.
   - **Linux Pop!_OS / COSMIC (`gui/cosmic/`):** [`sti-forms`](gui/cosmic/README.md) em **Rust + `libcosmic`** (Wayland nativo), com fallback para [`form_runner.py`](scripts/lib/form_runner.py).
2. **Contrato Único de Formulários & Segurança (`.env` + `forms/*.yml`):**
   - Ambas as GUIs leem os mesmos esquemas YAML (`schema`, `uischema`, `data`, regras `SHOW`/`HIDE`) e interpolam variáveis sensíveis (ramais, equipes, destinos, URLs) a partir do arquivo local `.env` (veja [`.env.example`](.env.example)).
3. **Motor NLP & Limpeza de Texto:**
   - Correção ortográfica contextual com [spaCy](https://spacy.io/) (`pt_core_news_sm`) e mais de 340 siglas institucionais em [`scripts/lib/dicionario.json`](scripts/lib/dicionario.json).
   - Limpador inteligente de quebras de linha de PDFs (`limpa_pdf` nativo em C# no `--action` e em PowerShell).
4. **Sincronização em 1 Comando & Suíte de Testes:**
   - [`sync.sh`](sync.sh) no Linux e [`sync.ps1`](sync.ps1) no Windows compilam a GUI nativa, vinculam Espanso, fazem backup/atualização automática do **Kando** e reiniciam os serviços.

---

## ⚡ Gatilhos e Ações Disponíveis

| Gatilho Espanso | Ação Kando (`--action`) | Descrição |
| :--- | :--- | :--- |
| `:ola` | `ola` | Formulário mestre de atendimento inicial STI (BIOS, Lentidão, Telefonia, Material, Fotos, Domínio) |
| `:devolu` | `devolucao_chamado` | Notificação padronizada de devolução técnica de chamado/material |
| `:cel` | `celular` | Respostas padronizadas de suporte à telefonia móvel |
| `:transporte` | `transporte_urbano` | Solicitação de deslocamento urbano com sugestão automática de horário (`+30 min`) |
| `:transdevo` | `transporte_material` | Despacho de devolução/movimentação de materiais ao DMP |
| `:viagem` | `transporte_viagem` | Solicitação de transporte intermunicipal com cálculo de datas e comarcas |
| `:diaria` | `diaria_viagem` | Solicitação de diárias de viagem para equipe terceirizada |
| `;arrumar` | `ia_arrumar` | Corretor ortográfico/contextual do clipboard via spaCy + dicionário STI |
| `;maiuscula` / `;minuscula` | `maiuscula` / `minuscula` | Conversão rápida de caixa do clipboard |
| *(Kando / PS)* | `limpa_pdf` | Reconstituição de parágrafos copiados de PDFs jurídicos |
| `:analisar` / `:limpar` / `:deluser` | `analisador` / `manutencao` / `removeruser` | Disparo assíncrono de rotinas PowerShell administrativas (Windows) |

---

## 📁 Estrutura do Repositório

```text
.
├── config/                         # Configurações globais e por SO do Espanso
│   ├── default.yml                 # Atalhos globais (LEFT_ALT, CTRL+ALT+SPACE, clipboard_threshold: 0)
│   ├── linux.yml                   # Backend EVDEV e layout us-intl (Pop!_OS COSMIC)
│   └── windows.yml                 # Otimizações Windows 10/11
├── Docs/                           # Central unificada de documentação técnica
├── forms/                          # Esquemas JSON Schema / UI Schema YAML compartilhados
├── gui/
│   ├── cosmic/                     # GUI nativa Linux (Rust + libcosmic -> sti-forms)
│   └── windows/                    # GUI nativa Windows (.NET 8 + WPF-UI Fluent Mica -> sti-forms.exe)
│       ├── StiForms.sln            # Solution .NET 8 (App + xUnit Tests)
│       ├── StiForms/               # Aplicação WPF-UI + ActionRunner Win32
│       └── StiForms.Tests/         # Testes unitários xUnit do núcleo C#
├── icons/                          # Ícones do Kando e CopyQ
├── match/                          # Gatilhos do Espanso (usando %CONFIG%/scripts/...)
├── scripts/
│   ├── copyq/                      # Scripts JavaScript do CopyQ
│   ├── kando/                      # Integração Kando (calls/, helpers/, workspaces/, sync_kando_windows.py)
│   ├── lib/                        # Núcleo compartilhado (utils.py, utils.ps1, dicionario.json, form_runner.py)
│   ├── powershell/                 # Utilitários PowerShell (run_admin_script.ps1, limpa_pdf.ps1, etc.)
│   ├── python/                     # Despachantes e geradores HTML (dispatcher.py, diaria_viagem.py, etc.)
│   ├── tests/                      # Suíte de testes Python + PowerShell (run_all.py)
│   └── textos/                     # Templates HTML modulares
├── .env.example                    # Modelo de configuração local (sem dados sensíveis)
├── AGENTS.md                       # Diretrizes obrigatórias para agentes de IA
├── sync.ps1                        # Sincronizador Windows (Build C# + .env + Espanso + Kando)
└── sync.sh                         # Sincronizador Linux (Build Rust + .env + Espanso + Kando)
```

---

## 🚀 Sincronização e Instalação Rápida

### 🪟 Windows 10/11 (PowerShell)
```powershell
# Compilar sti-forms.exe, instalar em %LOCALAPPDATA%\Programs\StiForms\,
# criar .env (se faltar), fazer backup/migrar o Kando e reiniciar o Espanso:
pwsh -NoProfile -ExecutionPolicy Bypass -File sync.ps1 -Build
```
> Caso precise reverter a alteração do menu do Kando:
> ```powershell
> pwsh -NoProfile -ExecutionPolicy Bypass -File sync.ps1 -RestoreKando
> ```

### 🐧 Linux Pop!_OS / COSMIC (Bash)
```bash
# Compilar sti-forms (Rust + libcosmic), instalar em ~/.local/bin/,
# linkar ~/.config/espanso e Kando, e reiniciar o Espanso:
./sync.sh --build
```

---

## 🧪 Suíte de Testes Automatizados

### Python + PowerShell (Linux e Windows)
```powershell
# Windows:
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/tests/rodar_testes.ps1 -IncludeDotnet
```
```bash
# Linux / macOS:
python3 tests/run_all.py
```

### Testes Unitários C# (xUnit — Windows)
```powershell
dotnet test gui/windows/StiForms.sln
```

---

## 📚 Documentação Técnica (`Docs/`)

Consulte o índice completo em [`Docs/README.md`](Docs/README.md):
- [Plano de Migração GUI Nativa](Docs/arquitetura/plano_migracao_gui_nativa.md)
- [Portabilidade Linux & Windows (`%CONFIG%`)](Docs/arquitetura/portabilidade_linux_windows.md)
- [Motor de Formulários Dinâmicos (`sti-forms.exe` / `sti-forms`)](Docs/arquitetura/formularios_dinamicos_e_runner.md)
- [Guia de Sincronização (`sync.sh` & `sync.ps1`)](Docs/guias/sincronizacao_ambientes.md)
- [Suíte de Testes Automatizados](Docs/testes/suite_de_testes_automatizados.md)
