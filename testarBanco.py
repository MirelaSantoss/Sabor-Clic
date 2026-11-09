import sqlite3
import os

caminho_banco = os.path.join(os.path.dirname(__file__), 'sabor_clic.db')
print(f"Banco consultado: {caminho_banco}")

conexao = sqlite3.connect(caminho_banco)
cursor = conexao.cursor()

#criação da tabela Usuario caso ainda ñ exista
cursor.execute("""
CREATE TABLE IF NOT EXISTS Usuario (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    tipo_perfil TEXT NOT NULL CHECK(tipo_perfil IN ('CLIENTE', 'OPERADOR', 'GERENTE')),
    telefone TEXT,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
);
""")

#inserção de teste caso esteja vazia
cursor.execute("SELECT COUNT(*) FROM Usuario;")
if cursor.fetchone()[0] == 0:
    cursor.execute("""
    INSERT INTO Usuario (nome, email, senha_hash, tipo_perfil, telefone)
    VALUES ('Gustavo Vieira Stoppa', 'gustavo.stoppa@saboreclic.com.br', '$2b$12$hash', 'GERENTE', '(11) 98765-4321');
    """)
    conexao.commit()

#consulta com a nomenclatura correta
usuarios = cursor.execute("""
    SELECT id_usuario, nome, email, tipo_perfil
    FROM Usuario;
""").fetchall()

print("\nutilizadores encontrados:")
for u in usuarios:
    print(f"ID: {u[0]} / Nome: {u[1]} / Email: {u[2]} / Perfil: {u[3]}")

conexao.close()