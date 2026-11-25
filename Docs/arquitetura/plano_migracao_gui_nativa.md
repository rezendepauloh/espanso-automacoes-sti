# 🚀 Plano de Migração: GUI Nativa (`libcosmic` no Linux & C# no Windows)

> **Roteiro incremental para substituir o `form_runner.py` (GTK3/Zenity) por uma interface nativa em Rust + `libcosmic` no Pop!_OS/COSMIC, substituir futuramente o `EDF.exe` por uma GUI nativa em C# no Windows, unificar as chamadas do Kando e eliminar dados sensíveis hardcoded via `.env`.**

---

## 🎯 1. Objetivo e Estratégia (Migração Tranquila)

A lógica de negócio, formatação HTML, cálculo de datas, templates e o motor NLP com spaCy em `scripts/python/` e `scripts/lib/` **serão mantidos**. O foco da refatoração é substituir apenas a camada de interface gráfica e disparo:

| Plataforma | Motor Atual (Legado) | Novo Motor Nativo | Diretório |
| :--- | :--- | :--- | :--- |
| **Linux (Pop!_OS / COSMIC)** | [`scripts/lib/form_runner.py`](../../scripts/lib/form_runner.py) (GTK3 / Zenity) | App nativo em **Rust + `libcosmic`** | [`gui/cosmic/`](../../gui/cosmic/README.md) |
| **Windows 10/11** | `EDF.exe` + `SendKeys()` PowerShell | App nativo em **C# (.NET 8 + WPF-UI Fluent Mica)** | [`gui/windows/`](../../gui/windows/README.md) |

---

## 🔍 2. Diagnóstico do Estado Atual (Por que migrar?)

Problemas identificados na auditoria do código atual:

1. **Limitações do `form_runner.py`:**
   - Renderiza apenas `ComboBoxText` (todos os `enum`), `TextView` (`type: array`) e `Entry` simples.
   - Ignora configurações já presentes em `forms/*.yml`:
     - `options.format: radio` (`devolucao_chamado.yml`, `transporte_urbano.yml`)
     - `options.multi: true` / `rows` / `placeholder` (`celular.yml`, `transporte_viagem.yml`)
     - `format: date` (`transporte_urbano.yml`, `transporte_viagem.yml`, `diaria_viagem.yml`)
     - `type: integer` (`analisador.yml`)
     - `HorizontalLayout` e validação de campos `required`
   - **Bug de regras aninhadas em `ola.yml`:** `parse_uischema_rules` sobrescreve a regra do container pai (`tipo == "📦 Material"`) pela regra do controle filho (`tipo_material == "permanente"`) no campo `patrimonio`.
   - **Bug do `hora_hoje` no Linux:** em `scripts/lib/utils.py` (`run_edf_form`), o retorno para `run_gui_form` ocorre antes do bloco que arredonda o horário sugerido (+30 min) para o `transporte_urbano`.
2. **Fluxo Kando fragmentado fora do repositório:**
   - `scripts/kando/calls/chamar_gatilho.sh` delega para `~/.local/bin/chamar_espanso_acao` (fora do Git), que mistura Bash + Python inline + `kando-cosmic-helper` + `copyq` + `wl-copy` + `evdev`.
3. **Dados sensíveis e pessoais hardcoded no repositório:**
   - Nomes completos de servidores e terceirizados em `forms/transporte_viagem.yml`, `forms/diaria_viagem.yml` e `forms/transporte_urbano.yml`.
   - Ramais/locais/rotas hardcoded em templates e scripts Python (`transporte_urbano.py`, `transporte_viagem.py`, `diaria_viagem.py`).
   - Nomes de usuários Windows hardcoded em `scripts/python/master_fix_kando.py` e links pessoais em `scripts/kando/README.md`.
   - Interpolação direta de argumentos em string PowerShell em `scripts/powershell/run_admin_script.ps1`.

---

## 🧩 3. Mapeamento de Controles (`forms/*.yml` → `libcosmic`)

