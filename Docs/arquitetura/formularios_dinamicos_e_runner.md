# 🏛️ Motor de Formulários Dinâmicos (EDF vs form_runner.py)

> **Engenharia de renderização de janelas de diálogo multiplataforma.**

---

## 🏗️ Como os Formulários Funcionam

O Espanso por padrão conta com recursos básicos de formulário, mas o ecossistema do STI utiliza interfaces visuais ricas com validação, campos condicionais (`rule: effect: SHOW`) e listas suspensas.

### 1. No Windows (EDF.exe)
- O executável `C:\Program Files\Espanso Dynamic Forms\EDF.exe` é chamado via subprocess com a flag `--form-config`.
- Ele renderiza uma interface nativa rica baseada em schema JSON/YAML.
- A saída é emitida com delimitadores de bloco:
  ```text
  ===FIELD:nome===
  Valor digitado
  ===END===
  ```

### 2. No Linux / Pop!_OS (form_runner.py)
- Como o `EDF.exe` é um binário do Windows, a função `run_edf_form()` em [`scripts/lib/utils.py`](../../scripts/lib/utils.py) detecta automaticamente a ausência do executável no sistema.
- Em fallback transparente, invoca [`scripts/lib/form_runner.py`](../../scripts/lib/form_runner.py).
- O `form_runner.py` renderiza a interface nativa em Python (via Tkinter ou Zenity), coletando os dados do schema YAML e retornando o mesmo formato de dicionário para o despachante.

