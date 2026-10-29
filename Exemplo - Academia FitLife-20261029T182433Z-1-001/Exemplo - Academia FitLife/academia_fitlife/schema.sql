CREATE DATABASE IF NOT EXISTS academia_fitlife CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE academia_fitlife;

CREATE TABLE IF NOT EXISTS usuarios (
 id_usuario INT AUTO_INCREMENT PRIMARY KEY,
 nome VARCHAR(100) NOT NULL,
 usuario VARCHAR(50) NOT NULL UNIQUE,
 senha VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS alunos (
 id_aluno INT AUTO_INCREMENT PRIMARY KEY,
 nome VARCHAR(100) NOT NULL,
 idade INT NOT NULL,
 telefone VARCHAR(20),
 cidade VARCHAR(80)
);
CREATE TABLE IF NOT EXISTS professores (
 id_professor INT AUTO_INCREMENT PRIMARY KEY,
 nome VARCHAR(100) NOT NULL,
 telefone VARCHAR(20),
 especialidade VARCHAR(80) NOT NULL
);
CREATE TABLE IF NOT EXISTS atividades (
 id_atividade INT AUTO_INCREMENT PRIMARY KEY,
 id_aluno INT NOT NULL,
 id_professor INT NOT NULL,
 modalidade ENUM('Musculação','Natação','Dança','Luta') NOT NULL,
 valor_mensal DECIMAL(10,2) NOT NULL DEFAULT 0,
 data_inicio DATE NOT NULL,
 FOREIGN KEY (id_aluno) REFERENCES alunos(id_aluno) ON DELETE RESTRICT,
 FOREIGN KEY (id_professor) REFERENCES professores(id_professor) ON DELETE RESTRICT
);




