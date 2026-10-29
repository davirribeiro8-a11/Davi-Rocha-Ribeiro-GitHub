import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123456",  
    "database": "academia_fitlife",
}

def connect():
    return mysql.connector.connect(**DB_CONFIG)
