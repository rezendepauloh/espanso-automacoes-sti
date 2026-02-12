# -*- coding: utf-8 -*-
import sys
import io

# 🔴 FORÇA UTF-8 NO STDOUT (ESSENCIAL NO WINDOWS)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def normaliza(txt):
    return txt.strip().lower()

def main():
    if len(sys.argv) < 6:
        print("Dados insuficientes para gerar a resposta.")
        return

    equipamento = sys.argv[1]
    tipo_material = normaliza(sys.argv[2])
    defeito = normaliza(sys.argv[3])
    patrimonio = sys.argv[4]
    chamado = sys.argv[5]

    print(
        f"Como a sua solicitação se trata de um pedido de {equipamento}, "
        f"sugiro realizar a abertura de um processo pelo Portal de Serviços "
        f"no link https://portaldeservicos.mpms.mp.br.\n"
    )

    # ===============================
    # MATERIAL DE CONSUMO
    # ===============================
    if tipo_material == "consumo":
        print(
            "No portal, navegue pelos menus:\n\n"
            "“Gestão Administrativa” -> “Solicitação de Material de Consumo”.\n"
            "Nos botões do topo, clique em “Solicitar”, depois em “Próximo”.\n"
        )

    # ===============================
    # MATERIAL PERMANENTE
    # ===============================
    elif tipo_material == "permanente":
        if defeito == "sim":
            print(
                "Como o material permanente está com defeito, "
                "o procedimento correto é realizar uma devolução com substituição.\n\n"
                "No portal, navegue pelos menus:\n"
                "“Gestão Administrativa” -> “Devolução de Material Permanente”.\n\n"
                "No grupo “Motivo de Devolução”, selecione “Danificado” "
                "e em “Substituição”, selecione “Sim”.\n"
            )
        else:
            print(
                "No portal, navegue pelos menus:\n"
                "“Gestão Administrativa” -> “Solicitação de Material Permanente”.\n"
            )

        if patrimonio:
            print(
                f"\nDigite {patrimonio} (Número do patrimônio do equipamento) no campo “Plaqueta” ou “Especificação” "
                "e clique em “Consultar”, selecionando o item correspondente.\n"
            )

    else:
        print("Tipo de material informado inválido.\n")

    print(
        f"\nNo campo “Observação/Justificativa”, descreva o motivo da solicitação "
        f"e informe o número do chamado ({chamado}).\n\n"
        "Feito isso, basta prosseguir até gerar o processo e aguardar o atendimento."
    )

if __name__ == "__main__":
    main()