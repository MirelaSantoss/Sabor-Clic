import os
import uuid
from pathlib import Path
from flask import Blueprint, render_template, jsonify, request, current_app
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from app.middleware import permissao_obrigatoria
from app.db import conectar
from app.model.prato import Prato

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
        con = conectar()
        dados = [dict(x) for x in con.execute("SELECT * FROM pratos ORDER BY id DESC")]
        con.close()
        return jsonify(dados)
    try:
        dados = request.form
        nome = dados.get("nome", "").strip()
        descricao = dados.get("descricao", "").strip()
        preco = float(dados.get("preco", "0").replace(",", "."))
        categoria = dados.get("categoria", "Pratos")
        if not nome or not descricao or preco <= 0 or categoria not in ("Pratos", "Bebidas", "Combos", "Sobremesas"):
            raise ValueError("Confira os dados do produto.")
        imagem = salvar_foto(request.files.get("imagem"))
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
        nome = str(dados.get("nome", prato["nome"])).strip()
        descricao = str(dados.get("descricao", prato["descricao"])).strip()
        preco = float(dados.get("preco", prato["preco"]))
        categoria = dados.get("categoria", prato["categoria"])
        if not nome or not descricao or preco <= 0 or categoria not in ("Pratos", "Bebidas", "Combos", "Sobremesas"):
            raise ValueError("Dados inválidos")
        Prato.atualizar(id, nome, descricao, preco, int(bool(dados.get("ativo", prato["ativo"]))), categoria)
        return jsonify({"mensagem": "Produto atualizado"})
    except (ValueError, TypeError) as erro:
        return jsonify({"erro": str(erro)}), 400

@admin_bp.route("/api/admin/relatorio")
@permissao_obrigatoria("administrador")
def relatorio():
    con = conectar()
    resumo = dict(con.execute("SELECT COUNT(*) AS pedidos, COALESCE(SUM(total),0) AS faturamento FROM pedidos").fetchone())
    resumo["funcionarios"] = [dict(x) for x in con.execute("SELECT id,nome,email,tipo FROM clientes WHERE tipo IN ('administrador','cozinheiro')")]
    con.close()
    return jsonify(resumo)
