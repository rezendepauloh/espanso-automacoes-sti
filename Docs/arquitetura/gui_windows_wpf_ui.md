# 🪟 Arquitetura da GUI Nativa Windows (`gui/windows/`)

> **Interface Fluent Mica em .NET 8 + C# 12 + WPF-UI 4.3.0, substituindo o `EDF.exe` e eliminando o `SendKeys()` do PowerShell no Kando.**

---

## 🎯 1. Motivação

Antes da migração:
- Os formulários do Espanso dependiam do binário externo `EDF.exe` (pesado e sem controle direto do código).
- Os atalhos do menu radial **Kando** disparavam `pwsh.exe` → `System.Windows.Forms.SendKeys('^% ')` → `Sleep 200ms` → barra de pesquisa do Espanso → Python → `EDF.exe`.

Com [`sti-forms.exe`](../../gui/windows/README.md):
- **Abertura nativa instantânea** com visual **Fluent Mica** (alinhado ao `AmbientesHub`).
- **Mesmo contrato** da versão Linux em Rust ([`gui/cosmic/`](../../gui/cosmic/README.md)): lê `forms/*.yml`, interpola `.env` e emite `===FIELD:...===` / `--json`.
- **Execução direta pelo Kando (`--action`)** com clipboard `CF_HTML` + texto puro e colagem via Win32 `SendInput`.

---

## 🧩 2. Fluxo Duplo (`Espanso` vs `Kando`)

### Fluxo A — Via Espanso (`:ola`, `:transporte`, etc.)
1. Espanso aciona `python "%CONFIG%/scripts/python/dispatcher.py"`.
2. [`scripts/lib/utils.py`](../../scripts/lib/utils.py) (`run_edf_form`) detecta `sti-forms.exe` em Windows (`_find_windows_forms_binary`) e o executa com `--form-config`.
3. `MainWindow` renderiza o formulário com regras `SHOW`/`HIDE` aninhadas, validação e atalhos (`Esc` cancela, `Enter` envia).
4. `sti-forms.exe` imprime `===FIELD:...=== ... ===END===` em UTF-8 no `stdout` e o Python devolve o HTML para o Espanso colar.

### Fluxo B — Via Kando (`sti-forms.exe --action <acao> --paste`)
1. [`Win32Helper`](../../gui/windows/StiForms/Services/Win32Helper.cs) captura imediatamente o `HWND` da janela em foco (`GetForegroundWindow()`).
2. [`ActionRunner`](../../gui/windows/StiForms/Services/ActionRunner.cs) executa o script Python alvo (ou [`PdfCleaner`](../../gui/windows/StiForms/Services/PdfCleaner.cs) nativo em C# para `limpa_pdf`).
3. [`ClipboardService`](../../gui/windows/StiForms/Services/ClipboardService.cs) grava simultaneamente **CF_HTML** (com offsets em bytes UTF-8 exatos para suportar acentos e emojis no Teams/Outlook) e **UnicodeText**.
4. `Win32Helper` restaura o foco para o `HWND` original (`SetForegroundWindow` + `AttachThreadInput`) e envia `Ctrl+V` via Win32 `SendInput`.

---

## 🔐 3. Segurança e Validações

- Variáveis pessoais e listas (`|`) ficam isoladas em `.env` (com fallback em `.env.example` para testes).
- Formulários administrativos (`analisador`, `manutencao`, `remove_profiles`) validam `computer_name`, `output_folder` e `users_to_purge` contra metacaracteres de shell antes da execução.
- Ações administrativas (`--action analisador`, `manutencao`, `removeruser`) disparam `executar_admin.py` sem sobrescrever o clipboard ou colar texto no editor ativo.
