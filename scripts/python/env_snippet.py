#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera snippets simples do Espanso usando variáveis configuradas no .env."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from lib.utils import get_env, setup_utf8


def main():
    setup_utf8()
    if len(sys.argv) < 2:
        sys.exit(1)

    key = sys.argv[1].strip().lower()
    if key == "zap":
        whatsapp = get_env("STI_WHATSAPP_FUNCIONAL", "00 90000-0000")
        print(
            f"Se não conseguir enviar pelo Teams, pode tentar enviar no nosso telefone funcional via WhatsApp: {whatsapp}.",
            end="",
        )
    elif key == "portal":
        portal_url = get_env("STI_PORTAL_SERVICOS_URL", "https://portal.exemplo.gov.br")
        print(
            f"sugiro realizar a abertura de um processo pelo Portal de Serviços: {portal_url}",
            end="",
        )
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
