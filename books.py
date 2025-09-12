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
    

# def edit_book(book_id):
#     book = db.query("SELECT * FROM books WHERE id = ?", [id])
#     if not book:
#         flash("Book not found.", "error")
#         return redirect(url_for("books.dashboard"))
#     book = book[0]

#     if book["user_id"] != session["user_id"]:
#         flash("You cannot edit this book.", "error")
#         return redirect(url_for("boks.dashboard"))

#     if request.method == "POST":
#         title = request.form.get("title")
#         author = request.form.get("author")
#         genre = request.form.get("genre")
#         year = request.form.get("year")
#         language = request.form.get("language")
#         comment = request.form.get("comment")
#         rating = request.form.get("rating")

#         try:
#             db.execute("""
#                 UPDATE books SET title=?, author=?, genre=?, year=?, language=?, comment=?, rating=?
#                 WHERE id=?
#             """, [title, author, genre, year, language, comment, rating, id])
#             flash("Book updated successfully!", "success")
#         except Exception as e:
#             flash(f"Database error: {e}", "error")

#         return redirect(url_for("books.dashboard"))

#     return render_template("edit_book.html", book=book)

# @books_bp.route("/delete_book/<int:id>", methods=["POST"])
# @require_login
# def delete_book(id):
#     book = db.query("SELECT * FROM books WHERE id = ?", [id])
#     if not book:
#         flash("Book not found.", "error")
#         return redirect(url_for("books.dashboard"))
#     book = book[0]

#     if book["user_id"] != session["user_id"]:
#         flash("You cannot delete this book.", "error")
#         return redirect(url_for("books.dashboard"))

#     try:
#         db.execute("DELETE FROM books WHERE id = ?", [id])
#         flash("Book deleted successfully!", "success")
#     except Exception as e:
#         flash(f"Database error: {e}", "error")

#     return redirect(url_for("books.dashboard"))
