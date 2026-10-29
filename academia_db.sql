CREATE SCHEMA IF NOT EXISTS `academia` DEFAULT CHARACTER SET utf8mb3 ;
SHOW WARNINGS;
USE `academia` ;

CREATE TABLE IF NOT EXISTS `usuarios` (
  `id` INT NOT NULL auto_increment,
  `nome` VARCHAR(50) NOT NULL,
  `email` VARCHAR(50) NOT NULL UNIQUE,
  `senha_hash` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;

SHOW WARNINGS;

CREATE TABLE IF NOT EXISTS `alunos` (
  `id` INT NOT NULL auto_increment,
  `nome` VARCHAR(50) NOT NULL,
  `cpf_criptografado` VARCHAR(100) NOT NULL,
  `email` VARCHAR(50) NOT NULL UNIQUE,
  `telefone` VARCHAR(11) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;

SHOW WARNINGS;
-- ------------------------------------------------- --


CREATE TABLE planos (
    id INT NOT NULL AUTO_INCREMENT,
    aluno_id INT NOT NULL,
    descricao VARCHAR(100),
    objetivo VARCHAR(100),
    PRIMARY KEY (id),
    CONSTRAINT fk_planos_alunos
        FOREIGN KEY (aluno_id)
        REFERENCES alunos(id)
) ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;

CREATE TABLE agendamentos (
    id INT NOT NULL AUTO_INCREMENT,
    plano_id INT NOT NULL,
    data DATE NOT NULL,
    horario TIME NOT NULL,
    observacao VARCHAR(200),
    reservar TINYINT,
    PRIMARY KEY (id),
    CONSTRAINT fk_agendamentos_planos
        FOREIGN KEY (plano_id)
        REFERENCES planos(id)
) ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;

-- ---------------------------------------- --
```CREATE TABLE IF NOT EXISTS `planos` (
  `id` INT NOT NULL auto_increment,
  `descricao` VARCHAR(100),
  `objetivo` VARCHAR(100),
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_planos_aluno1`
    FOREIGN KEY (`id`)
    REFERENCES `alunos` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;


CREATE TABLE IF NOT EXISTS `agendamentos` (
  `id` INT NOT NULL auto_increment,
  `data` DATE NOT NULL,
  `horario` TIME NOT NULL,
  `observacao` VARCHAR(200),
  `reservar` TINYINT,
   PRIMARY KEY (`id`),
   CONSTRAINT `agendamentos_ibfk_1`
    FOREIGN KEY (`id`)
    REFERENCES `planos` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;```


-- --------------------------------------------------------------------------- --

USE academia;

-- 1. INSERTS NA TABELA usuarios
INSERT INTO usuarios (nome, email, senha_hash) VALUES
('Ana Silva', 'ana@gmail.com', 'hash_ana123'),
('Bruno Santos', 'bruno@gmail.com', 'hash_bruno123'),
('Carla Oliveira', 'carla@gmail.com', 'hash_carla123'),
('Daniel Souza', 'daniel@gmail.com', 'hash_daniel123'),
('Eduarda Lima', 'eduarda@gmail.com', 'hash_eduarda123'),
('Felipe Costa', 'felipe@gmail.com', 'hash_felipe123'),
('Gabriela Alves', 'gabriela@gmail.com', 'hash_gabriela123');

select * from usuarios;

-- 2. INSERTS NA TABELA alunos
INSERT INTO alunos (nome, cpf_criptografado, email, telefone) VALUES
('Lucas Martins', 'cpf_cript_lucas001', 'lucas@gmail.com', '11987654321'),
('Mariana Rocha', 'cpf_cript_mariana002', 'mariana@gmail.com', '11987654322'),
('Pedro Ferreira', 'cpf_cript_pedro003', 'pedro@gmail.com', '11987654323'),
('Julia Mendes', 'cpf_cript_julia004', 'julia@gmail.com', '11987654324'),
('Rafael Gomes', 'cpf_cript_rafael005', 'rafael@gmail.com', '11987654325'),
('Beatriz Ribeiro', 'cpf_cript_beatriz006', 'beatriz@gmail.com', '11987654326'),
('Thiago Carvalho', 'cpf_cript_thiago007', 'thiago@gmail.com', '11987654327');

select * from alunos;

-- 3. INSERTS NA TABELA planos
-- A coluna id também é chave estrangeira para alunos.id.
```INSERT INTO planos (id, descricao, objetivo) VALUES
(1, 'Plano mensal', 'Condicionamento físico'),
(2, 'Plano trimestral', 'Ganho de força'),
(3, 'Plano semestral', 'Melhora da resistência'),
(4, 'Plano anual', 'Saúde e bem-estar'),
(5, 'Plano musculação', 'Desenvolvimento de força'),
(6, 'Plano funcional', 'Melhora da mobilidade'),
(7, 'Plano cardio', 'Melhora do condicionamento');```

USE academia;

-- 1. INSERTS NA TABELA planos
INSERT INTO planos (aluno_id, descricao, objetivo) VALUES
(1, 'Plano mensal', 'Condicionamento físico'),
(2, 'Plano trimestral', 'Ganho de força'),
(3, 'Plano semestral', 'Melhora da resistência'),
(4, 'Plano anual', 'Saúde e bem-estar'),
(5, 'Plano de musculação', 'Desenvolvimento muscular'),
(6, 'Plano funcional', 'Melhora da mobilidade'),
(7, 'Plano de cardio', 'Melhora do condicionamento');

select * from planos;

-- 2. INSERTS NA TABELA agendamentos
INSERT INTO agendamentos
(plano_id, `data`, horario, observacao, reservar) VALUES
(1, '2026-10-28', '08:00:00', 'Avaliação inicial', 1),
(2, '2026-10-28', '09:00:00', 'Treino de musculação', 1),
(3, '2026-10-29', '10:00:00', 'Treino funcional', 1),
(4, '2026-10-29', '14:00:00', 'Avaliação física', 0),
(5, '2026-10-30', '15:00:00', 'Treino de cardio', 1),
(6, '2026-10-30', '16:00:00', 'Treino de resistência', 0),
(7, '2026-10-31', '17:00:00', 'Acompanhamento de treino', 1);

select *  from agendamentos;
