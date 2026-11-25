# 🏛️ Motor de Formulários Dinâmicos (`sti-forms` / `EDF.exe` / `form_runner.py`)

> **Engenharia de renderização de janelas de diálogo multiplataforma com suporte a `.env` e regras condicionais.**

---

## 🏗️ Como os Formulários Funcionam

Os esquemas em `forms/*.yml` definem `schema` (JSON Schema), `uischema` (layout e regras `SHOW`/`HIDE`), `data` (valores iniciais com suporte a `${VAR}` do `.env`) e `template`.

### 1. No Linux / Pop!_OS COSMIC (`gui/cosmic/` → `sti-forms`)
- A função `run_edf_form()` em [`scripts/lib/utils.py`](../../scripts/lib/utils.py) prioriza o binário nativo **`sti-forms`** (escrito em **Rust + `libcosmic`**).
- Ele lê o `.env` local (com fallback para `.env.example`), resolve listas `|` e defaults dinâmicos (`hora_hoje`), renderiza `text_input`, `text_editor`, `dropdown`, `radio`, checklists com `checkbox`, atalhos de data (`Hoje`/`Amanhã`) e regras `SHOW`/`HIDE` compostas.
- Caso o binário `sti-forms` ainda não esteja compilado/instalado, faz fallback transparente para [`scripts/lib/form_runner.py`](../../scripts/lib/form_runner.py) (GTK3 / Zenity).

### 2. No Windows (`EDF.exe` → futuro `gui/windows/` em C#)
- Atualmente utiliza `C:\Program Files\Espanso Dynamic Forms\EDF.exe` via `--form-config` (com `.temp_<form>.yml` gerado pelo `utils.py` quando há variáveis `.env` ou defaults dinâmicos).
- A futura interface nativa em **C#** em [`gui/windows/`](../../gui/windows/README.md) substituirá o `EDF.exe` mantendo o mesmo contrato de saída:
  ```text
  ===FIELD:nome===
  Valor digitado
  ===END===
  ```
