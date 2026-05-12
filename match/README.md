# 🎯 Diretório de Gatilhos e Atalhos (Matches)

Este diretório contém os arquivos de mapeamento de expansão de texto (`matches`) do **Espanso**. É aqui que definimos os gatilhos (triggers) que o usuário digita (ex: `:ola`) e os associamos a textos estáticos ou a chamadas de scripts Python/PowerShell.

## 📄 Arquivos

### [base.yml](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/match/base.yml)
* **Função**: Gatilhos estáticos globais do Espanso.
* **O que faz**: Contém atalhos rápidos do dia a dia (siglas, saudações estáticas, e-mails de contato da STI e pequenas abreviações padronizadas).

### [celular.yml](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/match/celular.yml)
* **Função**: Mapeamento do gatilho de suporte celular (`:cel`).
* **O que faz**: Associa o gatilho `:cel` à chamada do script dinâmico `scripts/python/celular.py`, que renderiza os modelos HTML de suporte.

### [clipboard.yml](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/match/clipboard.yml)
* **Função**: Mapeamento de utilitários rápidos de clipboard.
* **O que faz**: Define gatilhos rápidos (ex: `:arrumar` para correção de texto, `:caps` para caixa alta, `:low` para caixa baixa) associando-os aos respectivos scripts executores PowerShell.

### [ola.yml](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/match/ola.yml)
* **Função**: Mapeamento do gatilho de saudação e abertura de chamados (`:ola`).
* **O que faz**: Associa o gatilho `:ola` ao script `scripts/python/dispatcher.py`, que gerencia e renderiza o cabeçalho e corpo da resposta com base no tipo de atendimento.

### [transporte_material.yml](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/match/transporte_material.yml)
* **Função**: Mapeamento do gatilho de transporte de materiais (`:tmat`).
* **O que faz**: Invoca o script `scripts/python/transporte_material.py` após o formulário correspondente.

### [transporte_urbano.yml](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/match/transporte_urbano.yml)
* **Função**: Mapeamento do gatilho de agendamento de motorista/transporte urbano (`:turb`).
* **O que faz**: Invoca o script `scripts/python/transporte_urbano.py` após a inserção dos dados de destino urbano.

### [transporte_viagem.yml](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/match/transporte_viagem.yml)
* **Função**: Mapeamento do gatilho de agendamento de transporte de viagem intermunicipal (`:tvia`).
* **O que faz**: Invoca o script `scripts/python/transporte_viagem.py` após o formulário do itinerário intermunicipal.
