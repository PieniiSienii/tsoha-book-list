import db
import ratings

def add_book(title, author, genre, year, language, comment, rating, user_id):
    sql = """
        INSERT INTO books (title, author, genre, year, language, comment, rating, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
    db.execute(sql, [title, author, genre, year, language, comment, rating, user_id])

    book_id = db.last_insert_id()

    # jos haluat synkata omistajan arvosanan ratings-tauluun
    if rating is not None:
        try:
            r = int(rating)
            if 1 <= r <= 5:
                ratings.upsert_rating(book_id, user_id, r)
        except Exception:
            pass


def search(query):
    sql = """SELECT id, title, author, genre, year, language, comment, rating
             FROM books
             WHERE title LIKE ? OR author LIKE ?"""
    return db.query(sql, [f"%{query}%", f"%{query}%"])

def edit_book(book_id, title, author, genre, year, language, comment, rating, user_id):
    sql = """UPDATE books
             SET title=?, author=?, genre=?, year=?, language=?, comment=?, rating=?
             WHERE id=? AND user_id=?"""
    db.execute(sql, [title, author, genre, year, language, comment, rating, book_id, user_id])

    if rating is not None:
        try:
            r = int(rating)
            if 1 <= r <= 5:
                ratings.upsert_rating(book_id, user_id, r)
        except Exception:
            pass

def delete_book(book_id, user_id):
    book = db.query("SELECT id FROM books WHERE id=? AND user_id=?", [book_id, user_id])
    if not book:
        raise Exception("You do not have permission to delete this book!")

    sql = "DELETE FROM books WHERE id=? AND user_id=?"
    db.execute(sql, [book_id, user_id])

def get_book(book_id: int):
    sql = """SELECT id, title, author, genre, year, language, comment, rating, user_id
             FROM books WHERE id=?"""
    rows = db.query(sql, [book_id])
    return rows[0] if rows else None

def get_genres():
    rows = db.query("SELECT DISTINCT genre FROM books WHERE genre IS NOT NULL AND genre <> '' ORDER BY genre")
    return [r["genre"] for r in rows]

def list_books_filtered(genre=None, rating_min=None):
    base = """
      SELECT b.id, b.title, b.author, b.genre, b.year, b.language, b.comment, b.rating,
             ROUND(AVG(r.value), 1) AS avg_rating
      FROM books b
      LEFT JOIN ratings r ON r.book_id = b.id
    """
    where = []
    params = []

    if genre:
        where.append("b.genre = ?")
        params.append(genre)

    where_sql = (" WHERE " + " AND ".join(where)) if where else ""
    group_by = " GROUP BY b.id"
    having = ""
    if rating_min is not None:
        having = " HAVING AVG(r.value) >= ?"
        params.append(int(rating_min))

    order_by = " ORDER BY b.id DESC"
    sql = base + where_sql + group_by + having + order_by
    return db.query(sql, params)

