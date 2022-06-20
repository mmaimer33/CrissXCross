from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import *
# from scrabble.Classes_old import *
# from scrabble.Values import *

# if "dictionary" not in globals():
#     dictionary = open("scrabble/word_list.txt").read().splitlines()

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///crissxcross.db")

@app.route("/")
def index():
    if session:
        user_id = session["user_id"]
        username = db.execute("SELECT username FROM Users WHERE id = :user_id", user_id = user_id)[0]["username"]
        return render_template("index.html", username=username)
    else:
        return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    # Forget any current user
    session.clear()

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return errorify("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return errorify("must provide password", 403)

        # Ensure password has at least 6 characters
        if len(request.form.get("password")) < 6:
            return errorify("password must have at least 6 characters", 403)

        # Ensure password has a number
        if not has_number(request.form.get("password")):
            return errorify("password must have a number", 403)

        # Ensure confirmation matches password
        elif request.form.get("password") != request.form.get("confirmation"):
            return errorify("passwords do not match", 403)

        # Ensure that username does not already exist
        rows = db.execute("SELECT * FROM Users WHERE username = :username",
                          username=request.form.get("username"))
        if len(rows) != 0:
            return errorify("username already exists", 403)

        # Insert username and password hash
        db.execute("INSERT INTO Users (username, hash) VALUES(?, ?)", request.form.get("username"), generate_password_hash(request.form.get("password")))


        # Remember which user has logged in
        rows = db.execute("SELECT * FROM Users WHERE username = :username",
                          username=request.form.get("username"))
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    # Forgets any current user
    session.clear()

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return errorify("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return errorify("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return errorify("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/test")
def test():
    return render_template("test.html")

if __name__ == "__main__":
    app.run()