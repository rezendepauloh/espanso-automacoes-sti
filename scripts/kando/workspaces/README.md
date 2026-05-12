# 📁 Automatizadores de Áreas de Trabalho (workspaces)

Este diretório armazena scripts complexos focados no gerenciamento de fluxos de trabalho locais da STI. Eles automatizam a abertura simultânea de abas de rede, conexões de sistemas e pastas do SharePoint de acordo com a área de atuação do usuário.

## 📄 Arquivos e Bibliotecas

### [biblioteca.ps1](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/kando/workspaces/biblioteca.ps1)
* **Função**: Motor de abertura de pastas e geração de relatórios de log.
* **O que faz**:
  * Fornece o núcleo de verificação física de caminhos de rede.
  * Se uma pasta do SharePoint ou OneDrive não for localizada, exibe uma notificação elegante na tela avisando sobre o problema, em vez de falhar silenciosamente.
  * Salva logs de auditoria detalhados e localizados de cada tentativa de abertura em `log_pastas.log`.

### [abrir_sajmp.ps1](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/kando/workspaces/abrir_sajmp.ps1)
* **Função**: Inicializador inteligente do sistema SAJMP.
* **O que faz**: Executa a rotina de abertura segura do atalho administrativo do sistema institucional SAJMP.

### [abrir_terminal_elevado.ps1](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/kando/workspaces/abrir_terminal_elevado.ps1)
* **Função**: Disparador de Console de Administrador.
* **O que faz**: Abre uma nova instância de terminal do PowerShell em modo de privilégio elevado (Administrador) para realização de comandos locais avançados de suporte.

### [limpar_memoria_fechando_apps.ps1](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/kando/workspaces/limpar_memoria_fechando_apps.ps1)
* **Função**: Script de otimização de RAM.
* **O que faz**: Encerra processos pesados ou inativos em segundo plano de forma segura para liberar memória RAM da máquina de atendimento do usuário.

### [pastas_chamados.ps1](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/kando/workspaces/pastas_chamados.ps1)
* **Função**: Carrega a área de atendimento a chamados.
* **O que faz**: Abre automaticamente as pastas do SharePoint e planilhas unificadas relativas ao acompanhamento de chamados abertos da DIT-Manutenção.

### [pastas_contratos.ps1](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/kando/workspaces/pastas_contratos.ps1)
* **Função**: Carrega o fluxo de gestão de contratos.
* **O que faz**: Abre em lote os diretórios locais e na nuvem de documentos, licitações e contratos mantidos pela coordenação.

### [pastas_estudos.ps1](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/kando/workspaces/pastas_estudos.ps1)
* **Função**: Abre diretórios de provas e aulas.
* **O que faz**: Atalho direto para as pastas pessoais e acadêmicas localizadas na nuvem do OneDrive do usuário.
