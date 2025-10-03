import db

def upsert_rating(book_id: int, user_id: int, value: int) -> None:
    sql = """
        INSERT INTO ratings (book_id, user_id, value)
        VALUES (?, ?, ?)
        ON CONFLICT(book_id, user_id) DO UPDATE SET value=excluded.value
    """
    db.execute(sql, [book_id, user_id, value])

def get_avg_rating(book_id: int):
    row = db.query(
        "SELECT ROUND(AVG(value), 1) AS avg_rating FROM ratings WHERE book_id=?",
        [book_id]
    )
    return row[0]["avg_rating"] if row and row[0]["avg_rating"] is not None else None

def get_creator_rating(book_id: int):
    row = db.query("SELECT rating FROM books WHERE id=?", [book_id])
    if not row:
        return None
    return row[0]["rating"]
