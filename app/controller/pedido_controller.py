from flask import (
    Blueprint, jsonify, render_template,
    request, session
)

from app.model.pedido import Pedido
from app.middleware import (
    login_obrigatorio,
    permissao_obrigatoria
)


pedido_bp = Blueprint("pedido_controller", __name__)


@pedido_bp.route("/pedido", methods=["GET"])
@login_obrigatorio
def pagina_pedidos():

    return render_template("pedidos.html")


@pedido_bp.route("/pedidos", methods=["POST"])
@login_obrigatorio
def criar_pedido():

    dados = request.get_json(silent=True) or {}

    itens = dados.get("itens", [])

    if not isinstance(itens, list) or not itens:
        return jsonify({
            "erro": "O pedido precisa ter pelo menos um item."
        }), 400

    try:

        pedido_id = Pedido.criar(
            session["usuario_id"],
            itens
        )

        return jsonify({
            "mensagem": "Pedido realizado com sucesso.",
            "pedido_id": pedido_id
        }), 201

    except (ValueError, TypeError):
        return jsonify({
            "erro": "Os itens ou as quantidades são inválidos."
        }), 400


@pedido_bp.route("/pedidos", methods=["GET"])
@login_obrigatorio
def listar_pedidos():

    if session.get("tipo") in ("administrador", "cozinheiro"):
        pedidos = Pedido.listar()
    else:
        pedidos = Pedido.listar_cliente(session["usuario_id"])

    return jsonify([
        dict(pedido) for pedido in pedidos
    ]), 200


@pedido_bp.route("/pedidos/<int:id>/status", methods=["PUT"])
@permissao_obrigatoria("cozinheiro", "administrador")
def atualizar_status(id):

    dados = request.get_json(silent=True) or {}

    status = dados.get("status")

    status_permitidos = [
        "Aguardando",
        "Iniciando Preparo",
        "Pronto para Entrega"
    ]

    if status not in status_permitidos:
        return jsonify({
            "erro": "Status inválido."
        }), 400

    alterados = Pedido.atualizar_status(id, status)

    if alterados == 0:
        return jsonify({
            "erro": "Pedido não encontrado."
        }), 404

    return jsonify({
        "mensagem": "Status atualizado com sucesso.",
        "status": status
    }), 200


@pedido_bp.route("/cozinheiro", methods=["GET"])
@permissao_obrigatoria("cozinheiro", "administrador")
def pagina_cozinheiro():

    return render_template("cozinha.html")