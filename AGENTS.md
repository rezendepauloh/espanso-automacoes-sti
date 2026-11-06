# 🤖 AGENTS.md — Diretrizes para Agentes de IA & Engenharia Autônoma

> **Instruções operacionais, restrições arquiteturais e protocolo de trabalho para Antigravity, Claude Code, Gemini e assistentes de código que operam neste repositório.**  
> *Leia com atenção antes de realizar qualquer alteração em scripts, formulários, regras do Espanso ou documentação.*

---

## 🎯 1. Filosofia e Visão Geral do Sistema

O **Espanso Automações STI (MPMS)** é um ecossistema de produtividade, formatação contextual e automação de chamados técnicos para a Secretaria de Tecnologia da Informação do Ministério Público de Mato Grosso do Sul.

O sistema opera de forma **híbrida e multiplataforma** tanto em **Linux (Pop!_OS COSMIC Wayland / X11)** quanto em **Windows 10/11**, integrando:
1. **Espanso**: Expansor de texto via matchers YAML (`match/`), variáveis dinâmicas e formulários (`forms/`).
2. **Motor NLP em Python**: Análise linguística com spaCy, expansão de mais de 340 siglas institucionais e resolução de templates HTML.
3. **PowerShell & Bash**: Utilitários de manipulação de clipboard, limpeza de quebra de linha de PDFs e acionadores de atalhos.
4. **Kando Pie Menu & CopyQ**: Interfaces rápidas de disparo visual e sanitização de histórico.

---

## 🏗️ 2. Arquitetura Modular e Organização de Diretórios

```text
.
├── config/                         # Configurações do motor Espanso
│   ├── default.yml                 # Configuração compartilhada (gatilhos, toggle)
│   ├── linux.yml                   # Backend Wayland (EVDEV, layout us-intl)
│   └── windows.yml                 # Backend nativo do Windows
├── forms/                          # Esquemas JSON/YAML para formulários dinâmicos (EDF / form_runner)
│   ├── analisador.yml              # Coleta IP/hostname para diagnóstico de máquina
│   ├── celular.yml                 # Pesquisa de suporte celular/telefonia
│   ├── devolucao_chamado.yml       # Despacho técnico de devolução de chamado
│   ├── diaria_viagem.yml           # Cálculo de diárias e roteiro de viagens
│   ├── manutencao.yml              # Limpeza remota de perfis e manutenção
│   ├── ola.yml                     # Saudação e cabeçalho mestre de atendimento
│   ├── remove_profiles.yml         # Remoção de contas de usuário órfãs
│   ├── transporte_material.yml     # Trâmite de equipamentos e periféricos
│   ├── transporte_urbano.yml       # Deslocamento urbano de servidores
│   └── transporte_viagem.yml       # Deslocamento intermunicipal de equipe
├── icons/                          # Ativos gráficos dos menus Kando e CopyQ
├── match/                          # Definições de triggers e substituições do Espanso
│   ├── admin_scripts.yml           # Atalhos para rotinas elevadas
│   ├── base.yml                    # Expansões estáticas comuns
│   ├── celular.yml                 # Respostas padronizadas de telefonia
│   ├── clipboard.yml               # ;arrumar, ;maiuscula, ;minuscula, ;parenteses
│   ├── ola.yml                     # Gatilhos :ola e :dev
│   ├── transporte_material.yml     # Gatilhos :tmat e :transdevo
│   ├── transporte_urbano.yml       # Gatilho :turb
│   └── transporte_viagem.yml       # Gatilhos :tvia e :diaria
├── scripts/                        # Lógica de negócio e executores
│   ├── copyq/                      # Comandos JavaScript para a área de transferência
│   ├── kando/                      # Integração do menu radial
│   │   ├── calls/                  # Wrappers chamadores (chamar_gatilho.sh e chamar_*.ps1)
│   │   ├── helpers/                # Scripts auxiliares de janelas (janelas.ps1, invisivel.vbs)
│   │   └── workspaces/             # Automação de janelas e abas do Explorer/Nautilus
│   ├── lib/                        # Núcleo compartilhado
│   │   ├── dicionario.json         # Base central de dados com mais de 340 siglas
│   │   ├── dicionario.ps1          # Converte dicionario.json em Hashtable no PowerShell
│   │   ├── dictionary.py           # Loader de dicionario.json em dict Python
│   │   ├── form_runner.py          # Renderizador de formulários nativo (Tkinter/Zenity) no Linux
│   │   ├── utils.ps1               # Invoke-TextCorrection e Clean-PdfText
│   │   └── utils.py                # Motor NLP spaCy, fix_text_with_ai e formatação
│   ├── powershell/                 # Scripts utilitários em PowerShell
│   ├── python/                     # Despachantes e geradores de texto dinâmicos
│   │   ├── celular.py              # Respostas de telefonia móvel
│   │   ├── devolucao_chamado.py    # Notificação de devolução técnica
│   │   ├── diaria_viagem.py        # Algoritmo de datas, dias úteis e comarcas
│   │   ├── dispatcher.py           # Despachante principal (:ola)
│   │   ├── executar_admin.py       # Execução assíncrona de rotinas administrativas
│   │   ├── ia_arrumar.py           # Corretor ortográfico inteligente do clipboard
│   │   ├── maiuscula.py            # Caixa alta multiplataforma
│   │   ├── minuscula.py            # Caixa baixa multiplataforma
│   │   ├── master_fix_kando.py     # Sincronizador de paths nos configs do Kando
│   │   └── respostas.py            # Resolvedor modular de templates de e-mail
│   ├── tests/                      # Suíte de Testes Automatizados
│   │   ├── run_all.py              # Orquestrador unificado ANSI colorido
│   │   ├── rodar_testes.ps1        # Wrapper PowerShell para Windows e Linux
│   │   ├── test_library.ps1        # Testes de funções puras PowerShell
│   │   ├── unit/                   # Testes unitários (syntax, nlp, cross_platform, pwsh)
│   │   └── integration/            # Testes de integração (forms, matches, kando)
│   └── textos/                     # Templates HTML de respostas rápidas
├── tests -> scripts/tests          # Link simbólico para execução conveniente a partir da raiz
├── AGENTS.md                       # Este guia para assistentes autônomos
└── README.md                       # Documentação geral do repositório
```

