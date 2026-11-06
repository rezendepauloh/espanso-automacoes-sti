# 📚 Central de Documentação Técnica — Espanso Automações STI (MPMS)

> **Documentação técnica unificada de engenharia, arquitetura, manuais práticos e portabilidade Linux/Windows do sistema de automação e atendimento.**

---

## 🗂️ Estrutura e Mapa da Documentação

```text
Docs/
├── README.md                                  # Este índice central unificado
│
├── 📖 guias/                                  # Manuais práticos de uso e rotinas
│   ├── atendimento_e_respostas_rapidas.md     # Formulário :ola, despachante e templates
│   ├── suporte_telefonia_celular.md           # Gatilho :cel e instruções de telefonia móvel
│   ├── viagens_e_diarias_terceirizados.md     # Gatilhos :viagem, :diaria e transporte
│   └── scripts_administrativos_edf.md         # Atalhos :analisar, :limpar, :deluser
│
├── 🏛️ arquitetura/                            # Decisões fundamentais de engenharia
│   ├── portabilidade_linux_windows.md         # Padrões cross-platform e observação do %CONFIG%
│   ├── motor_nlp_e_dicionario.md              # spaCy pt_core_news_sm e dicionário de siglas
│   └── formularios_dinamicos_e_runner.md      # EDF (Windows) vs form_runner.py (Linux)
│
├── 🧪 testes/                                 # Qualidade de software e integridade
│   └── suite_de_testes_automatizados.md       # Execução e cobertura de testes unitários e de integração
│
└── 🚨 issues/                                 # Registro de compatibilidade e pendências
    └── compatibilidade_config_espanso.md      # Registro do comportamento de %CONFIG% vs $CONFIG
```

---

## 🚀 Acessos Rápidos Mais Utilizados

### 1. Portabilidade e Compatibilidade de Plataformas
- **Observação Crítica sobre `%CONFIG%` vs `$CONFIG`:** [Guia de Portabilidade](arquitetura/portabilidade_linux_windows.md#atenção-crítica-variável-config-no-linux-e-windows)
- **Registro Detalhado da Issue de Resolução de Caminhos:** [Issue de Compatibilidade %CONFIG%](issues/compatibilidade_config_espanso.md)

### 2. Atendimento ao Usuário e Chamados
- **Como funciona o formulário mestre `:ola`:** [Atendimento e Respostas Rápidas](guias/atendimento_e_respostas_rapidas.md)
- **Procedimentos para Telefonia Celular (`:cel`):** [Suporte Telefonia Celular](guias/suporte_telefonia_celular.md)
- **Cálculo de Diárias e Formulários de Viagens:** [Viagens e Diárias](guias/viagens_e_diarias_terceirizados.md)

### 3. Engenharia e Automação
- **Funcionamento do Motor NLP e Siglas:** [Motor NLP e Dicionário](arquitetura/motor_nlp_e_dicionario.md)
- **Como executar os testes unitários e de integração:** [Suíte de Testes](testes/suite_de_testes_automatizados.md)

