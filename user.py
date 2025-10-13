import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import db

def create_user(username, password):
    password_hash = generate_password_hash(password)
    try:
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        return True, None
    except sqlite3.IntegrityError:
        return False, "Username already taken"


def get_user(user_id):
    sql = "SELECT Id, username FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0] if result else None

def check_login(username, password):
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])
    if not result:
        return None

    user_id = result[0]["id"]
    password_hash = result[0]["password_hash"]
    if check_password_hash(password_hash, password):
        return user_id
    else:
        return None

def get_user_page_data(user_id):
    user_rows = db.query(
        "SELECT id, username FROM users WHERE id = ?",
        [user_id]
    )
    if not user_rows:
        return None, None
    user_ = user_rows[0]

    books = db.query(
        """SELECT b.id, b.title, b.author, b.user_id, u.username
           FROM books b
           JOIN users u ON b.user_id = u.id
           WHERE b.user_id = ?
           ORDER BY b.id DESC""",
        [user_id]
    )
    return user_, books
