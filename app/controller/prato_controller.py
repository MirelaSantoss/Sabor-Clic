from flask import Blueprint, jsonify, render_template, request
from ..model.prato import Prato

prato_bp = Blueprint("prato", __name__)

# Nosso cardápio por enquanto
pratos = [
    Prato(1, "Hambúrguer com frango","Hambúrguer com queijo e bacon",40.00),
    Prato(2, "Marmitex simples", "Arroz e Feijão com strogonoff de frango",27.90),
    Prato(3,"Super marmitex","Arroz e Feijão acompanhado com lasanha, batata frita e salada",40.00)
]

# função para mostrar o cardápio
def cardapio():
    return [prato.dicionario_js() for prato in pratos]

# função para procurar por uma comida (pesquisando o id)
def buscar_prato(id):
    for prato in pratos:
        if prato.id == id:
            return prato.dicionario_js()
    return None


# Aqui tem todas as nossas rotas relacionadas aos pratos

@prato_bp.route("/cardapio", methods=["GET"])
def pagina_cardapio():
    return render_template("cardapio.html")


@prato_bp.route("/", methods=["GET"])
def inicio():
    return render_template("index.html")

@prato_bp.route("/pratos/<int:id>", methods=["GET"])
def consultar_prato(id):
    prato = buscar_prato(id)

    if prato:
        return jsonify(prato)


    return jsonify({"erro": "Prato não encontrado"}), 404



    