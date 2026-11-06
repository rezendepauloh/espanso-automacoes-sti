# 🏛️ Arquitetura de Portabilidade Multiplataforma (Linux & Windows)

> **Diretriz de compatibilidade do ecossistema Espanso entre o ambiente Windows 10/11 (STI / MPMS) e o ambiente Linux (Pop!_OS COSMIC Wayland / X11).**

---

## 🎯 1. Filosofia de Design Multiplataforma

O projeto foi projetado para sincronização transparente via Git entre estações de trabalho de naturezas diferentes:
1. **Windows 10/11**: Utilizado na rede física do MPMS. Opera com binários executáveis de suporte (ex: `EDF.exe`), PowerShell e registro do Windows.
2. **Pop!_OS 22.04 / 24.04 (Linux)**: Utilizado em ambiente pessoal/remoto. Opera com Wayland/X11 (backend `EVDEV`), utilitários nativos em Python (`form_runner.py` via Tkinter/Zenity) e `bash`.

---

## ⚠️ 2. Atenção Crítica: Variável `%CONFIG%` no Linux e Windows

> [!WARNING]
> **COMPORTAMENTO DO ESPANSO AO EXPANDIR VARIÁVEIS DE CAMINHO EM `params.args`**  
> No Espanso (v2.x), dentro dos blocos `type: script` nos arquivos YAML de `match/*.yml`, existe uma diferença crucial de interpretação de variáveis de path dependendo da sintaxe utilizada.

### O Problema Encontrado:
- Se utilizarmos `$CONFIG/scripts/...`, no ambiente **Linux** o Espanso ou a shell pode expandir `$CONFIG`, porém no **Windows** o Espanso não substitui `$CONFIG` dentro do array `params.args`. Ele passa a string literal `"$CONFIG/scripts/..."`, fazendo o Python tentar abrir um arquivo inexistente:
  ```text
  python: can't open file 'C:\Users\...\AppData\Local\Programs\Espanso\$CONFIG\scripts\python\dispatcher.py': [Errno 2] No such file or directory
  ```
- Por esse motivo, todos os arquivos `match/*.yml` foram ajustados para utilizar a sintaxe oficial do Espanso:
  ```yaml
  vars:
    - name: resposta
      type: script
      params:
        args:
          - python
          - "%CONFIG%/scripts/python/dispatcher.py"
  ```

### 🔍 O que observar ao testar no Pop!_OS:
1. **Suporte a `%CONFIG%` no Linux**: O core em Rust do Espanso substitui `%CONFIG%` internamente pelo caminho de configuração (`~/.config/espanso`).
2. **Se no Pop!_OS o `%CONFIG%` não expandir ou falhar**:
   - Verifique o log do Espanso no Linux:
     ```bash
     espanso log
     ```
   - Caso o Espanso no Linux trate `%CONFIG%` literalmente em vez de expandir no seu build específico, consulte o registro da issue em [`Docs/issues/compatibilidade_config_espanso.md`](../issues/compatibilidade_config_espanso.md) para aplicar o fallback por despachante relativo ou variável de ambiente `ESPANSO_CONFIG_DIR`.

---

## 📐 3. Regras de Código para Separadores de Caminho

Para garantir que o código funcione em ambos os sistemas sem exceções:

1. **PowerShell**:
   - Sempre utilize barras normais `/` para inclusão e dot-sourcing:
     ```powershell
     # CORRETO:
     . "$PSScriptRoot/../lib/utils.ps1"
     
     # ERRADO:
     . "$PSScriptRoot\..\lib\utils.ps1"
     ```
2. **Python**:
   - Sempre manipule arquivos usando a biblioteca `pathlib.Path`:
     ```python
     from pathlib import Path
     base_dir = Path(__file__).resolve().parent.parent
     ```
3. **Invocação de Python em Subprocessos**:
   - Nunca use `subprocess.run(["python", ...])`. Utilize sempre `sys.executable` para que o mesmo interpretador do ambiente em execução seja reaproveitado.

