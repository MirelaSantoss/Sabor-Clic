"""Execute uma vez para cadastrar a conta de administração."""
from getpass import getpass
from werkzeug.security import generate_password_hash
from app import create_app
from app.db import conectar

create_app()
nome = input("Nome do administrador: ").strip()
email = input("E-mail do administrador: ").strip().lower()
senha = getpass("Crie uma senha (mínimo 8 caracteres): ")
if not nome or "@" not in email or len(senha) < 8:
    raise SystemExit("Nome, e-mail ou senha inválidos.")

conexao = conectar()
try:
    existente = conexao.execute("SELECT id, tipo FROM clientes WHERE email = ?", (email,)).fetchone()
    if existente:
        raise SystemExit("Este e-mail já existe. Escolha outro e-mail para a conta de administração.")
    # Campos de cadastro exigidos pelo esquema atual; dados administrativos não são dados pessoais reais.
    import secrets
    identificador = "ADM-" + secrets.token_hex(12)
    conexao.execute("""INSERT INTO clientes
        (nome, telefone, cpf, data_nascimento, email, senha, genero, tipo)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'administrador')""",
        (nome, "não informado", identificador, "não informado", email,
         generate_password_hash(senha), None))
    conexao.commit()
    print("Administrador criado! Entre pelo botão 'Entrar como administrador'.")
finally:
    conexao.close()
