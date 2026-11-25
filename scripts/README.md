# 💻 Diretório Principal de Scripts e Automações

Este é o coração executivo do projeto. Ele contém toda a lógica em **Python** e **PowerShell** utilizada para manipular texto, processar formulários, interagir com o clipboard (área de transferência), limpar PDFs e integrar ferramentas externas (Kando e CopyQ).

## 📁 Subdiretórios

* **[python/](python/)**: Contém todos os scripts executivos em Python (.py), incluindo geradores de templates, processadores de texto com NLP e utilitários de manutenção do Kando.
* **[powershell/](powershell/)**: Contém os scripts executores PowerShell (.ps1) de clipboard (caixa alta, caixa baixa, correção ortográfica e limpeza de PDF).
* **[lib/](lib/)**: Bibliotecas compartilhadas (Python e PowerShell) e o banco de dados do dicionário centralizado em formato JSON.
* **[textos/](textos/)**: Modelos e arquivos HTML/texto puro que servem como templates de e-mail e respostas formais para atendimentos de suporte.
* **[kando/](kando/)**: Automações, scripts de janelas, chamadas de atalhos e configurações do menu radial **Kando**.
* **[tests/](tests/)**: Suíte de testes unitários automatizados para garantir integridade e regressão zero no projeto.
* **[copyq/](copyq/)**: Scripts de integração com o gerenciador de área de transferência **CopyQ**.
