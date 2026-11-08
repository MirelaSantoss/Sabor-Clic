import sqlite3
import os

# Caminho do banco de dados
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "sabor_clic.db")


def conectar():
    """Cria e retorna uma conexão com o banco de dados."""

    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")

    return conexao


def criar_tabelas():
    """Cria as tabelas necessárias para o funcionamento do sistema."""

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.executescript("""

        CREATE TABLE IF NOT EXISTS enderecos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rua TEXT NOT NULL,
            numero TEXT NOT NULL,
            bairro TEXT NOT NULL,
            cidade TEXT NOT NULL,
            estado TEXT NOT NULL,
            cep TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL,
            cpf TEXT NOT NULL UNIQUE,
            data_nascimento TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            genero TEXT,
            tipo TEXT NOT NULL DEFAULT 'cliente',
            endereco_id INTEGER,
            FOREIGN KEY (endereco_id) REFERENCES enderecos(id)
        );

        CREATE TABLE IF NOT EXISTS pratos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT NOT NULL,
            preco REAL NOT NULL,
            ativo INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Aguardando',
            data_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
            total REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        );

        CREATE TABLE IF NOT EXISTS pedido_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            prato_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
            FOREIGN KEY (prato_id) REFERENCES pratos(id)
        );

        CREATE TABLE IF NOT EXISTS cadastros_pendentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL,
            cpf TEXT NOT NULL,
            data_nascimento TEXT NOT NULL,
            email TEXT NOT NULL,
            senha_hash TEXT NOT NULL,
            genero TEXT,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        );

    """)

    conexao.commit()
    conexao.close()