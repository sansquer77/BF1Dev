import sqlite3
DB_PATH = "seu_banco.db"
def db_connect():
    return sqlite3.connect(DB_PATH, check_same_thread=False)
