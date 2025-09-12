import db

def add_book(title, author, genre, year, language, comment, rating, user_id):
    sql = """
        INSERT INTO books (title, author, genre, year, language, comment, rating, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
    db.execute(sql, [title, author, genre, year, language, comment, rating, user_id])

    book_id = db.last_insert_id()

    sql = "INSERT INTO added_books (book_id, user_id) VALUES (?, ?)"
    db.execute(sql, [book_id, user_id])

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

def delete_book(book_id, user_id):
    book = db.query("SELECT id FROM books WHERE id=? AND user_id=?", [book_id, user_id])
    if not book:
        raise Exception("You do not have permission to delete this book!")

    sql = "DELETE FROM books WHERE id=? AND user_id=?"
    db.execute(sql, [book_id, user_id])