import secrets

from flask import Flask
from flask import abort, redirect, render_template, request, flash, url_for, session


import db
import config
import user
import books
import comments
import ratings


app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
   if "user_id" not in session:
      abort(403)

def check_csrf():
    if "csrf_token" not in request.form:
       abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
       abort(403)

@app.route("/")
def main():
   return render_template("index.html")

@app.route("/user/<int:user_id>")
def user_page(user_id):
    user_, books = user.get_user_page_data(user_id)
    if not user_:
        return abort(404)
    return render_template("user_page.html", user_=user_, books=books)

@app.route("/search")
def search():
    query = request.args.get("query")
    results = books.search(query) if query else []
    return render_template("search.html", query=query, results=results)

@app.route("/new_book")
def new_book():
    require_login()
    return render_template("add_book.html")


@app.route("/create_book", methods=["POST"])
def create_book():
  require_login()
  check_csrf()

  title = request.form["title"]
  if not title or len(title) > 50:
    abort(403)
  author = request.form["author"]
  if not author or len(author) > 50:
    abort(403)
  genre = request.form["genre"]
  year = request.form["year"]
  language = request.form["language"]
  comment = request.form["comment"]
  rating = request.form["rating"]
  if rating == "":
    rating = None
  user_id = session["user_id"]
  
  books.add_book(title, author, genre, year, language, comment, rating, user_id)

  flash("Book added succesfully!")
  return redirect("dashboard")

@app.route("/edit_book/<int:book_id>", methods=["GET", "POST"])
def edit_book_route(book_id):
    require_login()
    user_id = session["user_id"]

    if request.method == "POST":
        check_csrf()

        title = request.form["title"]
        author = request.form["author"]
        genre = request.form["genre"]
        year = request.form["year"]
        language = request.form["language"]
        comment = request.form["comment"]
        rating = request.form["rating"]

        if rating == "":
            rating = None

        books.edit_book(
            book_id,
            title,
            author,
            genre,
            year,
            language,
            comment,
            rating,
            user_id
        )

        flash("Book updated successfully!")
        return redirect("/dashboard")

    book = db.query("SELECT * FROM books WHERE id=? AND user_id=?", [book_id, user_id])
    if not book:
        abort(403)
    return render_template("edit_book.html", book=book[0])


@app.route("/delete_book/<int:book_id>", methods=["POST"])
def delete_book_route(book_id):
    require_login()
    check_csrf()
    user_id = session["user_id"]
    books.delete_book(book_id, user_id)
    flash("Book deleted successfully!")
    return redirect("/dashboard")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        check_csrf()

    if request.method == "GET":
        return render_template("register.html")

    username = request.form["username"]
    password = request.form["password"]

    ok, err = user.create_user(username, password)
    if not ok:
        return render_template("register.html", error=err, username=username)

    return render_template("register.html", success="Username created successfully!", username=username)

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if password1 == "":
        flash("ERROR: Password can not be empty", "error")
        return redirect("register")
    if password1 != password2:
        flash("ERROR: Passwords do not match", "error")
        return redirect("register")

    ok, err = user.create_user(username, password1)
    if not ok:
        flash(f"ERROR: {err}", "error")
        return redirect("register")

    flash("Username created successfully", "success")
    return redirect("login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_id = user.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            flash("Login successful!", "success")
            return redirect("dashboard")
        else: 
            flash("ERROR: Invalid username or password", "error")
            return redirect("login")

    return render_template("login.html")

@app.route("/logout")
def logout():
    if "user_id" in session: 
        session.clear()
        flash("You have been logged out.", "success")
    return redirect("/")

@app.route("/dashboard")
def dashboard():
    require_login()
    user_books = db.query("SELECT * FROM books WHERE user_id = ?", [session["user_id"]])
    all_books = db.query("""
                        SELECT books.*, users.username, users.id AS owner_id
                        FROM books
                        JOIN users ON books.user_id = users.id
                        WHERE books.user_id != ? ORDER BY users.username
                        """, [session["user_id"]])
    
    return render_template("dashboard.html", user_books=user_books, all_books = all_books)    

@app.route("/books/<int:book_id>/rate", methods=["POST"])
def rate_book(book_id):
    require_login()
    check_csrf()
    user_id = int(session["user_id"])
    try:
        value = int(request.form.get("rating", 0))
    except ValueError:
        value = 0
    if value < 1 or value > 5:
        flash("Arvosanan tulee olla 1–5.", "error")
        return redirect(f"/books/{book_id}")

    ratings.upsert_rating(book_id, user_id, value)
    flash("Arvosana lisätty onnistuneesti", "success")
    return redirect(f"/books/{book_id}")



@app.route("/books/<int:book_id>/comments", methods=["GET", "POST"])
def book_comments(book_id):
    require_login()
    if request.method == "POST":
        check_csrf()
        user_id = session["user_id"]
        content = (request.form.get("content") or "").strip()
        if content:
            comments.add_comment(book_id, user_id, content)
        return redirect(f"/books/{book_id}/comments")

    comment_list = comments.get_comments(book_id)
    return render_template("book_comments.html", comments=comment_list, book_id=book_id)

@app.route("/books/<int:book_id>")
def book_detail(book_id):
    book = books.get_book(book_id)
    if not book:
        abort(404)
    avg_rating = ratings.get_avg_rating(book_id)
    creator_rating = ratings.get_creator_rating(book_id)
    comment_count = comments.get_comment_count(book_id)
    return render_template("book_detail.html",
                           book=book,
                           avg_rating=avg_rating,
                           creator_rating=creator_rating,
                           comment_count=comment_count)

@app.route("/books")
def books_list():
    genre = request.args.get("genre") or None
    rating_min = request.args.get("rating_min")
    rating_min = int(rating_min) if rating_min and rating_min.isdigit() else None

    all_genres = books.get_genres()
    items = books.list_books_filtered(genre=genre, rating_min=rating_min)

    return render_template("book_filtering.html",
                           books=items,
                           all_genres=all_genres,
                           selected_genre=genre,
                           selected_rating=rating_min)

if __name__ == "__main__":
    app.run(debug=True)