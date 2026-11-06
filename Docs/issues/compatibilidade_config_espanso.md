# 🚨 Registro de Compatibilidade: Resolução da Variável %CONFIG% no Espanso

> **Documento de rastreio de problema técnico e plano de contingência para execução de scripts no Linux (Pop!_OS) e Windows.**

---

## 📌 Contexto

Ao rodar o gatilho `:ola` no Windows após um `git pull`, o Espanso retornou a mensagem de erro:
```text
[Espanso]: An error occurred during rendering, please examine the logs for more information.
```

Ao inspecionar os logs em `%LOCALAPPDATA%\espanso\espanso.log`, identificou-se:
```text
python: can't open file 'C:\Users\paulogoncalves\AppData\Local\Programs\Espanso\$CONFIG\scripts\python\dispatcher.py': [Errno 2] No such file or directory
```

O binário do Espanso no Windows não expandiu a variável no estilo Unix (`$CONFIG`) passada como elemento do array `params.args`.

---

## 🛠️ Solução Aplicada

Substituição de todas as ocorrências de `$CONFIG` por `%CONFIG%` em todos os arquivos de gatilhos:
- `match/ola.yml`
- `match/celular.yml`
- `match/clipboard.yml`
- `match/admin_scripts.yml`
- `match/transporte_material.yml`
- `match/transporte_urbano.yml`
- `match/transporte_viagem.yml`

A documentação interna do motor do Espanso define `%CONFIG%` como o identificador nativo para interpolação da pasta de configuração do usuário em seus executáveis.

---

## 🧪 Plano de Validação no Pop!_OS (Linux)

Quando você estiver em casa no seu **Pop!_OS**, execute o seguinte procedimento de checagem:

1. Atualize o repositório com `git pull`.
2. Reinicie o Espanso:
   ```bash
   espanso restart
   ```
3. Abra um terminal ou editor de texto e digite:
   ```text
   :ola
   ```
4. Verifique se o formulário gráfico (`form_runner.py` / Tkinter) se abre normalmente.

### ⚠️ Caso ocorra erro de caminho no Pop!_OS:
Se o Espanso no Linux apresentar erro similar com `%CONFIG%`:
1. Abra os logs do Linux:
   ```bash
   espanso log
   ```
2. Caso o log acuse erro de arquivo não encontrado com `%CONFIG%`, a alternativa definitiva e 100% agnóstica a SO é utilizar um despachante genérico ou o parâmetro `cmd` em vez de `args`, ou invocar via script embutido no PATH, ou ler `ESPANSO_CONFIG_DIR`.
3. Notifique no chat que ajustaremos imediatamente a camada de chamada.

