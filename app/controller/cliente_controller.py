from flask import Blueprint, request, render_template, session, redirect, url_for, flash
from ..model.cliente import Cliente
from ..model.endereco import Endereco

clientes_bp = Blueprint("cliente", __name__)

clientes = []

#rota para login 
@clientes_bp.route("/login", methods=["GET"])
def pagina_login():
    return render_template("login.html")


@clientes_bp.route("/formulario", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":

        # Guarda os dados pessoais na session
        session["dados_cliente"] = {
            "nome": request.form["nome"],
            "telefone": request.form["telefone"],
            "cpf": request.form["cpf"],
            "data_nascimento": request.form["data_nascimento"],
            "email": request.form["email"],
            "senha": request.form["senha"],
            "genero": request.form["genero"]
        }

        return redirect(url_for("cliente.pagina_endereco"))

    return render_template("cadastro.html")


@clientes_bp.route("/endereco", methods=["GET", "POST"])
def pagina_endereco():
    if "dados_cliente" not in session:
        flash("Preencha seus dados pessoais primeiro.")
        return redirect(url_for("cliente.cadastro"))

    if request.method == "POST":

        # Recupera os dados pessoais da session
        dados = session["dados_cliente"]

        # Cria o endereço
        endereco = Endereco(
            request.form["rua"],
            request.form["numero"],
            request.form["bairro"],
            request.form["cidade"],
            request.form["estado"],
            request.form["cep"]
        )

        # Define o ID do cliente
        id_cliente = len(clientes) + 1

        # Cria o cliente com os dados pessoais e o endereço
        cliente = Cliente(
            id_cliente,
            dados["nome"],
            dados["telefone"],
            dados["cpf"],
            dados["data_nascimento"],
            dados["email"],
            dados["senha"],
            dados["genero"],
            endereco
        )

        clientes.append(cliente)

        # Limpa os dados temporários do cadastro
        session.pop("dados_cliente", None)

        flash("Cadastro realizado com sucesso!")
        return redirect("/cardapio")

    return render_template("endereco.html")


@clientes_bp.route("/carrinho", methods=["GET"])
def carrinho():
    return render_template("carrinho.html")