| Tipo "HTML" desejado | Declaração no YAML (`schema` / `uischema`) | Widget `libcosmic` |
| :--- | :--- | :--- |
| `<input text>` | `type: string` / `type: integer` | `widget::text_input` (com `placeholder`, filtro numérico e validação `required`) |
| `<textarea>` | `options.multi: true` | `widget::text_editor` |
| `<select>` | `enum: [...]` | `widget::dropdown` |
| `<input radio>` | `enum: [...]` + `options.format: radio` | `widget::radio` |
| `<input checkbox>` | `type: boolean` ou `type: array` selecionável | `widget::checkbox` (e checklist interativa com botão de adicionar/remover itens para `array`) |
| `<input date>` | `type: string` + `format: date` | Campo de data `DD/MM/YYYY` com atalhos rápidos (`Hoje`, `Amanhã`) convertendo para `YYYY-MM-DD` |
| Layout e Condições | `HorizontalLayout`, `VerticalLayout`, `rule` (`SHOW`/`HIDE`) | `widget::row` / `widget::column` com avaliação composta (pai + filho) |

---

## 🔐 4. Arquitetura de Segurança e Uso de `.env` com `.yml`

> **Dá certo usar `.env` com arquivos `.yml`?**  
> **Sim**, desde que a interpolação seja feita pelo **carregador do formulário** (o novo binário Rust no Linux, o futuro app C# no Windows e o `utils.py` durante a transição), pois parsers YAML puros (`yaml.safe_load` / `serde_yaml`) não expandem variáveis de ambiente sozinhos.

### Como funcionará o padrão `.env` + `.yml`:
1. O arquivo `.env` fica na raiz do projeto (já protegido pelo `.gitignore`) e o [`.env.example`](../../.env.example) fica versionado com dados fictícios (mocks).
2. Nos arquivos `forms/*.yml`, valores sensíveis ou listas de pessoas são substituídos por referências `${VAR}` (strings válidas em YAML, mantendo 100% de compatibilidade com os testes de sintaxe e schema em `scripts/tests/`):
   - **Strings simples:** `ramal: "${STI_RAMAL}"`
   - **Listas (`type: array`):** armazenadas no `.env` separadas por `|` (ex.: `STI_PASSAGEIROS_VIAGEM="Pessoa Exemplo 1|Pessoa Exemplo 2"`) e expandidas pelo runner para array de opções no momento de montar o formulário.
3. Scripts Python (`transporte_urbano.py`, `transporte_viagem.py`, `diaria_viagem.py`) também passarão a ler ramal e padrões do `.env` em vez de deixá-los hardcoded no código.
4. **Regra estrita para a nova GUI:**
   - Nunca gravar valores preenchidos pelos usuários em arquivos de log.
   - Validar identificadores (`computer_name`, IPs, nomes de usuário) na interface antes de enviar para scripts administrativos (`run_admin_script.ps1`).

---

## 🔗 5. Integração Unificada (Espanso + Kando)

- **Via Espanso (`:ola`, `:viagem`, `:cel`, etc.):**
  `match/*.yml` → script Python (`scripts/python/*.py`) → `utils.run_edf_form()` → chama o binário nativo em `gui/cosmic/` → usuário preenche → stdout devolvido ao Python → texto HTML colado pelo Espanso.
- **Via Kando (Menu Radial):**
  O Kando chama o wrapper versionado no repositório (ou o próprio binário Rust com flag de ação, ex.: `--action ola --paste`), que captura a janela em foco via `kando-cosmic-helper focused`, abre a mesma GUI nativa, executa o gerador Python, grava `text/html` e `text/plain` no clipboard Wayland/CopyQ, restaura o foco e injeta `Ctrl+V`.

---

## ✅ 6. Checklist Progressivo de Migração

Vá marcando cada item (`[x]`) somente após implementar e validar com `python3 tests/run_all.py` e teste real no desktop.

### Fase 0 — Fundação, Diretórios e Segurança (`.env`)
- [x] Documentar plano completo e checklist em `Docs/arquitetura/plano_migracao_gui_nativa.md`
- [x] Criar diretórios `gui/cosmic/` (Linux Rust) e `gui/windows/` (futuro Windows C#)
- [x] Criar `.env.example` na raiz com mocks seguros (sem dados reais)
- [x] Criar `.env` local (não versionado) com os dados reais da máquina/equipe
- [x] Implementar leitor de `.env` + interpolação `${VAR}` no `scripts/lib/utils.py` (para transição segura dos `.yml` e `.py`)
- [x] Migrar dados hardcoded de `forms/*.yml` (`passageiros`, `local`, `destino`, etc.) e `scripts/python/*.py` (ramais, URLs e contatos) para variáveis do `.env`
- [x] Sanitizar referências pessoais em `scripts/python/master_fix_kando.py`, `Docs/` e `README.md`s
- [x] Proteger `scripts/powershell/run_admin_script.ps1` contra injeção de argumentos

### Fase 1 — Estrutura Base do App Rust + `libcosmic` (`gui/cosmic/`)
- [x] Inicializar crate Cargo em `gui/cosmic/` (reaproveitando padrões de `workstation-hub`)
- [x] Implementar parser de `forms/*.yml` (`schema`, `uischema`, `data`, regras `SHOW`/`HIDE`) + interpolador de `.env`
- [x] Implementar saída compatível via `stdout` (`JSON` e/ou formato `===FIELD:...===` + `===END===`) e código de saída `0` (confirmar) / não-zero (cancelar)
- [ ] Avaliar tempo de abertura (`cold start`) no COSMIC Wayland (janela flutuante centralizada, foco inicial automático, `Esc` para cancelar)

### Fase 2 — Paridade Completa de Widgets e Regras
- [x] `<input text>` (`widget::text_input`) com `placeholder`, `type: integer` e validação `required`
- [x] `<textarea>` (`widget::text_editor`) para `options.multi: true`
- [x] `<select>` (`widget::dropdown`) para `enum`
- [x] `<input radio>` (`widget::radio`) para `options.format: radio`
- [x] `<input checkbox>` / listas `type: array` com seleção por checkbox + inclusão/remoção dinâmica de itens
- [x] `<input date>` (`format: date`) com atalhos rápidos (`Hoje` / `Amanhã`) e conversão `DD/MM/YYYY` ↔ `YYYY-MM-DD`
- [x] Motor de visibilidade `SHOW`/`HIDE` respeitando hierarquia pai + filho (corrigindo o caso `patrimonio` em `ola.yml`)
- [x] Suporte a `HorizontalLayout` (`widget::row`) e `VerticalLayout` (`widget::column`)
- [x] Cálculo dinâmico de `hora_hoje` (+30 min arredondado) funcionando no Linux para `transporte_urbano`

### Fase 3 — Integração Unificada com Espanso e Kando
- [x] Integrar `scripts/lib/utils.py` (`run_edf_form`) ao binário compilado do `gui/cosmic/` (mantendo fallback de segurança durante testes)
- [x] Trazer a lógica do `~/.local/bin/chamar_espanso_acao` para dentro do repositório (chamando o binário nativo + `kando-cosmic-helper` + clipboard Wayland/CopyQ)
- [x] Atualizar atalhos do Kando e `scripts/kando/calls/chamar_gatilho.sh` para o novo fluxo

### Fase 4 — Validação Formulário por Formulário (Linux)
- [x] `:ola` (`forms/ola.yml` — `dropdown` + `HorizontalLayout` + regras aninhadas `📦 Material` / `permanente`)
- [x] `:devolu` (`forms/devolucao_chamado.yml` — `radio`)
- [x] `:cel` (`forms/celular.yml` — `dropdown` + `textarea` + regra `SHOW` crítica)
- [x] `:transporte` (`forms/transporte_urbano.yml` — `radio` + `date` + `hora_hoje` + arrays `local`/`demandas`/`passageiros`)
- [x] `:transdevo` (`forms/transporte_material.yml` — array editável)
- [ ] `:viagem` (`forms/transporte_viagem.yml` — `date` + `textarea` + arrays)
- [x] `:diaria` (`forms/diaria_viagem.yml` — `date` + arrays)
- [ ] `:analisar`, `:limpar`, `:deluser` (`analisador.yml`, `manutencao.yml`, `remove_profiles.yml` — *scripts PowerShell exclusivos da rede Windows*)

### Fase 5 — Limpeza Final e Paridade Windows (`gui/windows/`)
- [ ] Remover `scripts/lib/form_runner.py` quando todos os formulários estiverem 100% validados no COSMIC
- [ ] Atualizar `scripts/tests/` com testes para o binário Rust (`cargo test`)
- [x] Implementar interface nativa em **C# (.NET 8 + WPF-UI Fluent Mica)** em `gui/windows/` (`sti-forms.exe`) substituindo `EDF.exe` e `SendKeys()` do Kando
- [x] Criar `sync.ps1` e `scripts/kando/sync_kando_windows.py` para build, backup e sincronização automática do Kando 3.0 no Windows
- [x] Criar suíte de testes xUnit em `gui/windows/StiForms.Tests/` e testes de integração Python em `scripts/tests/unit/test_windows_gui_and_sync.py`
