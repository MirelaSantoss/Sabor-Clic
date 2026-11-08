from flask import (
    Blueprint, jsonify, render_template,
    request, flash, redirect, url_for
)

from app.model.prato import Prato
from app.middleware import permissao_obrigatoria


prato_bp = Blueprint("prato", __name__)


@prato_bp.route("/", methods=["GET"])
def inicio():

    return render_template("index.html")


@prato_bp.route("/cardapio", methods=["GET"])
def pagina_cardapio():

    return render_template("cardapio.html")


@prato_bp.route("/api/pratos", methods=["GET"])
def listar_pratos():

    pratos = Prato.listar()

    return jsonify([
        dict(prato) for prato in pratos
    ]), 200


@prato_bp.route("/pratos/<int:id>", methods=["GET"])
def consultar_prato(id):

    prato = Prato.buscar(id)

    if prato is None:
        return jsonify({"erro": "Prato não encontrado."}), 404

    return jsonify(dict(prato)), 200


@prato_bp.route("/api/pratos", methods=["POST"])
@permissao_obrigatoria("administrador")
def cadastrar_prato():

    dados = request.get_json(silent=True) or {}

    nome = dados.get("nome", "").strip()
    descricao = dados.get("descricao", "").strip()

    try:
        preco = float(dados.get("preco", 0))
    except (TypeError, ValueError):
        return jsonify({"erro": "Preço inválido."}), 400

    if not nome or not descricao or preco <= 0:
        return jsonify({"erro": "Informe os dados corretamente."}), 400

    id_prato = Prato.cadastrar(nome, descricao, preco)

    return jsonify({
        "mensagem": "Prato cadastrado com sucesso.",
        "id": id_prato
    }), 201


@prato_bp.route("/api/pratos/<int:id>", methods=["PUT"])
@permissao_obrigatoria("administrador")
def editar_prato(id):

    dados = request.get_json(silent=True) or {}

    nome = dados.get("nome", "").strip()
    descricao = dados.get("descricao", "").strip()

    try:
        preco = float(dados.get("preco", 0))
    except (TypeError, ValueError):
        return jsonify({"erro": "Preço inválido."}), 400

    if not nome or not descricao or preco <= 0:
        return jsonify({"erro": "Dados inválidos."}), 400

    ativo = 1 if dados.get("ativo", True) else 0

    Prato.atualizar(id, nome, descricao, preco, ativo)

    return jsonify({"mensagem": "Prato atualizado."}), 200


@prato_bp.route("/api/pratos/<int:id>", methods=["DELETE"])
@permissao_obrigatoria("administrador")
def excluir_prato(id):

    prato = Prato.buscar(id)

    if prato is None:
        return jsonify({"erro": "Prato não encontrado."}), 404

    Prato.excluir(id)

    return jsonify({"mensagem": "Prato desativado."}), 200