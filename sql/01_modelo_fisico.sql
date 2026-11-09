CREATE DATABASE IF NOT EXISTS sabor_e_clic
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE sabor_e_clic;

CREATE TABLE IF NOT EXISTS Usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    tipo_perfil ENUM('CLIENTE', 'OPERADOR', 'GERENTE') NOT NULL,
    telefone VARCHAR(20) NULL,
    data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Categoria (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(80) NOT NULL UNIQUE,
    descricao VARCHAR(255) NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Prato (
    id_prato INT AUTO_INCREMENT PRIMARY KEY,
    id_categoria INT NOT NULL,
    nome VARCHAR(120) NOT NULL,
    descricao TEXT NULL,
    preco_venda DECIMAL(10, 2) NOT NULL,
    tempo_preparo_min INT NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_preco_prato CHECK (preco_venda > 0.00),
    CONSTRAINT chk_tempo_preparo CHECK (tempo_preparo_min >= 0),
    CONSTRAINT fk_prato_categoria FOREIGN KEY (id_categoria)
        REFERENCES Categoria(id_categoria)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Ingrediente (
    id_ingrediente INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    unidade_medida VARCHAR(10) NOT NULL,
    estoque_minimo DECIMAL(10, 3) NOT NULL DEFAULT 0.000,
    CONSTRAINT chk_unidade_medida CHECK (unidade_medida IN ('KG', 'G', 'L', 'ML', 'UN')),
    CONSTRAINT chk_estoque_minimo CHECK (estoque_minimo >= 0.000)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Composto_por (
    id_prato INT NOT NULL,
    id_ingrediente INT NOT NULL,
    qtd_necessaria DECIMAL(10, 3) NOT NULL,
    PRIMARY KEY (id_prato, id_ingrediente),
    CONSTRAINT chk_qtd_ficha CHECK (qtd_necessaria > 0.000),
    CONSTRAINT fk_comp_prato FOREIGN KEY (id_prato)
        REFERENCES Prato(id_prato)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_comp_ingrediente FOREIGN KEY (id_ingrediente)
        REFERENCES Ingrediente(id_ingrediente)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Lote_Estoque (
    id_lote INT AUTO_INCREMENT PRIMARY KEY,
    id_ingrediente INT NOT NULL,
    numero_lote VARCHAR(50) NOT NULL,
    qtd_atual DECIMAL(10, 3) NOT NULL,
    custo_unit DECIMAL(10, 4) NOT NULL,
    data_entrada DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_validade DATE NOT NULL,
    CONSTRAINT chk_qtd_lote CHECK (qtd_atual >= 0.000),
    CONSTRAINT chk_custo_lote CHECK (custo_unit >= 0.0000),
    CONSTRAINT fk_lote_ingrediente FOREIGN KEY (id_ingrediente)
        REFERENCES Ingrediente(id_ingrediente)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Movimento_Estoque (
    id_mov INT AUTO_INCREMENT PRIMARY KEY,
    id_ingrediente INT NOT NULL,
    id_usuario INT NOT NULL,
    tipo_mov ENUM('ENTRADA', 'BAIXA_PEDIDO', 'USO_EXTRAORDINARIO', 'PERDA') NOT NULL,
    qtd DECIMAL(10, 3) NOT NULL,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    motivo VARCHAR(255) NULL,
    CONSTRAINT chk_qtd_mov CHECK (qtd > 0.000),
    CONSTRAINT fk_mov_ingrediente FOREIGN KEY (id_ingrediente)
        REFERENCES Ingrediente(id_ingrediente)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_mov_usuario FOREIGN KEY (id_usuario)
        REFERENCES Usuario(id_usuario)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Pedido (
    id_pedido INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status_pedido ENUM('RECEBIDO', 'EM_PREPARO', 'PRONTO', 'ENTREGUE', 'CANCELADO') NOT NULL DEFAULT 'RECEBIDO',
    valor_total DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    observacoes VARCHAR(255) NULL,
    CONSTRAINT chk_valor_total CHECK (valor_total >= 0.00),
    CONSTRAINT fk_pedido_cliente FOREIGN KEY (id_cliente)
        REFERENCES Usuario(id_usuario)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Item_Pedido (
    id_item_pedido INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido INT NOT NULL,
    id_prato INT NOT NULL,
    preco_unit DECIMAL(10, 2) NOT NULL,
    qtd INT NOT NULL,
    CONSTRAINT chk_preco_item CHECK (preco_unit > 0.00),
    CONSTRAINT chk_qtd_item CHECK (qtd > 0),
    CONSTRAINT fk_item_pedido FOREIGN KEY (id_pedido)
        REFERENCES Pedido(id_pedido)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_item_prato FOREIGN KEY (id_prato)
        REFERENCES Prato(id_prato)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Bancada (
    id_bancada INT AUTO_INCREMENT PRIMARY KEY,
    cod_identificacao VARCHAR(20) NOT NULL UNIQUE,
    descricao VARCHAR(255) NULL,
    valor_hora DECIMAL(10, 2) NOT NULL,
    valor_caucao DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    status_operacional ENUM('DISPONIVEL', 'MANUTENCAO', 'INATIVA') NOT NULL DEFAULT 'DISPONIVEL',
    CONSTRAINT chk_valor_hora CHECK (valor_hora > 0.00),
    CONSTRAINT chk_valor_caucao CHECK (valor_caucao >= 0.00)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Reserva_Bancada (
    id_reserva INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_bancada INT NOT NULL,
    data_hora_inicio DATETIME NOT NULL,
    data_hora_fim DATETIME NOT NULL,
    valor_total_horas DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    valor_caucao_pago DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    valor_adicionais DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    status_reserva ENUM('SOLICITADA', 'CONFIRMADA', 'CONCLUIDA', 'CANCELADA') NOT NULL DEFAULT 'SOLICITADA',
    CONSTRAINT chk_datas_reserva CHECK (data_hora_fim > data_hora_inicio),
    CONSTRAINT chk_tot_horas CHECK (valor_total_horas >= 0.00),
    CONSTRAINT chk_caucao_pago CHECK (valor_caucao_pago >= 0.00),
    CONSTRAINT chk_adicionais CHECK (valor_adicionais >= 0.00),
    CONSTRAINT fk_reserva_cliente FOREIGN KEY (id_cliente)
        REFERENCES Usuario(id_usuario)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_reserva_bancada FOREIGN KEY (id_bancada)
        REFERENCES Bancada(id_bancada)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;