# 🛸 Espanso & Kando – Automações de Atendimento STI (MPMS)

Este repositório contém a suíte completa de automações desenvolvida em **Espanso + Python + PowerShell** com integrações ao **Kando** e **CopyQ**, desenhada sob medida para otimizar o atendimento de TI, agilizar respostas técnicas e formatar rotinas administrativas.

---

## 🚀 Funcionalidades Principais

### 📋 1. Espanso Dynamic Forms (EDF)
* **Formulários Dinâmicos**: Integração nativa com o `EDF.exe` para exibir caixas de diálogo interativas diretamente na tela do usuário.
* **Saudações Inteligentes (`:ola`)**: Coleta dados de chamados, nome de contato, e resolve o corpo do e-mail com base em templates HTML dinâmicos (suporte a BIOS, Lentidão, Telefonia, Troca de Ramais).
* **Gestão de Diárias de Viagem (`:tvia` / `:tmat` / `:turb`)**:
  * Calcula datas de início e fim.
  * Resolve automaticamente os dias da semana correspondentes.
  * Formata e pluraliza de forma inteligente comarcas e trajetos (ex: *"na comarca de..."* para 1 comarca; ou *"nas comarcas de..."* para mais de uma comarca).

### 🧠 2. Processamento de Texto Inteligente (NLP)
* **Híbrido de IA & Regex**: Motor NLP em Python utilizando a biblioteca **spaCy** combinada com dicionários rápidos.
* **Corretor Ortográfico de Clipboard (`:arrumar`)**: Corrige pontuações, arruma acentuação no contexto exato (distingue o verbo `é` da conjunção `e`) e resolve abreviações comuns.
* **Dicionário Centralizado Único**: Um único arquivo JSON ([dicionario.json](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/lib/dicionario.json)) gerencia mais de 340 siglas institucionais capitalizadas automaticamente (ex: `mpms` -> `MPMS`, `sajmp` -> `SAJMP`, `dit` -> `DIT`).
* **Limpador de PDF (`limpa_pdf.ps1`)**: Remove hífens de quebra de página e agrupa linhas cortadas ao copiar textos de relatórios em arquivos PDF para o clipboard.

### 🎛️ 3. Menu Radial Produtivo (Kando)
* Atalhos circulares que acionam os mesmos formulários do Espanso de forma 100% silenciosa e em plano de fundo.
* **Sincronizador Automático de Ambientes (`master_fix_kando.py`)**: Script inteligente que detecta qual usuário está logado no Windows (Casa, Trabalho, Administrador) e atualiza instantaneamente as centenas de caminhos absolutos de atalhos e scripts no arquivo de configuração ativo do Kando (`%APPDATA%/Kando/config.json`).
* **Auxiliares de Janela**: Atalhos rápidos para Minimizar, Maximizar ou Restaurar as janelas em foco usando VBScript silencioso.

### 📋 4. Histórico Inteligente (CopyQ)
* Executa as mesmas regras de correção e limpeza rápida de texto diretamente em itens armazenados no histórico da área de transferência.

---

## 📁 Estrutura de Diretórios do Projeto

```text
📁 espanso/
├── 📁 config/              # Configurações globais e engines do Espanso (default.yml)
├── 📁 forms/               # Esquemas YAML dos formulários dinâmicos do EDF
├── 📁 icons/               # Ícones PNG customizados para Kando e CopyQ
├── 📁 match/               # Mapeamento de gatilhos, atalhos estáticos e disparadores
└── 📁 scripts/             # Lógica principal de automação
    ├── 📁 copyq/           # Scripts JavaScript de integração do CopyQ
    ├── 📁 kando/           # Scripts e atalhos de janelas do Menu Radial Kando
    │   ├── 📁 calls/       # Wrappers de uma linha para chamar gatilhos
    │   ├── 📁 helpers/     # Utilitários de sistema (janelas, invisivel.vbs)
    │   └── 📁 workspaces/  # Automatizadores de abertura de pastas e abas do Explorer
    ├── 📁 lib/             # Dicionário JSON e módulos utilitários em Python/PowerShell
    ├── 📁 powershell/      # Scripts executores PowerShell de manipulação de clipboard
    ├── 📁 tests/           # Suíte de testes unitários (rodar_testes.ps1, python, ps1)
    └── 📁 textos/          # Templates HTML organizados por categoria de atendimento
```

---

## 🛠️ Tecnologias Utilizadas
* **Espanso** (Mecanismo de expansão)
* **Kando** (Menu radial para atalhos do mouse/teclado)
* **CopyQ** (Histórico de área de transferência avançado)
* **Python 3.10+** (spaCy NLP, parseador de dados)
* **PowerShell 5.1 / 7** (Manipulação de Clipboard e controle de processos no Windows)

## 🧪 Como Executar os Testes Unitários
Abra um console PowerShell na raiz e execute:
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\tests\rodar_testes.ps1"
```
Isso validará 100% da integridade física de templates HTML, carregamento de dicionário JSON, algoritmos de datas e o processador ortográfico.