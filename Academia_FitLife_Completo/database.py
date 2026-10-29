import os
import mysql.connector

DB_CONFIG = {
    "host": os.getenv("FITLIFE_DB_HOST", "localhost"),
    "user": os.getenv("FITLIFE_DB_USER", "root"),
    "password": os.getenv("FITLIFE_DB_PASSWORD", "123456"),
    "database": os.getenv("FITLIFE_DB_NAME", "academia_fitlife"),
    "autocommit": False,
}

def connect():
    """Abre uma conexão nova com o banco; feche-a após o uso."""
    return mysql.connector.connect(**DB_CONFIG)
