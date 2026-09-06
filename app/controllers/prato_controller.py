from model.prato import Prato

pratos = [
    Prato(
        1,
        "Hambúrguer com frango",
        "Hambúrguer com queijo e bacon",
        40.00
    ),

    Prato(
        2,
        "Marmitex simples",
        "Arroz e Feijão com strogonoff de frango",
        27.90
    ),

    Prato(
        3,
        "Super marmitex",
        "Arroz e Feijão acompanhado com lasanha, batata frita e salada",
        40.00
    )
]

def cardapio():
    return [prato.dicionario_js() for prato in pratos]


def buscar_prato(id):
    for prato in pratos:
        if prato.id == id:
            return prato.dicionario_js()
    return None