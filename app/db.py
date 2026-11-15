import sqlite3
import os

# Caminho do banco de dados
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "sabor_clic.db")


def conectar():
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")

    return conexao

#atualização do banco de dados local de todo mundo assim q rodar o cód
def _migrar_tabela_clientes_se_necessario(conexao):
    cursor = conexao.cursor()
    colunas = cursor.execute("PRAGMA table_info(clientes)").fetchall()
    if not colunas:
        return

    cpf_obrigatorio = any(
        col["name"] == "cpf" and col["notnull"] == 1 for col in colunas
    )
    if not cpf_obrigatorio:
        return

    conexao.commit()
    conexao.execute("PRAGMA foreign_keys = OFF")

    cursor.executescript("""
        CREATE TABLE clientes_nova (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            cpf TEXT UNIQUE,
            data_nascimento TEXT,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            genero TEXT,
            tipo TEXT NOT NULL DEFAULT 'cliente'
                CHECK (tipo IN ('cliente', 'cozinheiro', 'administrador')),
            endereco_id INTEGER,
            FOREIGN KEY (endereco_id) REFERENCES enderecos(id)
        );

        INSERT INTO clientes_nova (
            id, nome, telefone, cpf, data_nascimento,
            email, senha, genero, tipo, endereco_id
        )
        SELECT
            id,
            nome,
            NULLIF(NULLIF(telefone, ''), 'não informado'),
            CASE
                WHEN cpf IS NULL OR cpf = '' OR cpf LIKE 'FUNC-%' OR cpf LIKE 'ADM-%'
                THEN NULL
                ELSE cpf
            END,
            NULLIF(NULLIF(data_nascimento, ''), 'não informado'),
            email,
            senha,
            genero,
            tipo,
            endereco_id
        FROM clientes;

        DROP TABLE clientes;
        ALTER TABLE clientes_nova RENAME TO clientes;
    """)

    conexao.commit()
    conexao.execute("PRAGMA foreign_keys = ON")


def criar_tabelas():

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
            telefone TEXT,
            cpf TEXT UNIQUE,
            data_nascimento TEXT,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            genero TEXT,
            tipo TEXT NOT NULL DEFAULT 'cliente'
                CHECK (tipo IN ('cliente', 'cozinheiro', 'administrador')),
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

    _migrar_tabela_clientes_se_necessario(conexao)

    colunas = {linha[1] for linha in cursor.execute("PRAGMA table_info(pratos)")}
    for nome, tipo in (("categoria", "TEXT NOT NULL DEFAULT 'Pratos'"), ("imagem", "TEXT")):
        if nome not in colunas:
            cursor.execute(f"ALTER TABLE pratos ADD COLUMN {nome} {tipo}")

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS historico_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL REFERENCES pedidos(id),
            status TEXT NOT NULL,
            alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TRIGGER IF NOT EXISTS registrar_status
        AFTER UPDATE OF status ON pedidos
        WHEN NEW.status <> OLD.status
        BEGIN
            INSERT INTO historico_status (pedido_id, status)
            VALUES (NEW.id, NEW.status);
        END;
    """)

    cursor.execute("SELECT COUNT(*) FROM pratos")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO pratos (nome, descricao, preco) VALUES (?, ?, ?)
        """, [
            ("Hambúrguer com frango", "Hambúrguer com queijo e bacon", 40.00),
            ("Marmitex simples", "Arroz e feijão com strogonoff de frango", 27.90),
            ("Super marmitex", "Arroz e feijão com lasanha, batata frita e salada", 40.00)
        ])

    conexao.commit()
    conexao.close()