"""Crie contas de funcionários sem expor senhas no site."""
from getpass import getpass
from secrets import token_hex
from werkzeug.security import generate_password_hash
from app import create_app
from app.db import conectar

create_app()
tipo = input("Tipo (cozinheiro/administrador): ").strip().lower()
if tipo not in ("cozinheiro", "administrador"):
    raise SystemExit("Tipo inválido")
nome = input("Nome: ").strip()
email = input("E-mail: ").strip().lower()
senha = getpass("Senha (mínimo 8 caracteres): ")
if not nome or "@" not in email or len(senha) < 8:
    raise SystemExit("Confira nome, e-mail e senha")
con = conectar()
try:
    con.execute("""INSERT INTO clientes (nome, telefone, cpf, data_nascimento, email, senha, tipo)
                   VALUES (?, '', ?, '', ?, ?, ?)""",
                (nome, 'FUNC-' + token_hex(12), email, generate_password_hash(senha), tipo))
    con.commit()
    print("Funcionário cadastrado:", tipo)
except Exception as erro:
    print("Não foi possível cadastrar:", erro)
finally:
    con.close()
