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
        """
        SELECT
            b.id,
            b.title,
            b.author,
            b.year,
            b.language,
            b.comment,     -- creator's description
            b.rating,      -- creator's rating
            b.user_id,
            u.username
        FROM books b
        JOIN users u ON u.id = b.user_id
        WHERE b.user_id = ?
        ORDER BY b.id DESC
        """,
        [user_id]
    )
    return user_, books


def get_user_stats(user_id: int):
    """Return stats for the user's page:
       - top 3 categories
       - top 3 books by average rating (fallback to creator rating if no user ratings)
       - summary numbers
    """
    top_categories = db.query("""
        SELECT
            c.name AS category_name,
            COUNT(*) AS total
        FROM books b
        JOIN book_categories bc ON bc.book_id = b.id
        JOIN categories c ON c.id = bc.category_id
        WHERE b.user_id = ?
        GROUP BY c.id, c.name
        ORDER BY total DESC, category_name ASC
        LIMIT 3
    """, [user_id])

    top_books_by_avg = db.query("""
        SELECT
            b.id,
            b.title,
            ROUND(AVG(r.value), 1) AS avg_rating,
            COUNT(r.user_id) AS ratings_count
        FROM books b
        JOIN ratings r ON r.book_id = b.id
        WHERE b.user_id = ?
        GROUP BY b.id, b.title
        HAVING ratings_count > 0
        ORDER BY avg_rating DESC, ratings_count DESC, b.title ASC
        LIMIT 3
    """, [user_id])

    fallback_top_books = []
    if not top_books_by_avg:
        fallback_top_books = db.query("""
            SELECT
                b.id,
                b.title,
                b.rating AS creator_rating
            FROM books b
            WHERE b.user_id = ? AND b.rating IS NOT NULL
            ORDER BY b.rating DESC, b.title ASC
            LIMIT 3
        """, [user_id])

    summary_rows = db.query("""
        SELECT
            (SELECT COUNT(*) FROM books WHERE user_id = ?) AS total_books,
            (SELECT COUNT(*)
               FROM ratings r
               JOIN books b2 ON b2.id = r.book_id
              WHERE b2.user_id = ?) AS total_ratings_received,
            (SELECT ROUND(AVG(r2.value), 1)
               FROM ratings r2
               JOIN books b3 ON b3.id = r2.book_id
              WHERE b3.user_id = ?) AS overall_avg_rating,
            (SELECT COUNT(*)
               FROM book_comments c
               JOIN books b4 ON b4.id = c.book_id
              WHERE b4.user_id = ?) AS total_comments_received
    """, [user_id, user_id, user_id, user_id])
    summary = summary_rows[0] if summary_rows else {
        "total_books": 0,
        "total_ratings_received": 0,
        "overall_avg_rating": None,
        "total_comments_received": 0,
    }

    return {
        "top_categories": top_categories,
        "top_books_by_avg": top_books_by_avg,
        "fallback_top_books": fallback_top_books,
        "summary": summary,
    }
