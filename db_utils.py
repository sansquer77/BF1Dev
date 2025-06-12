import sqlite3
DB_PATH = 'bolao_f1Dev.db'
def db_connect():
    return sqlite3.connect(DB_PATH, check_same_thread=False)
