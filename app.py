from flask import Flask
from flask import redirect, render_template, request, flash, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import db
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key' 

def require_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper

@app.route("/")
def main():
   return render_template("index.html")



@app.route("/register")
def register():
  return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
  username = request.form["username"]
  password1 = request.form["password1"]
  password2 = request.form["password2"]

  if password1 == "":
    flash("ERROR: Password can not be empty", "error")
    return redirect(url_for("register"))

  if password1 != password2:
    flash("ERROR: Passwords do not match", "error")
    return redirect(url_for("register"))

  user_check = db.query("SELECT * FROM users WHERE username = ?", [username])
  if user_check:
      flash("ERROR: Username is already taken", "error")
      return redirect(url_for("register"))
  
  password_hash = generate_password_hash(password1)

  try:
      db.execute("INSERT INTO users (username, password_hash) VALUES (?,?)", [username,password_hash])
  except Exception as e:
      flash("ERROR: {e}", "error")
      return redirect(url_for("register"))

  flash("Username created successfully", "success")
  session["user_id"] = db.query("SELECT id FROM users WHERE username = ?", [username])[0]["id"]
  session["username"] = username
  return redirect(url_for("dashboard"))

@app.route("/login", methods=["GET","POST"])
def login():
  if request.method == "POST":
    username = request.form["username"]
    password = request.form["password"]
    user = db.query("SELECT * FROM users WHERE username = ?", [username])
    if not user:
      flash("ERROR: Invalid username or password", "error")
      return redirect(url_for("login"))
    user = user[0]
    stored_password_hash = user["password_hash"]

    if not check_password_hash(stored_password_hash,password):
      flash("ERROR: Invalid username or password", "error")
      return redirect(url_for("login"))
    
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    flash("Login successful!", "success")
    return redirect(url_for("dashboard"))
  return render_template("login.html")

@app.route("/logout")
def logout():
    del session["username"]
    flash("You have been logged out.", "success")
    return redirect(url_for("main"))

@app.route("/dashboard")
@require_login
def dashboard():
    user_books = db.query("SELECT * FROM books WHERE user_id = ?", [session["user_id"]])
    all_books = db.query("""
                        SELECT books.*, users.username FROM books
                        JOIN users ON books.user_id = users.id
                        WHERE books.user_id != ? ORDER BY users.username
                        """, [session["user_id"]])
    
    return render_template("dashboard.html", user_books=user_books, all_books = all_books)    

@app.route("/add_book", methods=["GET","POST"])
@require_login
def add_book():
    if request.method =="POST":
      print(" User is logged in:", session["user_id"])
      print(" Form data received:", request.form)
      
      title = request.form.get("title")
      author = request.form.get("author")
      
      if not title or not author:
          flash("Title and author are required.", "error")
          print(" Missing title or author")
          return redirect(url_for("dashboard"))

      print(" Attempting to insert book:", title, author)

      try:
          db.execute(
              "INSERT INTO books (user_id, title, author, genre, year, language, comment, rating) "
              "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (session["user_id"], title, author, request.form.get("genre"),
                request.form.get("year"), request.form.get("language"), 
                request.form.get("comment"), request.form.get("rating"))
          )
          flash("Book added successfully!", "success")
      except Exception as e:
          flash(f"Database error: {e}", "error")

      return redirect(url_for("dashboard"))

    return render_template("add_book.html")

@app.route("/edit_book/<int:id>", methods=["GET", "POST"])
@require_login
def edit_book(id):
    book = db.query("SELECT * FROM books WHERE id = ?", [id])
    if not book:
        flash("Book not found.", "error")
        return redirect(url_for("dashboard"))
    book = book[0]

    if book["user_id"] != session["user_id"]:
        flash("You cannot edit this book.", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        genre = request.form.get("genre")
        year = request.form.get("year")
        language = request.form.get("language")
        comment = request.form.get("comment")
        rating = request.form.get("rating")

        try:
            db.execute("""
                UPDATE books SET title=?, author=?, genre=?, year=?, language=?, comment=?, rating=?
                WHERE id=?
            """, [title, author, genre, year, language, comment, rating, id])
            flash("Book updated successfully!", "success")
        except Exception as e:
            flash(f"Database error: {e}", "error")

        return redirect(url_for("dashboard"))

    return render_template("edit_book.html", book=book)
@app.route("/delete_book/<int:id>", methods=["POST"])
@require_login
def delete_book(id):
    book = db.query("SELECT * FROM books WHERE id = ?", [id])
    if not book:
        flash("Book not found.", "error")
        return redirect(url_for("dashboard"))
    book = book[0]

    if book["user_id"] != session["user_id"]:
        flash("You cannot delete this book.", "error")
        return redirect(url_for("dashboard"))

    try:
        db.execute("DELETE FROM books WHERE id = ?", [id])
        flash("Book deleted successfully!", "success")
    except Exception as e:
        flash(f"Database error: {e}", "error")

    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)