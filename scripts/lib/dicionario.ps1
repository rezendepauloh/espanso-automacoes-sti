# Arquivo: dicionario.ps1
# Banco de dados de correções carregado dinamicamente do JSON centralizado

$global:meuDicionario = @{}

$caminhoJson = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "dicionario.json"

if (Test-Path $caminhoJson) {
    try {
        $jsonText = Get-Content -Raw -Path $caminhoJson -Encoding utf8
        $dados = ConvertFrom-Json $jsonText
        
        # Converte o PSCustomObject do JSON para Hashtable nativa (performance)
        foreach ($prop in $dados.PSObject.Properties) {
            $global:meuDicionario[$prop.Name] = $prop.Value
        }
    } catch {
        Write-Error "Erro ao carregar o dicionário JSON: $_"
    }
} else {
    Write-Warning "Dicionário JSON não encontrado em: $caminhoJson"
}