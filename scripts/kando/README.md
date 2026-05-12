# 🎛️ Diretório de Integração do Kando (scripts/kando)

Este diretório contém os componentes, atalhos dinâmicos, credenciais de segurança e scripts utilitários do menu radial **Kando**. Ele gerencia ações rápidas executadas a partir de atalhos e menus circulares.

## 📁 Estrutura e Subdiretórios

* **[calls/](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/kando/calls/)**: Contém os despachadores e wrappers parametrizados de atalhos.
  * `chamar_gatilho.ps1`: Despachador de 100% dos atalhos que simula a digitação de gatilhos do Espanso.
  * Wrappers individuais como `chamar_celular.ps1`, `chamar_ola.ps1` etc., que chamam o gatilho correto em uma única linha.
* **[helpers/](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/kando/helpers/)**: Scripts utilitários de sistema.
  * `janelas.ps1`: Helper que executa ações de maximizar, minimizar e restaurar a janela ativa do Windows usando simulação de teclas nativas.
  * `invisivel.vbs`: Script que invoca as automações do PowerShell em plano de fundo de forma 100% oculta para o usuário, sem piscar nenhuma tela preta de terminal.
* **[workspaces/](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/kando/workspaces/)**: Pasta dedicada a scripts de abertura e gerenciamento de áreas de trabalho complexas (como carregar automaticamente todas as pastas de chamados ou contratos, abrir o SAJMP, etc.) com geração de log detalhada em tempo de execução.
* **[credenciais/](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/kando/credenciais/)**: Armazena de forma criptografada as credenciais locais necessárias para execução de scripts de rede ou de sistemas. *(Ignorado pelo controle de versão por motivos de segurança).*

## 📄 Arquivos

### [config.ps1](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/kando/config.ps1)
* **Função**: Arquivo de configurações locais do Kando (não enviado ao Git).
* **O que faz**: Guarda os caminhos de rede e do OneDrive de pastas de Provas, SharePoint, Contratos, Chamados Unificados e pastas locais do computador do usuário de forma a parametrizar a biblioteca de aberturas.
