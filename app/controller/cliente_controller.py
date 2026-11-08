from flask import (
    Blueprint, request, render_template, session,
    redirect, url_for, flash, jsonify
)

import sqlite3

from app.model.cliente import Cliente
from app.middleware import login_obrigatorio


clientes_bp = Blueprint("cliente", __name__)


# ==================================================
# LOGIN
# ==================================================

@clientes_bp.route("/login", methods=["GET", "POST"])
def pagina_login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        usuario = Cliente.autenticar(email, senha)

        if usuario:

            session.clear()

            session["usuario_id"] = usuario["id"]
            session["usuario"] = usuario["nome"]
            session["tipo"] = usuario["tipo"]

            flash("Login realizado com sucesso!", "sucesso")

            return redirect(url_for("prato.pagina_cardapio"))

        flash("E-mail ou senha inválidos.", "erro")

    return render_template("login.html")


# ==================================================
# CADASTRO DE DADOS PESSOAIS
# ==================================================

@clientes_bp.route("/formulario", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":

        dados = {
            "nome": request.form.get("nome", "").strip(),
            "telefone": request.form.get("telefone", "").strip(),
            "cpf": request.form.get("cpf", "").strip(),
            "data_nascimento": request.form.get("data_nascimento", ""),
            "email": request.form.get("email", "").strip().lower(),
            "senha": request.form.get("senha", ""),
            "genero": request.form.get("genero", "")
        }

        # Verifica se os campos obrigatórios foram preenchidos.
        campos_obrigatorios = [
            dados["nome"],
            dados["telefone"],
            dados["cpf"],
            dados["data_nascimento"],
            dados["email"],
            dados["senha"]
        ]

        if not all(campos_obrigatorios):

            flash("Preencha todos os campos obrigatórios.", "erro")

            return render_template("cadastro.html")

        # Verifica o tamanho mínimo da senha.
        if len(dados["senha"]) < 8:

            flash("A senha deve ter pelo menos 8 caracteres.", "erro")

            return render_template("cadastro.html")

        try:

            # Salva os dados temporários no banco de dados.
            pending_id = Cliente.criar_cadastro_pendente(dados)

            # Guarda somente o ID na sessão.
            session["cadastro_pendente_id"] = pending_id

            return redirect(url_for("cliente.pagina_endereco"))

        except sqlite3.IntegrityError:

            flash("Este CPF ou e-mail já está cadastrado.", "erro")

            return render_template("cadastro.html")

        except Exception as erro:

            print("ERRO NO CADASTRO:", erro)

            flash("Não foi possível iniciar o cadastro.", "erro")

            return render_template("cadastro.html")

    # CORREÇÃO: permite abrir a página pelo método GET.
    return render_template("cadastro.html")


# ==================================================
# CADASTRO DE ENDEREÇO
# ==================================================

@clientes_bp.route("/endereco", methods=["GET", "POST"])
def pagina_endereco():

    pending_id = session.get("cadastro_pendente_id")

    if not pending_id:

        flash("Preencha seus dados pessoais primeiro.", "erro")

        return redirect(url_for("cliente.cadastro"))

    if request.method == "POST":

        endereco = {
            "rua": request.form.get("rua", "").strip(),
            "numero": request.form.get("numero", "").strip(),
            "bairro": request.form.get("bairro", "").strip(),
            "cidade": request.form.get("cidade", "").strip(),
            "estado": request.form.get("estado", "").strip(),
            "cep": request.form.get("cep", "").strip()
        }

        # Verifica se todos os campos foram preenchidos.
        if not all(endereco.values()):

            flash("Preencha todos os campos do endereço.", "erro")

            return render_template("endereco.html")

        try:

            # Finaliza o cadastro no banco de dados.
            Cliente.cadastrar(pending_id, endereco)

            # Remove o identificador temporário da sessão.
            session.pop("cadastro_pendente_id", None)

            flash(
                "Cadastro realizado com sucesso! Faça seu login.",
                "sucesso"
            )

            return redirect(url_for("cliente.pagina_login"))

        except sqlite3.IntegrityError as erro:

            print("ERRO DE INTEGRIDADE:", erro)

            session.pop("cadastro_pendente_id", None)

            flash(
                "Este CPF ou e-mail já está cadastrado.",
                "erro"
            )

            return redirect(url_for("cliente.cadastro"))

        except Exception as erro:

            print("ERRO NO CADASTRO:", erro)

            flash(
                "Não foi possível realizar o cadastro.",
                "erro"
            )

            return render_template("endereco.html")

    return render_template("endereco.html")


# ==================================================
# LOGOUT
# ==================================================

@clientes_bp.route("/logout", methods=["POST"])
def logout():

    session.clear()

    flash("Você saiu da sua conta.", "sucesso")

    return redirect(url_for("cliente.pagina_login"))


# ==================================================
# MINHA CONTA
# ==================================================

@clientes_bp.route("/minha-conta", methods=["GET"])
@login_obrigatorio
def minha_conta():

    usuario = Cliente.buscar_por_id(session["usuario_id"])

    if usuario is None:

        session.clear()

        return jsonify({
            "erro": "Usuário não encontrado."
        }), 404

    return jsonify(dict(usuario)), 200