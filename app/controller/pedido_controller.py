from flask import Blueprint, jsonify, request
from model.pedido import Pedido
from model.cliente import Cliente
from model.endereco import Endereco
from model.prato import Prato

pedido_bp = ("pedido_controller", __name__)

pedidos = []


@pedido_bp.route("/pedidos", methods=["POST"])
def criar_pedido():
    dados = request.json

    cliente = Cliente(
        dados["cliente"]["nome"],
        dados["cliente"]["telefone"]
    )

    endereco = Endereco(
        dados["endereco"]["rua"],
        dados["endereco"]["numero"],
        dados["endereco"]["bairro"]
    )

    itens = []

    for item in dados["itens"]:
        prato = Prato(item["nome"], item["preco"])
        itens.append(prato)

    pedido = Pedido(cliente, endereco, itens)
    pedidos.append(pedido)

    return jsonify(pedido.to_dict()), 201


@pedido_bp.route("/pedidos", methods=["GET"])
def listar_pedidos():
    lista = []

    for pedido in pedidos:
        lista.append(pedido.to_dict())

    return jsonify(lista), 200


@pedido_bp.route("/pedidos/<int:id>/iniciar-preparo", methods=["PUT"])
def iniciar_preparo(id):
    pedido_encontrado = None

    for pedido in pedidos:
        if pedido.id == id:
            pedido_encontrado = pedido
            break

    if pedido_encontrado is None:
        return jsonify({"erro": "Pedido não encontrado"}), 404

    pedido_encontrado.iniciar_preparo()

    return jsonify(pedido_encontrado.pedido_dicionario()), 200


