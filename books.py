# books.py
import db

def add_book(title, author, year, language, comment, rating, user_id):
    sql = """
        INSERT INTO books (title, author, year, language, comment, rating, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    db.execute(sql, [title, author, year, language, comment, rating, user_id])
    row = db.query("SELECT last_insert_rowid() AS id")
    return row[0]["id"]

def edit_book(*, book_id, title, author, year, language, comment, rating, user_id):
    sql = """
        UPDATE books
           SET title = ?, author = ?, year = ?, language = ?, comment = ?, rating = ?
         WHERE id = ? AND user_id = ?
    """
    db.execute(sql, [title, author, year, language, comment, rating, book_id, user_id])

def get_book(book_id):
    rows = db.query("SELECT * FROM books WHERE id=?", [book_id])
    return rows[0] if rows else None

def search(query):
    q = f"%{(query or '').strip().lower()}%"
    sql = """
        SELECT id, title, author, year
        FROM books
        WHERE lower(title) LIKE ? OR lower(author) LIKE ?
        ORDER BY title
    """
    return db.query(sql, [q, q])

def delete_book(book_id, user_id):
    book = db.query("SELECT id FROM books WHERE id=? AND user_id=?", [book_id, user_id])
    if not book:
        raise Exception("Sinulla ei ole oikeutta poistaa tätä kirjaa!")

    sql = "DELETE FROM books WHERE id=? AND user_id=?"
    db.execute(sql, [book_id, user_id])

def list_books_filtered(category_id=None, rating_min=None):
    params = []
    sql = """
        SELECT
            b.id,
            b.title,
            b.author,
            b.year,
            COALESCE(avg_r.avg_rating, NULL) AS avg_rating,
            COALESCE(GROUP_CONCAT(c.name, ', '), '') AS categories
        FROM books b
        LEFT JOIN book_categories bc ON bc.book_id = b.id
        LEFT JOIN categories c ON c.id = bc.category_id
        LEFT JOIN (
            SELECT book_id, AVG(value) AS avg_rating
            FROM ratings
            GROUP BY book_id
        ) AS avg_r ON avg_r.book_id = b.id
    """

    # WHERE vain jos kategoriafiltteri on käytössä
    if category_id is not None:
        sql += " WHERE bc.category_id = ?"
        params.append(int(category_id))

    sql += " GROUP BY b.id"

    # HAVING avg suodatus vain jos rating_min annettu
    if rating_min is not None:
        sql += " HAVING avg_r.avg_rating >= ?"
        params.append(int(rating_min))

    sql += " ORDER BY b.title"

    return db.query(sql, params)