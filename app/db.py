import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.environ.get("DATABASE_PATH") or os.path.join(BASE_DIR, "sabor_clic.db")


def conectar():
    caminho = os.environ.get("DATABASE_PATH") or DB_PATH
    conexao = sqlite3.connect(caminho)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")

    return conexao


def _adicionar_colunas_faltantes(cursor, tabela, novas_colunas):
    colunas_existentes = {
        linha[1] for linha in cursor.execute(f"PRAGMA table_info({tabela})").fetchall()
    }
    for nome_coluna, definicao in novas_colunas:
        if nome_coluna not in colunas_existentes:
            cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {nome_coluna} {definicao}")


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
            preco REAL NOT NULL CHECK (preco > 0),
            ativo INTEGER NOT NULL DEFAULT 1,
            categoria TEXT NOT NULL DEFAULT 'Pratos',
            imagem TEXT,
            tempo_preparo_min INTEGER NOT NULL DEFAULT 20
        );

        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Aguardando',
            data_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
            total REAL NOT NULL DEFAULT 0 CHECK (total >= 0),
            tempo_estimado INTEGER,
            observacoes TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        );

        CREATE TABLE IF NOT EXISTS pedido_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            prato_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL CHECK (quantidade > 0),
            preco_unitario REAL NOT NULL CHECK (preco_unitario > 0),
            observacoes TEXT,
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

        CREATE TABLE IF NOT EXISTS estoque_pratos (
            prato_id INTEGER PRIMARY KEY REFERENCES pratos(id),
            quantidade INTEGER NOT NULL CHECK (quantidade >= 0)
        );

        CREATE TABLE IF NOT EXISTS historico_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL REFERENCES pedidos(id),
            status TEXT NOT NULL,
            alterado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS bancadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cod_identificacao TEXT NOT NULL UNIQUE,
            descricao TEXT,
            valor_hora REAL NOT NULL CHECK (valor_hora > 0),
            valor_caucao REAL NOT NULL DEFAULT 0 CHECK (valor_caucao >= 0),
            status_operacional TEXT NOT NULL DEFAULT 'DISPONIVEL'
                CHECK (status_operacional IN ('DISPONIVEL', 'MANUTENCAO', 'INATIVA'))
        );

        CREATE TABLE IF NOT EXISTS reservas_bancadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            bancada_id INTEGER NOT NULL,
            data_hora_inicio DATETIME NOT NULL,
            data_hora_fim DATETIME NOT NULL,
            valor_total_horas REAL NOT NULL DEFAULT 0 CHECK (valor_total_horas >= 0),
            valor_caucao_pago REAL NOT NULL DEFAULT 0 CHECK (valor_caucao_pago >= 0),
            valor_adicionais REAL NOT NULL DEFAULT 0 CHECK (valor_adicionais >= 0),
            status_reserva TEXT NOT NULL DEFAULT 'CONFIRMADA'
                CHECK (status_reserva IN ('SOLICITADA', 'CONFIRMADA', 'CONCLUIDA', 'CANCELADA')),
            CHECK (data_hora_fim > data_hora_inicio),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (bancada_id) REFERENCES bancadas(id)
        );
    """)

    _migrar_tabela_clientes_se_necessario(conexao)

    _adicionar_colunas_faltantes(cursor, "pratos", [
        ("categoria", "TEXT NOT NULL DEFAULT 'Pratos'"),
        ("imagem", "TEXT"),
        ("tempo_preparo_min", "INTEGER NOT NULL DEFAULT 20"),
    ])
    _adicionar_colunas_faltantes(cursor, "pedidos", [
        ("tempo_estimado", "INTEGER"),
        ("observacoes", "TEXT"),
    ])
    _adicionar_colunas_faltantes(cursor, "pedido_itens", [
        ("observacoes", "TEXT"),
    ])

    cursor.executescript("""
        CREATE TRIGGER IF NOT EXISTS criar_estoque_padrao_prato
        AFTER INSERT ON pratos
        BEGIN
            INSERT OR IGNORE INTO estoque_pratos (prato_id, quantidade)
            VALUES (NEW.id, 50);
        END;

        CREATE TRIGGER IF NOT EXISTS registrar_status
        AFTER UPDATE OF status ON pedidos
        WHEN NEW.status <> OLD.status
        BEGIN
            INSERT INTO historico_status (pedido_id, status)
            VALUES (NEW.id, NEW.status);
        END;

        CREATE TRIGGER IF NOT EXISTS conferir_estoque_antes_pedido
        BEFORE INSERT ON pedido_itens
        WHEN EXISTS (SELECT 1 FROM estoque_pratos WHERE prato_id = NEW.prato_id)
        BEGIN
            SELECT CASE
                WHEN (SELECT quantidade FROM estoque_pratos WHERE prato_id = NEW.prato_id) < NEW.quantidade
                THEN RAISE(ABORT, 'Estoque insuficiente')
            END;
        END;

        CREATE TRIGGER IF NOT EXISTS baixar_estoque_pedido
        AFTER INSERT ON pedido_itens
        WHEN EXISTS (SELECT 1 FROM estoque_pratos WHERE prato_id = NEW.prato_id)
        BEGIN
            UPDATE estoque_pratos
            SET quantidade = quantidade - NEW.quantidade
            WHERE prato_id = NEW.prato_id;
        END;

        CREATE TRIGGER IF NOT EXISTS atualizar_total_pedido
        AFTER INSERT ON pedido_itens
        BEGIN
            UPDATE pedidos
            SET total = ROUND((
                SELECT COALESCE(SUM(preco_unitario * quantidade), 0)
                FROM pedido_itens
                WHERE pedido_id = NEW.pedido_id
            ), 2)
            WHERE id = NEW.pedido_id;
        END;
    """)

    cursor.execute("SELECT COUNT(*) FROM pratos")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO pratos (nome, descricao, preco, categoria, tempo_preparo_min)
            VALUES (?, ?, ?, ?, ?)
        """, [
            ("Hambúrguer com frango", "Hambúrguer artesanal de frango com queijo e bacon crocante", 40.00, "Pratos", 25),
            ("Marmitex simples", "Arroz soltinho, feijão caseiro e strogonoff de frango", 27.90, "Pratos", 20),
            ("Super marmitex", "Arroz, feijão, lasanha à bolonhesa, batata frita e salada fresca", 40.00, "Combos", 30),
        ])

    cursor.execute("""
        INSERT OR IGNORE INTO estoque_pratos (prato_id, quantidade)
        SELECT id, 50 FROM pratos
    """)

    cursor.execute("SELECT COUNT(*) FROM bancadas")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO bancadas (cod_identificacao, descricao, valor_hora, valor_caucao, status_operacional)
            VALUES (?, ?, ?, ?, ?)
        """, [
            ("BANCADA-01", "Estação quente com fogão industrial de 6 bocas, chapa e coifa de exaustão", 45.00, 300.00, "DISPONIVEL"),
            ("BANCADA-02", "Estação de panificação e massas com masseira, forno combinado e bancada de inox", 60.00, 500.00, "DISPONIVEL"),
            ("BANCADA-03", "Estação fria para montagem de saladas e sushis com pista refrigerada", 40.00, 200.00, "DISPONIVEL"),
        ])

    conexao.commit()
    conexao.close()
