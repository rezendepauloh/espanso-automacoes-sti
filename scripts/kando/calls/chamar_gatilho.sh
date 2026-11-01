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

# Se chamar_espanso_acao existir no PATH ou em ~/.local/bin, delega a ele
if command -v chamar_espanso_acao >/dev/null 2>&1; then
    exec chamar_espanso_acao "$ACAO"
elif [ -x "$HOME/.local/bin/chamar_espanso_acao" ]; then
    exec "$HOME/.local/bin/chamar_espanso_acao" "$ACAO"
else
    # Fallback: executa script python correspondente se existir
    CONFIG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
    SCRIPT_PY="$CONFIG_DIR/scripts/python/${ACAO}.py"
    if [ -f "$SCRIPT_PY" ]; then
        python3 "$SCRIPT_PY"
    fi
fi
