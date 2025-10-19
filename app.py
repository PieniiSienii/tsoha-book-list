import secrets
from datetime import datetime


from flask import Flask
from flask import abort, redirect, render_template, request, flash, session


import db
import config
import user
import books
import comments
import ratings
import categories


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
    all_categories = categories.all_categories()
    return render_template("add_book.html", categories=all_categories)


@app.route("/create_book", methods=["POST"])
def create_book():
    require_login()
    check_csrf()

    title = (request.form.get("title") or "").strip()
    author = (request.form.get("author") or "").strip()
    year = request.form.get("year") or None
    language = (request.form.get("language") or "").strip() or None
    comment = (request.form.get("comment") or "").strip() or None
    rating = request.form.get("rating") or None
    category_ids = request.form.getlist("categories")  # <— monivalinta

    if not title or len(title) > 200:
        flash("Kirjan nimi vaaditaan (max 200).", "error")
        return redirect("/new_book")
    if not author or len(author) > 200:
        flash("Kirjailija vaaditaan (max 200).", "error")
        return redirect("/new_book")

    try:
        year = int(year) if year not in ("", None) else None
    except ValueError:
        flash("Vuosi ei ole numero.", "error")
        return redirect("/new_book")

    try:
        rating = int(rating) if rating not in ("", None) else None
    except ValueError:
        rating = None

    if not category_ids:
        flash("Valitse vähintään yksi luokka.", "error")
        return redirect("/new_book")

    user_id = session["user_id"]

    # HUOM: books.add_book ei enää odota genreä
    book_id = books.add_book(title, author, year, language, comment, rating, user_id)

    categories.set_for_book(book_id, category_ids)

    flash("Kirja lisätty onnistuneesti!", "success")
    return redirect("/dashboard")

from datetime import datetime
from flask import render_template, request, redirect, flash, abort, session

@app.route("/edit_book/<int:book_id>", methods=["GET", "POST"])
def edit_book_route(book_id):
    require_login()
    user_id = session["user_id"]

    if request.method == "POST":
        check_csrf()

        title = (request.form.get("title") or "").strip()
        author = (request.form.get("author") or "").strip()
        year = request.form.get("year") or None
        language = (request.form.get("language") or "").strip() or None
        comment = (request.form.get("comment") or "").strip() or None
        rating = request.form.get("rating") or None
        category_ids = request.form.getlist("categories")  # -> ["1","2",...]

        if not title or not author:
            flash("Kirjan nimi ja kirjailija ovat pakollisia.", "error")
            return redirect(f"/edit_book/{book_id}")
        if not category_ids:
            flash("Valitse vähintään yksi luokka.", "error")
            return redirect(f"/edit_book/{book_id}")

        try:
            year = int(year) if year not in ("", None) else None
        except ValueError:
            flash("Vuosi ei ole numero.", "error")
            return redirect(f"/edit_book/{book_id}")
        try:
            rating = int(rating) if rating not in ("", None) else None
        except ValueError:
            rating = None

        books.edit_book(
            book_id=book_id,
            title=title,
            author=author,
            year=year,
            language=language,
            comment=comment,
            rating=rating,
            user_id=user_id
        )

        # Muunna kategoria-ID:t kokonaisluvuiksi, jos setteri sitä odottaa
        categories.set_for_book(book_id, [int(x) for x in category_ids])

        flash("Kirja päivitetty.", "success")
        return redirect("/dashboard")

    row = db.query("SELECT * FROM books WHERE id=? AND user_id=?", [book_id, user_id])
    if not row:
        abort(403)
    book = row[0]

    all_categories = categories.all_categories()             # lista kategorioita
    selected_raw = categories.get_for_book(book_id)          # esim. [1,3,5] tai objekteja

    def to_id(x):
        return x.id if hasattr(x, "id") else (x.get("id") if isinstance(x, dict) else (x[0] if isinstance(x, (list, tuple)) else int(x)))
    selected_ids = {to_id(x) for x in selected_raw}

    return render_template(
        "edit_book.html",
        book=book,
        categories=all_categories or [],
        selected_categories=selected_ids,
        current_year=datetime.now().year,
    )

