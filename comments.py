import db

def add_comment(book_id: int, user_id: int, content: str) -> None:
    sql = "INSERT INTO book_comments (book_id, user_id, content) VALUES (?, ?, ?)"
    db.execute(sql, [book_id, user_id, content.strip()])

def get_comments(book_id: int):
    sql = """
        SELECT c.content, c.created_at, u.username AS author
        FROM book_comments c
        JOIN users u ON u.id = c.user_id
        WHERE c.book_id = ?
        ORDER BY c.created_at DESC
    """
    return db.query(sql, [book_id])

def get_comment_count(book_id: int) -> int:
    row = db.query("SELECT COUNT(*) AS n FROM book_comments WHERE book_id=?", [book_id])
    return row[0]["n"] if row else 0
