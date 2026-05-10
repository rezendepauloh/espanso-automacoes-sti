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
        f"Como a sua solicitação se trata de um pedido de <strong>{equipamento}</strong>, "
        f"sugiro realizar a abertura de um processo pelo Portal de Serviços "
        f"no link <a href=\"https://portaldeservicos.mpms.mp.br\">https://portaldeservicos.mpms.mp.br</a>.<br /><br />"
    )

    # ===============================
    # MATERIAL DE CONSUMO
    # ===============================
    if tipo_material == "consumo":
        print(
            "No portal, navegue pelos menus:<br />"
            "<strong>“Gestão Administrativa” -> “Solicitação de Material de Consumo”</strong>.<br /><br />"
            "Nos botões do topo, clique em <strong>“Solicitar”</strong>, depois em <strong>“Próximo”</strong>.<br /><br />"
        )

    # ===============================
    # MATERIAL PERMANENTE
    # ===============================
    elif tipo_material == "permanente":
        if defeito == "sim":
            print(
                "Como o material permanente está com defeito, "
                "o procedimento correto é realizar uma <strong>devolução com substituição</strong>.<br /><br />"
                "No portal, navegue pelos menus:<br />"
                "<strong>“Gestão Administrativa” -> “Devolução de Material Permanente”</strong>.<br /><br />"
                "No grupo <strong>“Motivo de Devolução”</strong>, selecione <strong>“Danificado”</strong> "
                "e em <strong>“Substituição”</strong>, selecione <strong>“Sim”</strong>.<br /><br />"
            )
        else:
            print(
                "No portal, navegue pelos menus:<br />"
                "<strong>“Gestão Administrativa” -> “Solicitação de Material Permanente”</strong>.<br /><br />"
            )

        if patrimonio:
            print(
                f"Digite <strong>{patrimonio}</strong> (Número do patrimônio do equipamento) no campo <strong>“Plaqueta”</strong> ou <strong>“Especificação”</strong> "
                "e clique em <strong>“Consultar”</strong>, selecionando o item correspondente.<br /><br />"
            )

    else:
        print("Tipo de material informado inválido.<br />")

    print(
        f"No campo <strong>“Observação/Justificativa”</strong>, descreva o motivo da solicitação "
        f"e informe o seu número de chamado conosco <strong>({chamado})</strong> para embasamento.<br /><br />"
        "Feito isso, basta prosseguir até gerar o processo e aguardar o atendimento."
    )

if __name__ == "__main__":
    main()