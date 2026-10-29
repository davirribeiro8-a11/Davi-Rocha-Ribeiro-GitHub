
import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "estoque_sensores",
    "auth_plugin": "mysql_native_password"
}


def conectar():
    """
    Cria e retorna uma conexão com o banco de dados MySQL.
    """
    return mysql.connector.connect(**DB_CONFIG)
