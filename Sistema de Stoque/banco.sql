-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

SHOW WARNINGS;

CREATE SCHEMA IF NOT EXISTS smartmeds
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_0900_ai_ci;

SHOW WARNINGS;
USE smartmeds;

CREATE TABLE IF NOT EXISTS cliente (
id INT NOT NULL AUTO_INCREMENT,
nome VARCHAR(100) NOT NULL,
email VARCHAR(100) NOT NULL,
senha VARCHAR(255) NOT NULL,
cnpj VARCHAR(14) NOT NULL,
PRIMARY KEY (id),
UNIQUE INDEX email (email ASC) VISIBLE,
UNIQUE INDEX cnpj (cnpj ASC) VISIBLE
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

CREATE TABLE IF NOT EXISTS localizacao (
id INT NOT NULL AUTO_INCREMENT,
rua VARCHAR(100) NOT NULL,
numero VARCHAR(10) NOT NULL,
andar VARCHAR(20) NULL DEFAULT NULL,
PRIMARY KEY (id)
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

CREATE TABLE IF NOT EXISTS produto (
id INT NOT NULL AUTO_INCREMENT,
nome VARCHAR(100) NOT NULL,
marca VARCHAR(100) NULL DEFAULT NULL,
data_de_validade DATE NULL DEFAULT NULL,
especificacao TEXT NULL DEFAULT NULL,
unidade_medida VARCHAR(50) NULL DEFAULT NULL,
localizacao_id INT NULL DEFAULT NULL,
PRIMARY KEY (id),
INDEX fk_produto_localizacao (localizacao_id ASC) VISIBLE,
CONSTRAINT fk_produto_localizacao
FOREIGN KEY (localizacao_id)
REFERENCES localizacao (id)
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

CREATE TABLE IF NOT EXISTS movimentacao (
id INT NOT NULL AUTO_INCREMENT,
tipo_movimentacao VARCHAR(50) NULL DEFAULT NULL,
data_movimentacao DATETIME NULL DEFAULT NULL,
quantidade INT NOT NULL,
quantidade_min INT NULL DEFAULT NULL,
produto_id INT NULL DEFAULT NULL,
PRIMARY KEY (id),
INDEX fk_movimentacao_produto (produto_id ASC) VISIBLE,
CONSTRAINT fk_movimentacao_produto
FOREIGN KEY (produto_id)
REFERENCES produto (id)
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

CREATE TABLE IF NOT EXISTS usuario (
id INT NOT NULL AUTO_INCREMENT,
nome VARCHAR(100) NOT NULL,
email VARCHAR(100) NOT NULL,
senha VARCHAR(255) NOT NULL,
tipo VARCHAR(20) NOT NULL,
identificacao VARCHAR(20) NOT NULL,
PRIMARY KEY (id),
UNIQUE INDEX email (email ASC) VISIBLE
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

CREATE TABLE IF NOT EXISTS pedido_entrada (
id_pedido_entrada INT NOT NULL AUTO_INCREMENT,
numero_documento VARCHAR(50) NULL DEFAULT NULL,
fornecedor VARCHAR(100) NULL DEFAULT NULL,
data_entrada DATE NOT NULL,
id_usuario INT NOT NULL,
observacao TEXT NULL DEFAULT NULL,
status VARCHAR(30) NULL DEFAULT 'aberto',
criado_em DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (id_pedido_entrada),
INDEX fk_pedido_entrada_usuario (id_usuario ASC) VISIBLE,
CONSTRAINT fk_pedido_entrada_usuario
FOREIGN KEY (id_usuario)
REFERENCES usuario (id)
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

CREATE TABLE IF NOT EXISTS item_entrada (
id INT NOT NULL AUTO_INCREMENT,
quantidade INT NOT NULL,
valor DECIMAL(10,2) NULL DEFAULT NULL,
pedido_entrada_id INT NULL DEFAULT NULL,
movimentacao_id INT NULL DEFAULT NULL,
PRIMARY KEY (id),
INDEX fk_item_entrada_pedido (pedido_entrada_id ASC) VISIBLE,
INDEX fk_item_entrada_movimentacao (movimentacao_id ASC) VISIBLE,
CONSTRAINT fk_item_entrada_movimentacao
FOREIGN KEY (movimentacao_id)
REFERENCES movimentacao (id),
CONSTRAINT fk_item_entrada_pedido
FOREIGN KEY (pedido_entrada_id)
REFERENCES pedido_entrada (id_pedido_entrada)
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

CREATE TABLE IF NOT EXISTS pedido_saida (
id INT NOT NULL AUTO_INCREMENT,
tipo VARCHAR(50) NULL DEFAULT NULL,
pagamento VARCHAR(50) NULL DEFAULT NULL,
quantidade INT NOT NULL,
valor DECIMAL(10,2) NULL DEFAULT NULL,
data_pagamento DATE NULL DEFAULT NULL,
cliente_id INT NULL DEFAULT NULL,
usuario_id INT NOT NULL,
PRIMARY KEY (id),
INDEX fk_pedido_saida_cliente (cliente_id ASC) VISIBLE,
INDEX fk_pedido_saida_usuario (usuario_id ASC) VISIBLE,
CONSTRAINT fk_pedido_saida_cliente
FOREIGN KEY (cliente_id)
REFERENCES cliente (id),
CONSTRAINT fk_pedido_saida_usuario
FOREIGN KEY (usuario_id)
REFERENCES usuario (id)
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

CREATE TABLE IF NOT EXISTS item_saida (
id INT NOT NULL AUTO_INCREMENT,
quantidade INT NOT NULL,
valor DECIMAL(10,2) NULL DEFAULT NULL,
pedido_saida_id INT NULL DEFAULT NULL,
movimentacao_id INT NULL DEFAULT NULL,
PRIMARY KEY (id),
INDEX fk_item_saida_pedido (pedido_saida_id ASC) VISIBLE,
INDEX fk_item_saida_movimentacao (movimentacao_id ASC) VISIBLE,
CONSTRAINT fk_item_saida_movimentacao
FOREIGN KEY (movimentacao_id)
REFERENCES movimentacao (id),
CONSTRAINT fk_item_saida_pedido
FOREIGN KEY (pedido_saida_id)
REFERENCES pedido_saida (id)
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;





-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: smartmeds
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cliente`
--

DROP TABLE IF EXISTS `cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cliente` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `senha` varchar(255) NOT NULL,
  `cnpj` varchar(14) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `cnpj` (`cnpj`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cliente`
--

LOCK TABLES `cliente` WRITE;
/*!40000 ALTER TABLE `cliente` DISABLE KEYS */;
INSERT INTO `cliente` VALUES (4,'Samuel Rodrigues Ferreira','samuel.ferreira3s@gmail.com','123456','85236974125896'),(6,'Mattheus de Jesus Toledo','matheus.jesus.mt@gmail.com','matheus.29','32541569874520'),(8,'Maria Luísa Joaquim Ortolan','malu.ortolan@gmail.com','Malu@2009','85236956325412');
/*!40000 ALTER TABLE `cliente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `item_entrada`
--

DROP TABLE IF EXISTS `item_entrada`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `item_entrada` (
  `id` int NOT NULL AUTO_INCREMENT,
  `quantidade` int NOT NULL,
  `valor` decimal(10,2) DEFAULT NULL,
  `pedido_entrada_id` int DEFAULT NULL,
  `movimentacao_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_item_entrada_pedido` (`pedido_entrada_id`),
  KEY `fk_item_entrada_movimentacao` (`movimentacao_id`),
  CONSTRAINT `fk_item_entrada_movimentacao` FOREIGN KEY (`movimentacao_id`) REFERENCES `movimentacao` (`id`),
  CONSTRAINT `fk_item_entrada_pedido` FOREIGN KEY (`pedido_entrada_id`) REFERENCES `pedido_entrada` (`id_pedido_entrada`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `item_entrada`
--

LOCK TABLES `item_entrada` WRITE;
/*!40000 ALTER TABLE `item_entrada` DISABLE KEYS */;
INSERT INTO `item_entrada` VALUES (1,10,0.10,1,1),(2,14,0.21,3,2),(3,10,200.00,5,3),(4,20,40.00,6,2),(5,16,74.00,8,4),(6,5,25.00,9,2),(7,100,8888888.00,10,6),(8,1,10.00,12,3);
/*!40000 ALTER TABLE `item_entrada` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `item_saida`
--

DROP TABLE IF EXISTS `item_saida`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `item_saida` (
  `id` int NOT NULL AUTO_INCREMENT,
  `quantidade` int NOT NULL,
  `valor` decimal(10,2) DEFAULT NULL,
  `pedido_saida_id` int DEFAULT NULL,
  `movimentacao_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_item_saida_pedido` (`pedido_saida_id`),
  KEY `fk_item_saida_movimentacao` (`movimentacao_id`),
  CONSTRAINT `fk_item_saida_movimentacao` FOREIGN KEY (`movimentacao_id`) REFERENCES `movimentacao` (`id`),
  CONSTRAINT `fk_item_saida_pedido` FOREIGN KEY (`pedido_saida_id`) REFERENCES `pedido_saida` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `item_saida`
--

LOCK TABLES `item_saida` WRITE;
/*!40000 ALTER TABLE `item_saida` DISABLE KEYS */;
/*!40000 ALTER TABLE `item_saida` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `localizacao`
--

DROP TABLE IF EXISTS `localizacao`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `localizacao` (
  `id` int NOT NULL AUTO_INCREMENT,
  `rua` varchar(100) NOT NULL,
  `numero` varchar(10) NOT NULL,
  `andar` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `localizacao`
--

LOCK TABLES `localizacao` WRITE;
/*!40000 ALTER TABLE `localizacao` DISABLE KEYS */;
INSERT INTO `localizacao` VALUES (1,'Corredor A','01','Térreo'),(2,'Corredor B','15','1º Andar'),(3,'Prateleira C','08','2º Andar'),(4,'Senaizinho','10','2'),(5,'humberto','5','4° Andar'),(6,'humberto','5','4° Andar'),(7,'humberto','5','4° Andar'),(8,'Senaizinho','4678','9'),(9,'tilambo cano','67','67'),(10,'tilambo cano','67','67'),(11,'Corredor A','01','Térreo'),(12,'Corredor B','15','1º Andar'),(13,'Prateleira C','08','2º Andar');
/*!40000 ALTER TABLE `localizacao` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movimentacao`
--

DROP TABLE IF EXISTS `movimentacao`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movimentacao` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tipo_movimentacao` varchar(50) DEFAULT NULL,
  `data_movimentacao` datetime DEFAULT NULL,
  `quantidade` int NOT NULL,
  `quantidade_min` int DEFAULT NULL,
  `produto_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_movimentacao_produto` (`produto_id`),
  CONSTRAINT `fk_movimentacao_produto` FOREIGN KEY (`produto_id`) REFERENCES `produto` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimentacao`
--

LOCK TABLES `movimentacao` WRITE;
/*!40000 ALTER TABLE `movimentacao` DISABLE KEYS */;
INSERT INTO `movimentacao` VALUES (1,'CADASTRO','2026-06-18 14:44:09',1,NULL,4),(2,'CADASTRO','2026-06-18 15:06:10',1,NULL,5),(3,'CADASTRO','2026-06-18 15:07:44',1,NULL,6),(4,'CADASTRO','2026-07-30 15:14:44',1,NULL,7),(6,'CADASTRO','2026-08-27 13:55:44',1,NULL,12);
/*!40000 ALTER TABLE `movimentacao` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedido_entrada`
--

DROP TABLE IF EXISTS `pedido_entrada`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedido_entrada` (
  `id_pedido_entrada` int NOT NULL AUTO_INCREMENT,
  `numero_documento` varchar(50) DEFAULT NULL,
  `fornecedor` varchar(100) DEFAULT NULL,
  `data_entrada` date NOT NULL,
  `id_usuario` int NOT NULL,
  `observacao` text,
  `status` varchar(30) DEFAULT 'aberto',
  `criado_em` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_pedido_entrada`),
  KEY `fk_pedido_entrada_usuario` (`id_usuario`),
  CONSTRAINT `fk_pedido_entrada_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedido_entrada`
--

LOCK TABLES `pedido_entrada` WRITE;
/*!40000 ALTER TABLE `pedido_entrada` DISABLE KEYS */;
INSERT INTO `pedido_entrada` VALUES (1,'6767','tu','2026-06-26',1,'sla','ABERTO','2026-06-18 14:59:55'),(2,'6767','Malu','2026-06-26',9,'slaaa','ABERTO','2026-06-18 15:08:58'),(3,'5365','Malu','2026-06-26',9,'kkkkkk','PENDENTE','2026-06-18 15:24:30'),(4,'5365','Malu','2026-06-26',9,'oi','ABERTO','2026-06-18 15:30:04'),(5,'5365','Malu','2026-06-26',9,'ewr8u9fsdhjf','PENDENTE','2026-06-18 15:58:05'),(6,'5365','Malu','2026-06-26',9,'´kkkkkkkk','ABERTO','2026-07-28 11:08:34'),(7,'5365','Malu','2026-06-26',9,'AAAAAAAAAAAASDDDDDDFSSSSSS','PENDENTE','2026-07-30 15:16:42'),(8,'5365','Malu','2026-06-26',9,'SLA SLA SLAAAAA','ABERTO','2026-08-11 09:22:55'),(9,'090409','Maria Luisa','2026-09-09',9,'4545454545','ABERTO','2026-08-11 09:24:45'),(10,'090409','Maria Luisa','2026-09-09',15,'xdfsgrdv','ABERTO','2026-08-27 13:59:03'),(11,'020','malu','2026-09-03',15,'oioioii','ABERTO','2026-09-03 16:40:05'),(12,'003','malu','2026-09-15',15,'milena','ABERTO','2026-09-15 09:51:40'),(13,'566','malu','2026-09-15',15,'ifejdic','ABERTO','2026-09-15 10:08:10');
/*!40000 ALTER TABLE `pedido_entrada` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedido_saida`
--

DROP TABLE IF EXISTS `pedido_saida`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedido_saida` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tipo` varchar(50) DEFAULT NULL,
  `pagamento` varchar(50) DEFAULT NULL,
  `quantidade` int NOT NULL,
  `valor` decimal(10,2) DEFAULT NULL,
  `data_pagamento` date DEFAULT NULL,
  `cliente_id` int DEFAULT NULL,
  `usuario_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_pedido_saida_cliente` (`cliente_id`),
  KEY `fk_pedido_saida_usuario` (`usuario_id`),
  CONSTRAINT `fk_pedido_saida_cliente` FOREIGN KEY (`cliente_id`) REFERENCES `cliente` (`id`),
  CONSTRAINT `fk_pedido_saida_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedido_saida`
--

LOCK TABLES `pedido_saida` WRITE;
/*!40000 ALTER TABLE `pedido_saida` DISABLE KEYS */;
INSERT INTO `pedido_saida` VALUES (1,'VENDA','PIX',5,50.00,'2028-12-04',6,9),(2,'VENDA','PIX',8,2000.00,'2029-02-18',4,9),(3,'DESCARTE','PIX',10,20.00,'2026-07-28',8,9);
/*!40000 ALTER TABLE `pedido_saida` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `produto`
--

DROP TABLE IF EXISTS `produto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `produto` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `marca` varchar(100) DEFAULT NULL,
  `data_de_validade` date DEFAULT NULL,
  `especificacao` text,
  `unidade_medida` varchar(50) DEFAULT NULL,
  `localizacao_id` int DEFAULT NULL,
  `quantidade` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `fk_produto_localizacao` (`localizacao_id`),
  CONSTRAINT `fk_produto_localizacao` FOREIGN KEY (`localizacao_id`) REFERENCES `localizacao` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `produto`
--

LOCK TABLES `produto` WRITE;
/*!40000 ALTER TABLE `produto` DISABLE KEYS */;
INSERT INTO `produto` VALUES (4,'Cinegripe','Cinegripe','2026-07-11','ambiente ambos','30 capsula',8,0),(5,'dorflex','Novalgina','2026-07-09','ambiente ambos','ml',9,39),(6,'Cinegripe','Cinegripe','2027-07-18','ambiente ambos','30 capsula',4,10),(7,'carmed','caemed','2008-10-30','ambiente ambos','10000',NULL,16),(12,'dorflex','DIMIMI','2027-12-31','ambiente ambos','30 capsula',NULL,0);
/*!40000 ALTER TABLE `produto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `senha` varchar(255) NOT NULL,
  `tipo` varchar(20) NOT NULL,
  `identificacao` varchar(20) NOT NULL,
  `permissao` tinyint NOT NULL DEFAULT '0',
  `foto_nome` varchar(255) DEFAULT NULL,
  `foto_caminho` varchar(500) DEFAULT NULL,
  `foto_blob` blob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES (1,'mecanico admin','davi.r.ribeiro8@aluno.senai.br','$2b$12$46gleLFxYOjpUfVQ27iF0.8ODEvqW4hiU2P2zKf12jlE8pYkdQpWq','adm','0001',0,NULL,NULL,NULL),(9,'gerenciador admin','smartmedsproject@gmail.com','$2b$12$OAqwZ40KgaNVfUFR/5FzuOa5gRlITu6x0hIUjx9CePh2GzsESi94e','adm','0001',0,NULL,NULL,NULL),(14,'Davi Rocha Ribeiro','davi.rocha@gmail.com','$2b$12$MSTUkTNd2Cw191HW4t1uDe0L00/WdjEnLyqMojRoHsdLiPM.xptJm','adm','004',0,NULL,NULL,NULL),(15,'Maria Luisa Joaquim Ortolan','maria.ortolan@gmail.com','$2b$12$tiRXB3QHWihoKxnb9FXNT.ULo9805HEkEur.Hdd3FZPqMUkTVq2QK','adm','006',0,NULL,NULL,NULL),(16,'Matheus Jesus Toledo','matheus.toledo@gmail.com','$2b$12$4XV.PSTpy2J5RPXEzKHqQeSm.B5/fAqzZ12ieDK4bE9YD6YQeTDae','consulta','007',0,NULL,NULL,NULL),(18,'Antonio Donisete Antunes Garcia Junior','junior@gmail.com','$2b$12$5zI.bIz.vC3J.PoiudD3mORXUpFHauaWe3lD8biMTgtDEfIS7sHQm','consulta','159',0,NULL,NULL,NULL),(26,'Guilherme Jesuino Marques','guilherme@gmail.com','$2b$12$V.KGi90c03fjIE8yieQX/e.hI0OU.x9KtQLOW3jE8C4wXx7aQoac6','adm','001',0,NULL,NULL,NULL);
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-15 14:04:12