@app.route("/delete_book/<int:book_id>", methods=["POST"])
def delete_book_route(book_id):
    require_login()
    check_csrf()
    user_id = session["user_id"]
    try:
        books.delete_book(book_id, user_id)
        flash("Kirja poistettu onnistuneesti!", "success")
    except Exception as e:
        flash(str(e), "error")
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
        return redirect("/register")
    if password1 != password2:
        flash("ERROR: Passwords do not match", "error")
        return redirect("/register")

    ok, err = user.create_user(username, password1)
    if not ok:
        flash(f"ERROR: {err}", "error")
        return redirect("/register")

    flash("Username created successfully", "success")
    return redirect("/login")


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
            return redirect("/dashboard")
        else: 
            flash("ERROR: Invalid username or password", "error")
            return redirect("/login")

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

def safe_next_url():
    nxt = request.form.get("next") or request.args.get("next") or ""
    if isinstance(nxt, str) and nxt.startswith("/"):
        return nxt
    return "/dashboard"

@app.route("/books/<int:book_id>", methods=["GET", "POST"])
def book_detail(book_id):
    book = books.get_book(book_id)
    if not book:
        return abort(404)

    user_id = session.get("user_id")
    if user_id is not None:
        user_id = int(user_id)

    is_owner = (user_id == book["user_id"]) if user_id else False

    if request.method == "POST":
        check_csrf()

        if not user_id:
            flash("Please sign in to continue.", "error")
            return redirect(f"/books/{book_id}")

        if is_owner:
            flash("You cannot rate or comment your own book.", "error")
            return redirect(f"/books/{book_id}")

        action = request.form.get("action", "")

        if action == "feedback":
            r = request.form.get("rating", type=int)
            content = (request.form.get("content") or "").strip()

            if r is not None and 1 <= r <= 5:
                ratings.upsert_rating(book_id, user_id, r)
                flash("Rating saved.", "success")

            if content:
                comments.add_comment(book_id, user_id, content)
                flash("Comment added.", "success")

            if (r is None or not (1 <= r <= 5)) and not content:
                flash("Please give a rating or a comment.", "error")

            return redirect(safe_next_url())

        flash("Unknown action.", "error")
        return redirect(f"/dashboard")

    # GET-haara
    avg_rating = ratings.get_avg_rating(book_id)
    creator_rating = ratings.get_creator_rating(book_id)
    comment_count = comments.get_comment_count(book_id) if hasattr(comments, "get_comment_count") else None
    book_comments = comments.get_comments(book_id) if hasattr(comments, "list_for_book") else []
    all_ratings = ratings.get_avg_rating(book_id)
    return render_template(
        "book_detail.html",
        book=book,
        is_owner=is_owner,
        avg_rating=avg_rating,
        creator_rating=creator_rating,
        comment_count=comment_count,
        comments=book_comments,
        all_ratings=all_ratings,
    )

@app.route("/books")
def books_list():
    category_id = request.args.get("category_id") or None
    try:
        category_id = int(category_id) if category_id else None
    except ValueError:
        category_id = None

    rating_min = request.args.get("rating_min")
    try:
        rating_min = int(rating_min) if rating_min and rating_min.isdigit() else None
    except ValueError:
        rating_min = None

    all_cats = categories.all_categories()

    items = books.list_books_filtered(category_id=category_id, rating_min=rating_min)

    return render_template("book_filtering.html",
                           books=items,
                           all_genres=all_cats,          # jos templatessa on vielä 'all_genres'
                           selected_genre=category_id,   # jos templatessa on vielä 'selected_genre'
                           selected_rating=rating_min)


@app.context_processor
def inject_globals():
    return {"current_year": datetime.now().year}

if __name__ == "__main__":
    app.run(debug=True)