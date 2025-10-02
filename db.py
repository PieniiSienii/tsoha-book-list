import sqlite3
from flask import g

DB_PATH = "database.db"

def get_connection():
    con = sqlite3.connect(DB_PATH, timeout=5.0, isolation_level=None)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA foreign_keys=ON")
    return con

def execute(sql, params=()):
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute("BEGIN")
        cur.execute(sql, params)
        last_id = cur.lastrowid
        con.commit()
        g.last_insert_id = last_id
        return last_id
    except sqlite3.IntegrityError:
        con.rollback()
        raise
    except Exception:
        con.rollback()
        raise
    finally:
        try:
            cur.close()
        finally:
            con.close()

def query(sql, params=()):
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        try:
            cur.close()
        finally:
            con.close()

def last_insert_id():
    return getattr(g, "last_insert_id", None)
