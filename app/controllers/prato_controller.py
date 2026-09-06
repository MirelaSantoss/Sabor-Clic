from flask import jsonify, render_template
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

def configurar_rotas(app):

    @app.route("/cardapio", methods=["GET"])
    def pagina_cardapio():
        return render_template("index.html")


    @app.route("/", methods=["GET"])
    def listar_pratos():
        return jsonify(cardapio())

    @app.route("/pratos/<int:id>", methods=["GET"])
    def consultar_prato(id):
        prato = buscar_prato(id)

        if prato:
            return jsonify(prato)


        return jsonify({"erro": "Prato não encontrado"}), 404

    