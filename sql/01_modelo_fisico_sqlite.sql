PRAGMA foreign_keys = ON;

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
