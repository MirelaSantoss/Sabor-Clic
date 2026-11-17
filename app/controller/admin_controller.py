import uuid
from pathlib import Path
from flask import Blueprint, render_template, jsonify, request, current_app
from werkzeug.utils import secure_filename
from app.middleware import (
    permissao_obrigatoria,
    limpar_texto,
    nome_prato_valido,
    converter_preco,
    converter_ativo,
    CATEGORIAS_VALIDAS
)
from app.model.prato import Prato
from app.model.cliente import Cliente
from app.model.pedido import Pedido
from app.model.bancada import Bancada

admin_bp = Blueprint("admin", __name__)
EXTENSOES = {"jpg", "jpeg", "png", "webp"}


def salvar_foto(arquivo):
    if not arquivo or not arquivo.filename:
        return None
    nome = secure_filename(arquivo.filename)
    if "." not in nome or nome.rsplit(".", 1)[-1].lower() not in EXTENSOES:
        raise ValueError("Envie uma foto JPG, PNG ou WEBP.")
    pasta = Path(current_app.static_folder) / "uploads"
    pasta.mkdir(exist_ok=True)
    novo_nome = uuid.uuid4().hex + "." + nome.rsplit(".", 1)[-1].lower()
    arquivo.save(pasta / novo_nome)
    return "uploads/" + novo_nome


@admin_bp.route("/admin")
@permissao_obrigatoria("administrador")
def painel():
    return render_template("admin.html")


@admin_bp.route("/api/admin/pratos", methods=["GET", "POST"])
@permissao_obrigatoria("administrador")
def pratos():
    if request.method == "GET":
        return jsonify(Prato.listar_todos())
    try:
        dados = request.form if request.form else (request.get_json(silent=True) or {})
        nome = limpar_texto(dados.get("nome", ""))
        descricao = limpar_texto(dados.get("descricao", ""))
        preco = converter_preco(dados.get("preco"))
        categoria = limpar_texto(dados.get("categoria", "Pratos")) or "Pratos"
        if not nome_prato_valido(nome):
            raise ValueError("O nome do prato deve ter entre 3 e 120 caracteres.")
        if not descricao or categoria not in CATEGORIAS_VALIDAS:
            raise ValueError("Confira os dados do produto.")
        imagem = salvar_foto(request.files.get("imagem")) if request.files else None
        novo = Prato.cadastrar(nome, descricao, preco, categoria, imagem)
        return jsonify({"id": novo, "mensagem": "Produto cadastrado!"}), 201
    except (ValueError, TypeError) as erro:
        return jsonify({"erro": str(erro)}), 400


@admin_bp.route("/api/admin/pratos/<int:id>", methods=["PUT", "DELETE"])
@permissao_obrigatoria("administrador")
def editar_prato(id):
    prato = Prato.buscar(id)
    if not prato:
        return jsonify({"erro": "Produto não encontrado"}), 404
    if request.method == "DELETE":
        Prato.excluir(id)
        return jsonify({"mensagem": "Produto desativado"})
    dados = request.get_json(silent=True) or {}
    try:
        nome = limpar_texto(dados.get("nome", prato["nome"]))
        descricao = limpar_texto(dados.get("descricao", prato["descricao"]))
        preco = converter_preco(dados.get("preco", prato["preco"]))
        categoria = limpar_texto(dados.get("categoria", prato["categoria"])) or prato["categoria"]
        ativo = converter_ativo(dados.get("ativo"), prato["ativo"])
        if not nome_prato_valido(nome):
            raise ValueError("O nome do prato deve ter entre 3 e 120 caracteres.")
        if not descricao or categoria not in CATEGORIAS_VALIDAS:
            raise ValueError("Dados inválidos")
        Prato.atualizar(id, nome, descricao, preco, ativo, categoria)
        return jsonify({"mensagem": "Produto atualizado"})
    except (ValueError, TypeError) as erro:
        return jsonify({"erro": str(erro)}), 400


@admin_bp.route("/api/admin/funcionarios", methods=["POST"])
@permissao_obrigatoria("administrador")
def cadastrar_funcionario():
    dados = request.get_json(silent=True) or {}
    try:
        novo_id = Cliente.cadastrar_funcionario(
            dados.get("nome", ""),
            dados.get("email", ""),
            dados.get("senha", ""),
            dados.get("tipo", ""),
            dados.get("telefone")
        )
        return jsonify({"id": novo_id, "mensagem": "Funcionário cadastrado com sucesso!"}), 201
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400


@admin_bp.route("/api/admin/relatorio")
@permissao_obrigatoria("administrador")
def relatorio():
    resumo = Pedido.resumo_vendas()
    resumo["funcionarios"] = Cliente.listar_funcionarios()
    resumo["bancadas"] = Bancada.listar()
    resumo["reservas_bancadas"] = Bancada.listar_reservas()
    return jsonify(resumo)


@admin_bp.route("/api/bancadas/<int:id>", methods=["PUT"])
@admin_bp.route("/api/admin/bancadas/<int:id>", methods=["PUT"])
@permissao_obrigatoria("administrador")
def atualizar_bancada(id):
    dados = request.get_json(silent=True) or {}
    try:
        bancada = Bancada.buscar(id)
        if not bancada:
            return jsonify({"erro": "Bancada não encontrada."}), 404
        Bancada.atualizar(
            id,
            dados.get("valor_hora", bancada["valor_hora"]),
            dados.get("valor_caucao", bancada["valor_caucao"]),
            dados.get("descricao", bancada["descricao"]),
            dados.get("status_operacional", bancada["status_operacional"])
        )
        return jsonify({"mensagem": "Bancada atualizada com sucesso."}), 200
    except (ValueError, TypeError) as erro:
        return jsonify({"erro": str(erro)}), 400
