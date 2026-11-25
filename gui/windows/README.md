# 🪟 GUI Nativa Windows — C#

Este diretório está reservado para a futura interface gráfica nativa em **C#** para **Windows 10/11**, responsável por substituir o executável externo `EDF.exe` (Espanso Dynamic Forms).

## 📋 Responsabilidades Planejadas
- Compartilhar o mesmo contrato de entrada (`forms/*.yml` + variáveis do `.env`) e de saída (`===FIELD:...===` / JSON) definido para a versão Linux em [`gui/cosmic/`](../cosmic/README.md).
- Permitir validação local e suporte completo a todos os tipos de campos (`radio`, `textarea`, `checkbox`, `date`, regras `SHOW`/`HIDE`) sem depender de terceiros no Windows.

> Acompanhe o roadmap completo no [Plano de Migração](../../Docs/arquitetura/plano_migracao_gui_nativa.md).
