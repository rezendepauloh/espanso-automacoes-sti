# 🛸 Espanso, CopyQ & Kando – Automações de Atendimento STI (MPMS)

> Suíte completa e multiplataforma de automações e produtividade em **Espanso + Python + Bash + PowerShell**, integrada ao **Kando** e **CopyQ**, desenhada sob medida para otimizar o atendimento de TI, agilizar respostas técnicas institucionais e formatar rotinas administrativas no **Linux (Pop!_OS COSMIC / Wayland)** e **Windows 10/11**.

---

## 🎯 Visão Geral e Filosofia

O projeto visa transformar o fluxo de trabalho do suporte técnico da STI (Secretaria de Tecnologia da Informação do MPMS), eliminando tarefas repetitivas através de três pilares:

1. **Portabilidade Universal (Linux & Windows)**:
   - Caminhos de arquivos agnósticos de plataforma (usando `/` e `Path`).
   - Formulários dinâmicos com fallback inteligente: [EDF.exe](https://github.com/espanso/espanso) no Windows e [form_runner.py](/scripts/lib/form_runner.py) (Tkinter / Zenity) no Linux.
   - Ativação de atalhos via [chamar_gatilho.sh](/scripts/kando/calls/chamar_gatilho.sh) (`wtype` / `evdev` / Wayland) e [chamar_gatilho.ps1](/scripts/kando/calls/chamar_gatilho.ps1) (`SendKeys` / Windows).
2. **Inteligência Contextual e Linguística (NLP)**:
   - Motor híbrido com [spaCy](https://spacy.io/) e dicionários de termos institucionais com mais de 340 siglas capitalizadas automaticamente.
   - Algoritmo contextual que distingue a conjunção aditiva `e` do verbo flexionado `é`.
3. **Qualidade e Regressão Zero**:
   - Suíte de testes automatizados unificada com **26 testes unitários e de integração**, cobertura de sintaxe estática (Python, Bash, PowerShell, YAML e JSON) e validação de coerência estrutural.

---

## 🚀 Funcionalidades Principais

### 📋 1. Formulários Dinâmicos e Despachos Rápidos
* **Saudações de Chamados (`:ola`)**:
  - Exibe formulário dinâmico coletando nome do contato, número do chamado, tipo de atendimento e detalhes do equipamento.
  - Carrega dinamicamente templates HTML modulares para BIOS, Lentidão, Telefonia, Pedidos de Fotos, Equipamentos fora do domínio e Troca de Ramais.
* **Diárias e Transporte Intermunicipal (`:diaria` / `:tvia`)**:
  - Coleta datas de saída e retorno, passageiros e destinos.
  - Formata as datas no padrão brasileiro (`DD/MM/AAAA`) e calcula automaticamente os dias da semana (`segunda-feira`, etc.).
  - Pluraliza inteligentemente as comarcas (ex: *"na comarca de Bonito"* vs *"nas comarcas de Bonito e Jardim"*).
* **Transporte Urbano (`:turb`)**:
  - Sugere automaticamente o horário atual arredondado para o próximo bloco de 30 minutos.
* **Devolução e Movimentação de Material (`:tmat` / `:dev`)**:
  - Despachos padronizados para trâmite de monitores, gabinetes, switches e periféricos com controle de patrimônio.

### 🧠 2. Processamento de Texto Inteligente (NLP)
* **Corretor Contextual de Clipboard (`;arrumar` ou `:ia`)**:
  - Corrige pontuação colada, ajusta capitalização pós-pontuação e normaliza espaçamentos.
  - Substitui siglas mapeadas no [dicionario.json](/scripts/lib/dicionario.json) (ex: `mpms` $\rightarrow$ `MPMS`, `sajmp` $\rightarrow$ `SAJMP`, `sti` $\rightarrow$ `STI`, `dit` $\rightarrow$ `DIT`).
* **Formatador de Caixa Alta e Baixa (`;maiuscula` / `;minuscula`)**:
  - Execução ultra rápida em Python nativo cross-platform (~15ms) para transformar o texto copiado no clipboard.
* **Limpador de Texto de PDF (`limpa_pdf.ps1`)**:
  - Remove hífens de quebra de margem e reconstitui parágrafos contínuos preservando pontuações jurídicas (`art.`, `inc.`, `fls.`).

### 🎛️ 3. Menu Radial Produtivo (Kando)
* Acesso visual rápido via atalhos circulares do mouse.
* Chamadores otimizados em [scripts/kando/calls/](/scripts/kando/calls/):
  - No Linux: [chamar_gatilho.sh](/scripts/kando/calls/chamar_gatilho.sh) dispara via Wayland ou scripts Python diretos.
  - No Windows: [chamar_gatilho.ps1](/scripts/kando/calls/chamar_gatilho.ps1) simula atalho nativo do Espanso.
* **Sincronizador de Ambientes ([`master_fix_kando.py`](/scripts/python/master_fix_kando.py))**:
  - Atualiza caminhos de backup e arquivos ativos do Kando (`~/.config/kando/` ou `%APPDATA%\Kando\`).

---

## 📁 Estrutura do Repositório

```text
.
├── config/                         # Configurações do Espanso
│   ├── default.yml                 # Configuração compartilhada
│   ├── linux.yml                   # Otimizações específicas para Linux/Wayland (EVDEV)
│   └── windows.yml                 # Otimizações específicas para Windows
├── forms/                          # Esquemas YAML de formulários dinâmicos
│   ├── analisador.yml              # Analisador de hardware e inventário
│   ├── celular.yml                 # Levantamento de suporte a celular/telefonia
│   ├── devolucao_chamado.yml       # Devolução técnica de chamados
│   ├── diaria_viagem.yml           # Solicitação de diárias de viagem
│   ├── manutencao.yml              # Manutenção preventiva e limpeza de host
│   ├── ola.yml                     # Abertura padrão de atendimento
│   ├── remove_profiles.yml         # Remoção de perfis locais órfãos
│   ├── transporte_material.yml     # Transporte de material e patrimônio
│   ├── transporte_urbano.yml       # Transporte de passageiros urbano
│   └── transporte_viagem.yml       # Transporte de passageiros intermunicipal
├── icons/                          # Ícones temáticos para Kando e CopyQ
├── match/                          # Regras de expansão de texto (matches)
│   ├── admin_scripts.yml           # Atalhos de scripts com privilégio administrativo
│   ├── base.yml                    # Expansões estáticas comuns
│   ├── celular.yml                 # Gatilhos de resposta de celular
│   ├── clipboard.yml               # ;arrumar, ;maiuscula, ;minuscula, ;parenteses
│   ├── ola.yml                     # :ola e :dev
│   ├── transporte_material.yml     # :tmat e :transdevo
│   ├── transporte_urbano.yml       # :turb
│   └── transporte_viagem.yml       # :tvia e :diaria
├── scripts/                        # Código-fonte das automações
│   ├── copyq/                      # Integração com o histórico de clipboard
│   ├── kando/                      # Menu Radial Kando
│   │   ├── calls/                  # Wrappers chamadores (Bash e PowerShell)
│   │   ├── helpers/                # Gerenciamento de janelas e scripts auxiliares
│   │   └── workspaces/             # Automação de pastas e abas do Explorer
│   ├── lib/                        # Bibliotecas centrais compartilhadas
│   │   ├── dicionario.json         # Dicionário JSON com mais de 340 siglas
│   │   ├── dicionario.ps1          # Loader do dicionário em PowerShell
│   │   ├── dictionary.py           # Loader do dicionário em Python
│   │   ├── form_runner.py          # Executor GUI nativo multiplataforma (Tkinter/Zenity)
│   │   ├── utils.ps1               # Utilitários de texto e clipboard PowerShell
│   │   └── utils.py                # Motor NLP Spacy, datas, templates e clipboard
│   ├── powershell/                 # Scripts auxiliares PowerShell
│   ├── python/                     # Despachantes e geradores Python
│   │   ├── celular.py              # Gerador de respostas sobre celulares
│   │   ├── devolucao_chamado.py    # Gerador de mensagens de devolução
│   │   ├── diaria_viagem.py        # Calculador de datas e comarcas
│   │   ├── dispatcher.py           # Despachante mestre do atendimento (:ola)
│   │   ├── executar_admin.py       # Disparador assíncrono de rotinas elevadas
│   │   ├── ia_arrumar.py           # Corretor ortográfico contextual
│   │   ├── maiuscula.py            # Caixa alta multiplataforma
│   │   ├── minuscula.py            # Caixa baixa multiplataforma
│   │   ├── master_fix_kando.py     # Sincronizador de configurações do Kando
│   │   └── respostas.py            # Resolvedor de templates HTML de atendimento
│   ├── tests/                      # Suíte de Testes Automatizados
│   │   ├── run_all.py              # Executor unificado com saída ANSI colorida
│   │   ├── rodar_testes.ps1        # Wrapper para PowerShell no Windows/Linux
│   │   ├── test_library.ps1        # Testes puros da biblioteca PowerShell
│   │   ├── unit/                   # Testes unitários (sintaxe, NLP, cross-platform)
│   │   └── integration/            # Testes de integração (forms, matches, kando)
│   └── textos/                     # Templates HTML de respostas organizados por categoria
├── tests -> scripts/tests          # Link simbólico para execução conveniente a partir da raiz
├── AGENTS.md                       # Diretrizes para agentes de IA e engenharia autônoma
└── README.md                       # Esta documentação
```

---

## 🧪 Como Executar a Suíte de Testes

A suíte possui relatório detalhado com cores ANSI, medição de tempo em milissegundos e resumo completo de execução:

### 🐧 No Linux / macOS:
```bash
# A partir da raiz do repositório:
python3 tests/run_all.py

# Ou pelo caminho do módulo:
python3 scripts/tests/run_all.py
```

### 🪟 No Windows (ou via PowerShell Core):
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/tests/rodar_testes.ps1
```

---

## 🛠️ Requisitos e Instalação

* **Espanso**: Versão `2.2.1` ou superior instalada.
* **Python**: Versão `3.10+` com as dependências do ambiente:
  ```bash
  pip install spacy pyperclip pyyaml
  python -m spacy download pt_core_news_sm
  ```
* **PowerShell**: PowerShell 7 (`pwsh`) no Linux ou Windows PowerShell 5.1 / 7 no Windows.
* **Kando** *(opcional)*: Versão `1.4.0+` para acionamento via menu radial.
* **CopyQ** *(opcional)*: Para regras automáticas de limpeza no histórico da área de transferência.
