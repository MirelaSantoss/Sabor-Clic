import sqlite3
from flask import (
    Blueprint, request, render_template, session,
    redirect, url_for, flash, jsonify
)

from app.model.cliente import Cliente
from app.model.endereco import Endereco
from app.model.bancada import Bancada
from app.middleware import (
    login_obrigatorio, permissao_obrigatoria, _destino_padrao,
    limpar_texto, email_valido, senha_valida
)

clientes_bp = Blueprint("cliente", __name__)


@clientes_bp.route("/login", methods=["GET", "POST"])
def pagina_login():
    if "usuario_id" in session:
        return redirect(_destino_padrao(session.get("tipo")))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        usuario = Cliente.autenticar(email, senha)

        if usuario:
            session.clear()
            session.permanent = True
            session["usuario_id"] = usuario["id"]
            session["usuario"] = usuario["nome"]
            session["tipo"] = usuario["tipo"]

            flash("Login realizado com sucesso!", "sucesso")
            return redirect(_destino_padrao(usuario["tipo"]))

        flash("E-mail ou senha inválidos.", "erro")

    return render_template("login.html")


@clientes_bp.route("/formulario", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        dados = {
            "nome": limpar_texto(request.form.get("nome", "")),
            "telefone": limpar_texto(request.form.get("telefone", "")),
            "cpf": limpar_texto(request.form.get("cpf", "")),
            "data_nascimento": limpar_texto(request.form.get("data_nascimento", "")),
            "email": limpar_texto(request.form.get("email", "")).lower(),
            "senha": request.form.get("senha", ""),
            "genero": limpar_texto(request.form.get("genero", ""))
        }

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

        if not email_valido(dados["email"]):
            flash("Informe um e-mail válido com no máximo 120 caracteres.", "erro")
            return render_template("cadastro.html")

        if not senha_valida(dados["senha"]):
            flash("A senha deve ter pelo menos 8 caracteres, misturando letras e números.", "erro")
            return render_template("cadastro.html")

        try:
            pending_id = Cliente.criar_cadastro_pendente(dados)
            session["cadastro_pendente_id"] = pending_id
            return redirect(url_for("cliente.pagina_endereco"))

        except sqlite3.IntegrityError:
            flash("Este CPF ou e-mail já está cadastrado.", "erro")
            return render_template("cadastro.html")

        except ValueError as erro:
            flash(str(erro), "erro")
            return render_template("cadastro.html")

        except Exception:
            flash("Não foi possível iniciar o cadastro.", "erro")
            return render_template("cadastro.html")

    return render_template("cadastro.html")


@clientes_bp.route("/endereco", methods=["GET", "POST"])
def pagina_endereco():
    pending_id = session.get("cadastro_pendente_id")

    if not pending_id:
        flash("Preencha seus dados pessoais primeiro.", "erro")
        return redirect(url_for("cliente.cadastro"))

    if request.method == "POST":
        obj_endereco = Endereco(
            request.form.get("rua", ""),
            request.form.get("numero", ""),
            request.form.get("bairro", ""),
            request.form.get("cidade", ""),
            request.form.get("estado", ""),
            request.form.get("cep", "")
        )

        if not obj_endereco.valido():
            flash("Preencha todos os campos do endereço.", "erro")
            return render_template("endereco.html")

        try:
            Cliente.cadastrar(pending_id, obj_endereco)
            session.pop("cadastro_pendente_id", None)
            flash("Cadastro realizado com sucesso! Faça seu login.", "sucesso")
            return redirect(url_for("cliente.pagina_login"))

        except sqlite3.IntegrityError:
            session.pop("cadastro_pendente_id", None)
            flash("Este CPF ou e-mail já está cadastrado.", "erro")
            return redirect(url_for("cliente.cadastro"))

        except Exception:
            flash("Não foi possível realizar o cadastro.", "erro")
            return render_template("endereco.html")

    return render_template("endereco.html")


@clientes_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Você saiu da sua conta.", "sucesso")
    return redirect(url_for("cliente.pagina_login"))


@clientes_bp.route("/minha-conta", methods=["GET"])
@login_obrigatorio
def minha_conta():
    usuario = Cliente.buscar_por_id(session["usuario_id"])

    if usuario is None:
        session.clear()
        return jsonify({"erro": "Usuário não encontrado."}), 404

    return jsonify(dict(usuario)), 200


@clientes_bp.route("/carrinho", methods=["GET"])
@permissao_obrigatoria("cliente")
def carrinho():
    return render_template("carrinho.html")


@clientes_bp.route("/bancadas", methods=["GET"])
@permissao_obrigatoria("cliente")
def pagina_bancadas():
    return render_template("bancadas.html")


@clientes_bp.route("/api/bancadas", methods=["GET"])
def listar_bancadas():
    apenas_disp = session.get("tipo") != "administrador"
    return jsonify(Bancada.listar(apenas_disponiveis=apenas_disp)), 200


@clientes_bp.route("/api/bancadas/agenda", methods=["GET"])
@login_obrigatorio
def agenda_ocupacao_bancadas():
    bancada_id = request.args.get("bancada_id")
    data_filtro = request.args.get("data")
    eh_admin = session.get("tipo") == "administrador"
    try:
        agenda = Bancada.agenda_ocupacao(
            bancada_id=bancada_id if bancada_id else None,
            data_filtro=data_filtro if data_filtro else None,
            incluir_cliente=eh_admin
        )
        return jsonify(agenda), 200
    except (ValueError, TypeError) as erro:
        return jsonify({"erro": str(erro)}), 400


@clientes_bp.route("/api/bancadas/reservas", methods=["GET", "POST"])
@login_obrigatorio
def reservas_bancadas():
    if request.method == "GET":
        if session.get("tipo") == "administrador":
            return jsonify(Bancada.listar_reservas()), 200
        if session.get("tipo") == "cliente":
            return jsonify(Bancada.listar_reservas(session["usuario_id"])), 200
        return jsonify({"erro": "Você não possui permissão para esta ação."}), 403

    if session.get("tipo") != "cliente":
        return jsonify({"erro": "Somente clientes podem agendar bancadas."}), 403

    dados = request.get_json(silent=True) or {}
    try:
        bancada_id = dados.get("id_bancada", dados.get("bancada_id"))
        inicio = dados.get("data_hora_inicio", "")
        fim = dados.get("data_hora_fim", "")
        if not bancada_id or not inicio or not fim:
            raise ValueError("Informe a bancada, data/hora de início e data/hora de fim.")
        resultado = Bancada.criar_reserva(session["usuario_id"], bancada_id, inicio, fim)
        resultado["mensagem"] = "Reserva de bancada confirmada com sucesso!"
        return jsonify(resultado), 201
    except (ValueError, TypeError) as erro:
        return jsonify({"erro": str(erro)}), 400


@clientes_bp.route("/api/bancadas/reservas/<int:id>", methods=["PUT", "DELETE"])
@permissao_obrigatoria("cliente")
def editar_ou_cancelar_reserva_cliente(id):
    try:
        if request.method == "DELETE":
            resultado = Bancada.atualizar_reserva_cliente(
                id,
                session["usuario_id"],
                cancelar=True
            )
            resultado["mensagem"] = "Reserva cancelada com sucesso."
            return jsonify(resultado), 200

        dados = request.get_json(silent=True) or {}
        atualizada = Bancada.atualizar_reserva_cliente(
            id,
            session["usuario_id"],
            bancada_id=dados.get("bancada_id", dados.get("id_bancada")),
            data_hora_inicio=dados.get("data_hora_inicio"),
            data_hora_fim=dados.get("data_hora_fim"),
            cancelar=bool(dados.get("cancelar"))
        )
        atualizada["mensagem"] = "Reserva reagendada com sucesso!"
        return jsonify(atualizada), 200
    except PermissionError as erro:
        return jsonify({"erro": str(erro)}), 403
    except (ValueError, TypeError) as erro:
        return jsonify({"erro": str(erro)}), 400
