# 🦀 GUI Nativa Linux — Rust + `libcosmic`

Este diretório abrigará o aplicativo gráfico nativo em **Rust + `libcosmic`** para o ambiente **Pop!_OS / COSMIC Wayland**, responsável por substituir gradualmente o [`scripts/lib/form_runner.py`](../../scripts/lib/form_runner.py) e unificar as chamadas de formulário feitas pelo **Espanso** e pelo **Kando**.

## 📋 Responsabilidades Planejadas
- Ler os esquemas de formulário em `forms/*.yml` (`schema`, `uischema`, `data` e regras `SHOW`/`HIDE`).
- Interpolar variáveis sensíveis ou listas personalizadas a partir do arquivo `.env` na raiz do projeto (mantendo o repositório livre de dados reais hardcoded).
- Renderizar todos os controles nativos do COSMIC (`text_input`, `text_editor`, `dropdown`, `radio`, `checkbox`, listas editáveis e seletor de data).
- Retornar os campos preenchidos via `stdout` para os scripts Python e/ou atuar como executor direto para o Kando via `kando-cosmic-helper`.

> Acompanhe o progresso e os requisitos detalhados no [Plano de Migração](../../Docs/arquitetura/plano_migracao_gui_nativa.md).
