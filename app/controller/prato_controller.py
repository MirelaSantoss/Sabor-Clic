from flask import (
    Blueprint, jsonify, render_template,
    request, session
)

from app.model.prato import Prato
from app.middleware import (
    permissao_obrigatoria,
    login_obrigatorio,
    limpar_texto,
    nome_prato_valido,
    converter_preco,
    converter_ativo,
    CATEGORIAS_VALIDAS
)


prato_bp = Blueprint("prato", __name__)


@prato_bp.route("/", methods=["GET"])
def inicio():
    return render_template("index.html")


@prato_bp.route("/cardapio", methods=["GET"])
@login_obrigatorio
def pagina_cardapio():
    return render_template("cardapio.html")


@prato_bp.route("/api/pratos", methods=["GET"])
def listar_pratos():
    pratos = Prato.listar()
    return jsonify([dict(prato) for prato in pratos]), 200


@prato_bp.route("/pratos/<int:id>", methods=["GET"])
def consultar_prato(id):
    prato = Prato.buscar(id)

    if prato is None:
        return jsonify({"erro": "Prato não encontrado."}), 404

    if not prato["ativo"] and session.get("tipo") != "administrador":
        return jsonify({"erro": "Prato não encontrado."}), 404

    return jsonify(dict(prato)), 200


@prato_bp.route("/api/pratos", methods=["POST"])
@permissao_obrigatoria("administrador")
def cadastrar_prato():
    dados = request.get_json(silent=True) or {}

    nome = limpar_texto(dados.get("nome", ""))
    descricao = limpar_texto(dados.get("descricao", ""))
    categoria = limpar_texto(dados.get("categoria", "Pratos")) or "Pratos"

    try:
        preco = converter_preco(dados.get("preco"))
    except (TypeError, ValueError):
        return jsonify({"erro": "Preço inválido."}), 400

    if not nome_prato_valido(nome):
        return jsonify({"erro": "O nome do prato deve ter entre 3 e 120 caracteres."}), 400

    if not descricao or categoria not in CATEGORIAS_VALIDAS:
        return jsonify({"erro": "Informe os dados corretamente."}), 400

    id_prato = Prato.cadastrar(nome, descricao, preco, categoria)

    return jsonify({
        "mensagem": "Prato cadastrado com sucesso.",
        "id": id_prato
    }), 201


@prato_bp.route("/api/pratos/<int:id>", methods=["PUT"])
@permissao_obrigatoria("administrador")
def editar_prato(id):
    prato_atual = Prato.buscar(id)
    if prato_atual is None:
        return jsonify({"erro": "Prato não encontrado."}), 404

    dados = request.get_json(silent=True) or {}

    nome = limpar_texto(dados.get("nome", prato_atual["nome"]))
    descricao = limpar_texto(dados.get("descricao", prato_atual["descricao"]))
    categoria = limpar_texto(dados.get("categoria", prato_atual["categoria"])) or prato_atual["categoria"]

    try:
        preco = converter_preco(dados.get("preco", prato_atual["preco"]))
    except (TypeError, ValueError):
        return jsonify({"erro": "Preço inválido."}), 400

    if not nome_prato_valido(nome):
        return jsonify({"erro": "O nome do prato deve ter entre 3 e 120 caracteres."}), 400

    if not descricao or categoria not in CATEGORIAS_VALIDAS:
        return jsonify({"erro": "Dados inválidos."}), 400

    ativo = converter_ativo(dados.get("ativo"), prato_atual["ativo"])

    Prato.atualizar(id, nome, descricao, preco, ativo, categoria)

    return jsonify({"mensagem": "Prato atualizado."}), 200


@prato_bp.route("/api/pratos/<int:id>", methods=["DELETE"])
@permissao_obrigatoria("administrador")
def excluir_prato(id):
    prato = Prato.buscar(id)

    if prato is None:
        return jsonify({"erro": "Prato não encontrado."}), 404

    Prato.excluir(id)

    return jsonify({"mensagem": "Prato desativado."}), 200
