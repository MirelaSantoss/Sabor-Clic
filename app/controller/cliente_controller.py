from flask import Blueprint, request, render_template
from ..model.cliente import Cliente
from ..model.endereco import Endereco 

clientes_bp = Blueprint("cliente", __name__)

clientes = []

@clientes_bp.route("/formulario", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":

        # Informações do cliente
        nome = request.form["nome"]
        telefone = request.form["telefone"]
        cpf = request.form["cpf"]
        data_nascimento = request.form["data_nascimento"]
        email = request.form["email"]
        senha = request.form["senha"]
        genero = request.form["genero"]

        # Informações de endereço do cliente
        rua = request.form["rua"]
        numero = request.form["numero"]
        bairro = request.form["bairro"]
        cidade = request.form["cidade"]
        estado = request.form["estado"]
        cep = request.form["cep"]

        endereco = Endereco(rua, numero, bairro, cidade, estado, cep)

        # Aqui define p id do cliente
        id = len(clientes) + 1

        cliente = Cliente(nome, telefone, cpf, data_nascimento, email, senha, genero, endereco)
        clientes.append(cliente)

        return "Cliente cadastrado com sucesso!"

    return render_template("cadastro.html")