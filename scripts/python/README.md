# 🐍 Diretório de Scripts Python (scripts/python)

Este diretório contém os scripts executivos e processadores de formulário escritos em **Python 3**. Ele faz uso extensivo do processamento de linguagem natural (NLP Spacy), tratamento dinâmico de strings e renderização de layouts HTML.

## 📄 Arquivos

### [celular.py](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/python/celular.py)
* **Função**: Processador do formulário de telefonia celular.
* **O que faz**: Recebe as variáveis do formulário `:cel` e injeta os dados nos templates de celular correspondentes (localizados em `scripts/textos/celular/`).

### [devolucao_chamado.py](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/python/devolucao_chamado.py)
* **Função**: Gerador de textos de devolução ou reatribuição de chamados.
* **O que faz**: Formata de modo elegante e formal o motivo pelo qual um atendimento de chamado da STI está sendo devolvido ou transferido de setor.

### [diaria_viagem.yml](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/python/diaria_viagem.py)
* **Função**: Calculadora inteligente de diárias e comarcas para viagens.
* **O que faz**:
  * Formata e valida o período das datas de início e fim da viagem.
  * Calcula de forma inteligente o dia da semana correspondente a cada data.
  * Agrupa e processa a lista de cidades/comarcas de destino (pluraliza corretamente: "na comarca de..." se for 1 cidade; ou "nas comarcas de..." se forem 2 ou mais, fazendo a junção ortográfica perfeita com "e" e vírgulas).

### [dispatcher.py](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/python/dispatcher.py)
* **Função**: Despachador de atendimentos unificado.
* **O que faz**: Centraliza a lógica de decisão do formulário `:ola`. Se o atendimento for de materiais, redireciona o fluxo para o script de materiais; se for um atendimento de suporte comum, invoca o script de respostas rápidas para carregar o HTML correspondente.

### [ia_arrumar.py](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/python/ia_arrumar.py)
* **Função**: Corretor inteligente com IA / NLP.
* **O que faz**: Executa o motor NLP de correção ortográfica e de contexto no texto copiado do clipboard, unindo gramática contextualizada com a expansão inteligente do dicionário de termos institucionais.

### [master_fix_kando.py](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/python/master_fix_kando.py)
* **Função**: Sincronizador Automático de Configurações do Kando.
* **O que faz**: Autodetecta qual usuário está logado no Windows (seja `paulogoncalves` no trabalho, `paulo_admin` em privilégio elevado ou `User` em casa) e migra instantaneamente todas as centenas de caminhos absolutos do arquivo de configuração ativo (`%APPDATA%/Kando/config.json`) ou backups locais, permitindo portabilidade total entre dispositivos.

### [material.py](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/python/material.py)
* **Função**: Gerador de procedimento de solicitação de materiais.
* **O que faz**: Cria instruções passo a passo detalhadas para o usuário final sobre como solicitar materiais via Portal de Serviços do MPMS, distinguindo dinamicamente as regras entre materiais de consumo e materiais permanentes (com ou sem necessidade de substituição por defeito).

### [respostas.py](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/python/respostas.py)
* **Função**: Repositório de respostas rápidas de atendimentos comuns.
* **O que faz**: Associa a opção selecionada no formulário `:ola` (como BIOS, lentidão, telefone desconectado, ramal, cabos, etc.) ao arquivo HTML de resposta estática correto localizado na pasta `scripts/textos/` e o imprime formatado.

### [transporte_material.py](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/python/transporte_material.py)
* **Função**: Gerador de requisições de transporte de materiais da STI.

### [transporte_urbano.py](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/python/transporte_urbano.py)
* **Função**: Gerador de reservas de veículos para rotas urbanas.

### [transporte_viagem.py](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/python/transporte_viagem.py)
* **Função**: Gerador de agendamento de viagens de longa distância.

### [update_kando_ai.py](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/python/update_kando_ai.py)
* **Função**: Script histórico utilitário para atualização em lote de comandos do Kando nos backups JSON.
