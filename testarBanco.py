import sqlite3
import os

# Localiza a pasta onde este arquivo está salvo.
PASTA_PROJETO = os.path.dirname(os.path.abspath(__file__))

# Localiza o banco de dados correto.
CAMINHO_BANCO = os.path.join(PASTA_PROJETO, "sabor_clic.db")

print("Banco consultado:", CAMINHO_BANCO)

# Conecta ao banco correto.
conexao = sqlite3.connect(CAMINHO_BANCO)
conexao.row_factory = sqlite3.Row

# Verifica os clientes.
clientes = conexao.execute("""
    SELECT id, nome, email, cpf
    FROM clientes
""").fetchall()

print("\n===== CLIENTES CADASTRADOS =====")

for cliente in clientes:
    print(dict(cliente))

# Verifica os endereços.
enderecos = conexao.execute("""
    SELECT * FROM enderecos
""").fetchall()

print("\n===== ENDEREÇOS CADASTRADOS =====")

for endereco in enderecos:
    print(dict(endereco))

conexao.close()