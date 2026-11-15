#unificação do criar_admin, sendo feito tudo aqui agr
from app import create_app
from app.model.cliente import Cliente

create_app()

tipo = input("Tipo (cozinheiro/administrador): ").strip().lower()
nome = input("Nome: ").strip()
email = input("E-mail: ").strip().lower()
senha = input("Senha (mínimo 8 caracteres): ")

try:
    novo_id = Cliente.cadastrar_funcionario(nome, email, senha, tipo)
    print(f"Funcionário cadastrado com sucesso (ID {novo_id} - {tipo}).")
except ValueError as erro:
    raise SystemExit(f"Erro: {erro}")