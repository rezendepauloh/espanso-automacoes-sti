# 📋 Diretório de Formulários (Forms)

Este diretório armazena os esquemas YAML dos formulários dinâmicos exibidos pelo **EDF.exe** (Espanso Dynamic Forms). Cada formulário define os campos de entrada, listas de seleção (`enum`) e botões que o usuário preenche ao acionar um gatilho.

## 📄 Arquivos

### [celular.yml](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/forms/celular.yml)
* **Função**: Formulário de atendimento e suporte à telefonia celular institucional.
* **O que faz**: Solicita o nome do usuário, permite selecionar o modelo de resposta/modelo de erro e as observações (normais ou críticas).

### [devolucao_chamado.yml](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/forms/devolucao_chamado.yml)
* **Função**: Formulário para preenchimento de devolução de chamados.
* **O que faz**: Solicita o número do chamado e a justificativa para devolução ou re-atribuição de atendimento.

### [diaria_viagem.yml](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/forms/diaria_viagem.yml)
* **Função**: Formulário para solicitação e prestação de contas de diárias de viagem.
* **O que faz**: Coleta informações sobre o beneficiário, período da viagem (datas de início e fim) e as comarcas/cidades de destino.

### [ola.yml](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/forms/ola.yml)
* **Função**: Formulário unificado de saudação e abertura de atendimentos da STI.
* **O que faz**: Coleta o nome, número do chamado e o tipo de atendimento (como lentidão, BIOS, problemas de telefonia, pedido de materiais). O conteúdo serve como entrada para o disparador inteligente de templates.

### [transporte_material.yml](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/forms/transporte_material.yml)
* **Função**: Formulário de requisição de transporte de materiais e insumos da STI.
* **O que faz**: Solicita detalhes dos materiais, origem, destino e número do chamado de suporte.

### [transporte_urbano.yml](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/forms/transporte_urbano.yml)
* **Função**: Formulário de reserva para transporte urbano (dentro do município).
* **O que faz**: Reúne dados sobre os passageiros, horário de partida, destino exato, finalidade da locomoção e o motorista atribuído.

### [transporte_viagem.yml](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/forms/transporte_viagem.yml)
* **Função**: Formulário de agendamento de viagem intermunicipal de transporte.
* **O que faz**: Semelhante ao urbano, mas foca em rotas de longa distância intermunicipais, registrando detalhes detalhados do itinerário do veículo oficial.
