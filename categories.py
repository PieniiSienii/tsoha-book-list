import db

def all_categories():
    return db.query("SELECT id, name FROM categories ORDER BY name")

def get_for_book(book_id):
    rows = db.query("SELECT category_id FROM book_categories WHERE book_id=?", [book_id])
    return [r["category_id"] for r in rows]

def set_for_book(book_id, category_ids):
    db.execute("DELETE FROM book_categories WHERE book_id=?", [book_id])
    for cid in category_ids:
        db.execute(
            "INSERT OR IGNORE INTO book_categories (book_id, category_id) VALUES (?, ?)",
            [book_id, int(cid)]
        )
