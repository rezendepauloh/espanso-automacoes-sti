# 🐚 Diretório de Scripts PowerShell (scripts/powershell)

Este diretório contém os scripts executivos em **PowerShell** (.ps1). Cada script é responsável por manipular e tratar o conteúdo da área de transferência (clipboard) do Windows de forma instantânea e silenciosa.

## 📄 Arquivos

### [arrumar.ps1](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/powershell/arrumar.ps1)
* **Função**: Corretor ortográfico rápido de clipboard.
* **O que faz**:
  * Captura o texto presente na área de transferência.
  * Executa a rotina de correção usando o dicionário central [dicionario.json](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/lib/dicionario.json).
  * Corrige a pontuação básica e capitalizações de siglas (ex: `mpms` -> `MPMS`).
  * Atualiza a área de transferência com o resultado e aciona o atalho de colagem automática.

### [limpa_pdf.ps1](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/powershell/limpa_pdf.ps1)
* **Função**: Limpeza inteligente de textos copiados de PDFs.
* **O que faz**:
  * Captura o texto copiado de relatórios, sentenças ou documentos PDF (que costumam vir cheios de quebras de linha artificiais e palavras cortadas por hífens).
  * Executa o algoritmo `Clean-PdfText` da biblioteca central para unificar os parágrafos de forma inteligente, preservando pontuações e abreviações (como `art.`).
  * Atualiza a área de transferência com o parágrafo fluído e limpo e cola no local do cursor.

### [maiuscula.ps1](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/powershell/maiuscula.ps1)
* **Função**: Conversor rápido de texto para Caixa Alta (UPPERCASE).
* **O que faz**: Converte todo o texto presente no clipboard do Windows para letras maiúsculas de forma instantânea e cola o resultado.

### [minuscula.ps1](file:///c:/Users/paulogoncalves/AppData/Roaming/espanso/scripts/powershell/minuscula.ps1)
* **Função**: Conversor rápido de texto para Caixa Baixa (lowercase).
* **O que faz**: Converte todo o texto presente no clipboard do Windows para letras minúsculas de forma instantânea e cola o resultado.