---

## ⚠️ 3. Regras Críticas de Engenharia (NÃO VIOLE)

1. **Portabilidade Universal de Separadores de Caminho**:
   - **NUNCA** use barras invertidas `\` para caminhos em dot-sourcing no PowerShell (ex: evite `. "$PSScriptRoot\..\lib\utils.ps1"`). Use sempre barras normais: `. "$PSScriptRoot/../lib/utils.ps1"`. O PowerShell aceita `/` tanto no Windows quanto no Linux.
   - Em Python, use sempre `pathlib.Path` ou `os.path.join`. Evite strings literais com `\` para caminhos de diretório.
   - Nos arquivos `match/*.yml`, use sempre `%CONFIG%/scripts/...`. O Espanso expande `%CONFIG%` dinamicamente em ambas as plataformas (Linux e Windows), enquanto `$CONFIG` no Windows não é interpretado e resulta em erro de path.

2. **Invocação Segura de Subprocessos Python**:
   - Dispatchers Python (`dispatcher.py`, `run_script.py`, etc.) **DEVEM** invocar `sys.executable` ao chamar scripts filhos via `subprocess`. Nunca use a string hardcoded `"python"`, pois em ambientes Linux ela pode não existir ou apontar para um binário inconsistente.

3. **Independência de Diretório Atual (CWD)**:
   - Funções que carregam arquivos (como `read_template()`, `run_edf_form()`, `load_dictionary()`) **NÃO** devem presumir que o usuário executou o comando a partir da pasta do script. Use `Path(__file__).resolve().parent` para calcular caminhos relativos ao arquivo físico.

4. **Compatibilidade de Formulários (Linux vs Windows)**:
   - O executável `EDF.exe` só existe no Windows. No Linux, o sistema automaticamente aciona o `form_runner.py` (baseado em Tkinter / Zenity). Toda alteração em `forms/*.yml` deve manter a chave `schema` (JSON Schema com `properties`) e a chave `template` (Jinja2) consistentes.
   - Todo placeholder `{{campo}}` usado no template deve corresponder a uma propriedade declarada em `schema.properties`.

5. **Proteção de Stream UTF-8 e Platform Flags**:
   - Nunca recrie cegamente `sys.stdout = io.TextIOWrapper(...)` se o stream já estiver em UTF-8. No Linux isso fecha o descritor de arquivo original. Use a proteção existente:
     ```python
     if sys.stdout and hasattr(sys.stdout, 'encoding') and sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
         sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
     ```
   - No PowerShell, proteja chamadas de `Add-Type -AssemblyName System.Windows.Forms` contra execução em ambientes Linux (`if ($IsLinux) { ... }`).

---

## 🔄 4. Ciclo Obrigatório de Toda Mudança (Checklist do Agente)

Antes de finalizar qualquer interação que envolva código, formulários ou configurações:

1. **Executar a Suíte Completa de Testes**:
   ```bash
   python3 tests/run_all.py
   ```
   - Todos os testes (unitários e de integração) **DEVEM** passar com 100% de sucesso.
   - Nenhuma entrega com falha ou regressão será aceita.

2. **Criar Testes para Novas Funcionalidades**:
   - Se criar um novo formulário em `forms/`, certifique-se de que ele respeita a sintaxe YAML e o schema testado por `test_forms_and_matches.py`.
   - Se criar um script ou dispatcher, adicione um caso de teste correspondente em `tests/unit/` ou `tests/integration/`.

3. **Verificar Permissões e Shebangs**:
   - Scripts executáveis em Python ou Bash devem conter shebang (`#!/usr/bin/env python3` ou `#!/bin/bash`) e permissão de execução `+x`.

4. **Sincronizar Documentação**:
   - Mantenha `README.md` e `AGENTS.md` rigorosamente atualizados com novos atalhos, parâmetros e mudanças de arquitetura.

---

## 🧪 5. Comandos Chave de Referência Rápida

| Objetivo | Comando |
| :--- | :--- |
| **Executar todos os testes (Linux/macOS)** | `python3 tests/run_all.py` |
| **Executar todos os testes (PowerShell)** | `pwsh scripts/tests/rodar_testes.ps1` |
| **Executar apenas testes unitários** | `python3 -m unittest discover -s scripts/tests/unit` |
| **Executar apenas testes de integração** | `python3 -m unittest discover -s scripts/tests/integration` |
| **Testar corretor NLP direto no terminal** | `python3 scripts/python/ia_arrumar.py` |
| **Testar despacho de viagem no terminal** | `python3 scripts/python/diaria_viagem.py` |

