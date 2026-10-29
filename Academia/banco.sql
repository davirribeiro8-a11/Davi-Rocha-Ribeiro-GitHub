CREATE DATABASE IF NOT EXISTS estoque_sensores;
USE estoque_sensores;

CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    perfil VARCHAR(30) NOT NULL,
    status VARCHAR(20) DEFAULT 'ativo',
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE produto (
    id_produto INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    unidade_medida VARCHAR(20) NOT NULL,
    estoque_minimo DECIMAL(10,2) DEFAULT 0,
    estoque_maximo DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'ativo',
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
    imagem_nome VARCHAR(255) NULL,
    imagem_tipo VARCHAR(100) NULL,
    imagem_blob LONGBLOB NULL;
);

CREATE TABLE localizacao (
    id_localizacao INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    setor VARCHAR(100),
    corredor VARCHAR(50),
    prateleira VARCHAR(50),
    observacao TEXT
);

CREATE TABLE estoque (
    id_estoque INT AUTO_INCREMENT PRIMARY KEY,
    id_produto INT NOT NULL,
    id_localizacao INT NOT NULL,
    quantidade_atual DECIMAL(10,2) DEFAULT 0,
    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (id_produto) REFERENCES produto(id_produto),
    FOREIGN KEY (id_localizacao) REFERENCES localizacao(id_localizacao),

    UNIQUE (id_produto, id_localizacao)
);

CREATE TABLE pedido_entrada (
    id_pedido_entrada INT AUTO_INCREMENT PRIMARY KEY,
    numero_documento VARCHAR(50),
    fornecedor VARCHAR(100),
    data_entrada DATE NOT NULL,
    id_usuario INT NOT NULL,
    observacao TEXT,
    status VARCHAR(30) DEFAULT 'aberto',
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE item_pedido_entrada (
    id_item_entrada INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido_entrada INT NOT NULL,
    id_produto INT NOT NULL,
    id_localizacao INT NOT NULL,
    quantidade DECIMAL(10,2) NOT NULL,
    valor_unitario DECIMAL(10,2) DEFAULT 0,
    valor_total DECIMAL(10,2) DEFAULT 0,

    FOREIGN KEY (id_pedido_entrada) REFERENCES pedido_entrada(id_pedido_entrada),
    FOREIGN KEY (id_produto) REFERENCES produto(id_produto),
    FOREIGN KEY (id_localizacao) REFERENCES localizacao(id_localizacao)
);

CREATE TABLE pedido_saida (
    id_pedido_saida INT AUTO_INCREMENT PRIMARY KEY,
    numero_documento VARCHAR(50),
    solicitante VARCHAR(100),
    data_saida DATE NOT NULL,
    id_usuario INT NOT NULL,
    observacao TEXT,
    status VARCHAR(30) DEFAULT 'aberto',
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE item_pedido_saida (
    id_item_saida INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido_saida INT NOT NULL,
    id_produto INT NOT NULL,
    id_localizacao INT NOT NULL,
    quantidade DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (id_pedido_saida) REFERENCES pedido_saida(id_pedido_saida),
    FOREIGN KEY (id_produto) REFERENCES produto(id_produto),
    FOREIGN KEY (id_localizacao) REFERENCES localizacao(id_localizacao)
);

CREATE TABLE cadastro_sensor (
    id_sensor INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    tipo_sensor VARCHAR(50) NOT NULL,
    codigo_sensor VARCHAR(50) NOT NULL UNIQUE,
    id_localizacao INT NOT NULL,
    id_produto INT NULL,
    status VARCHAR(20) DEFAULT 'ativo',
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_localizacao) REFERENCES localizacao(id_localizacao),
    FOREIGN KEY (id_produto) REFERENCES produto(id_produto)
);

CREATE TABLE dados_sensor (
    id_dado_sensor INT AUTO_INCREMENT PRIMARY KEY,
    id_sensor INT NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    unidade VARCHAR(20),
    data_leitura DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_sensor) REFERENCES cadastro_sensor(id_sensor)
);