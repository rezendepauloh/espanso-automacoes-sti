# 🏛️ Motor de Formulários Dinâmicos (GUI Nativa Linux & Windows)

> **Engenharia de renderização de janelas de diálogo multiplataforma com contrato unificado sobre `forms/*.yml`.**

---

## 🏗️ Estratégia por Sistema Operacional

A função `run_edf_form()` em [`scripts/lib/utils.py`](../../scripts/lib/utils.py) seleciona automaticamente o renderizador nativo mais rápido disponível:

### 1. Windows 10/11 (`sti-forms.exe` → fallback `EDF.exe`)
1. **Prioridade 1 (`gui/windows/`):** [`sti-forms.exe`](gui_windows_wpf_ui.md) desenvolvido em **C# (.NET 8) + WPF-UI 4.3.0 (Fluent Mica)**.
   - Localizado via `STI_FORMS_BIN`, `%LOCALAPPDATA%\Programs\StiForms\sti-forms.exe`, `gui/windows/bin/sti-forms.exe` ou `PATH`.
   - Lê diretamente `forms/*.yml` + `.env` e devolve `===FIELD:<campo>=== ... ===END===` em UTF-8 no `stdout`.
2. **Fallback Legado:** Caso `sti-forms.exe` ainda não tenha sido compilado (`sync.ps1 -Build`), utiliza `C:\Program Files\Espanso Dynamic Forms\EDF.exe` (com arquivo `.temp_*.yml` resolvido pelo Python).

### 2. Linux / Pop!_OS COSMIC (`sti-forms` → fallback `form_runner.py`)
1. **Prioridade 1 (`gui/cosmic/`):** `sti-forms` desenvolvido em **Rust + `libcosmic`** (Wayland nativo).
   - Localizado em `gui/cosmic/target/release/sti-forms`, `~/.local/bin/sti-forms` ou `PATH`.
2. **Fallback:** [`scripts/lib/form_runner.py`](../../scripts/lib/form_runner.py) (GTK3 / PyGObject com fallback Zenity).

---

## 📋 Contrato Único de Entrada e Saída

- **Entrada:** `--form-config <caminho.yml>` ou `--form <nome>`
- **Saída (`stdout`):**
  ```text
  ===FIELD:nome===
  Valor digitado
  ===END===
  ```
- **Modo JSON (`--json`):** objeto JSON ordenado pelas chaves do schema.
- **Inspeção (`--dump-resolved`):** exibe defaults e variáveis `.env` já interpoladas sem abrir janela.
- **Códigos de saída:** `0` quando enviado (`Preencher`), diferente de `0` quando cancelado (`Esc` ou fechar janela).
