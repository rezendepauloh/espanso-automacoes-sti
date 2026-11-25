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
│   └── sincronizacao_ambientes.md             # sync.sh (Linux) e sync.ps1 (Windows + Kando)
│
├── 🏛️ arquitetura/                            # Decisões fundamentais de engenharia
│   ├── gui_windows_wpf_ui.md                  # GUI nativa Windows (.NET 8 + WPF-UI + Win32)
│   ├── formularios_dinamicos_e_runner.md      # Fluxo multiplataforma (sti-forms / sti-forms.exe)
│   ├── portabilidade_linux_windows.md         # Padrões cross-platform e observação do %CONFIG%
│   └── plano_migracao_gui_nativa.md           # Roadmap e checklist da migração Rust/libcosmic e C#
│
├── 🧪 testes/                                 # Qualidade de software e integridade
│   └── suite_de_testes_automatizados.md       # Execução Python, PowerShell e xUnit (.NET 8)
│
└── 🚨 issues/                                 # Registro de compatibilidade e pendências
    └── compatibilidade_config_espanso.md      # Registro do comportamento de %CONFIG% vs $CONFIG
```

---

## 🚀 Acessos Rápidos Mais Utilizados

### 1. Instalação e Sincronização

- **Sincronizar Windows (`sync.ps1`) e Linux (`sync.sh`):** [Guia de Sincronização](guias/sincronizacao_ambientes.md)
- **Observação Crítica sobre `%CONFIG%` vs `$CONFIG`:** [Guia de Portabilidade](arquitetura/portabilidade_linux_windows.md#atenção-crítica-variável-config-no-linux-e-windows)
- **Registro da Issue de Resolução de Caminhos:** [Issue de Compatibilidade %CONFIG%](issues/compatibilidade_config_espanso.md)

### 2. Interfaces Gráficas Nativas & Atendimento

- **GUI Nativa Windows (.NET 8 + WPF-UI Fluent Mica):** [Arquitetura GUI Windows](arquitetura/gui_windows_wpf_ui.md)
- **Motor de Formulários Dinâmicos (Linux & Windows):** [Formulários Dinâmicos e Runners](arquitetura/formularios_dinamicos_e_runner.md)
- **Plano de Migração e Checklist:** [Plano de Migração GUI Nativa](arquitetura/plano_migracao_gui_nativa.md)
- **Como funciona o formulário mestre `:ola`:** [Atendimento e Respostas Rápidas](guias/atendimento_e_respostas_rapidas.md)

### 3. Testes e Qualidade

- **Como rodar Python, PowerShell e xUnit (`dotnet test`):** [Suíte de Testes](testes/suite_de_testes_automatizados.md)
