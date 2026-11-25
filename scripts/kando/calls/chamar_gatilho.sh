#!/bin/bash
# ==============================================================================
# Script unificado em Bash para acionar atalhos e formulários do Espanso via Kando no Linux
# ==============================================================================
GATILHO="$1"

if [ -z "$GATILHO" ]; then
    echo "Uso: $0 <gatilho_ou_acao>"
    exit 1
fi

# Mapeamento de gatilhos do Espanso para ações diretas
case "$GATILHO" in
    :tmat|:transdevo|transporte_material)
        ACAO="transporte_material"
        ;;
    :turb|transporte_urbano)
        ACAO="transporte_urbano"
        ;;
    :dev|devolucao_chamado)
        ACAO="devolucao_chamado"
        ;;
    :diaria|diaria_viagem)
        ACAO="diaria_viagem"
        ;;
    :tvia|transporte_viagem)
        ACAO="transporte_viagem"
        ;;
    :ola|ola)
        ACAO="ola"
        ;;
    :cel|celular)
        ACAO="celular"
        ;;
    :ia|ia_arrumar)
        ACAO="ia_arrumar"
        ;;
    :min|minuscula)
        ACAO="minuscula"
        ;;
    :mai|maiuscula)
        ACAO="maiuscula"
        ;;
    *)
        ACAO="$GATILHO"
        ;;
esac

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
CONFIG_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Prioriza o despachante versionado do repositório, mantendo fallback para ~/.local/bin
if [ -x "$SCRIPT_DIR/chamar_acao.sh" ]; then
    exec "$SCRIPT_DIR/chamar_acao.sh" "$ACAO"
elif command -v chamar_espanso_acao >/dev/null 2>&1; then
    exec chamar_espanso_acao "$ACAO"
elif [ -x "$HOME/.local/bin/chamar_espanso_acao" ]; then
    exec "$HOME/.local/bin/chamar_espanso_acao" "$ACAO"
else
    SCRIPT_PY="$CONFIG_DIR/scripts/python/${ACAO}.py"
    if [ -f "$SCRIPT_PY" ]; then
        python3 "$SCRIPT_PY" --kando
    fi
fi
