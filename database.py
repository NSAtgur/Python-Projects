from flask import g
import sqlite3


DATABASE = "users.db"


def init_db():
    db = sqlite3.connect(DATABASE ,timeout=10,check_same_thread = False)
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, role TEXT NOT NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS students(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, roll INTEGER UNIQUE NOT NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS attendance(id INTEGER PRIMARY KEY AUTOINCREMENT, roll INTEGER NOT NULL, status TEXT NOT NULL, date TEXT NOT NULL )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS audit_log(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, action TEXT NOT NULL, timestamp DATETIME NOT NULL )""")
    db.commit()
    db.close()


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE , timeout = 10,check_same_thread = False)
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db',None)
    if db is not None:
        db.close()

