from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_mail import Mail, Message

from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import *
from scrabble.Classes import *
from scrabble.Values import *

from dotenv import load_dotenv
load_dotenv()
import os
#import magic

# if "dictionary" not in globals():
#     dictionary = open("scrabble/word_list.txt").read().splitlines()

app = Flask(__name__)
mail = Mail(app)
app.config['MAIL_SERVER']='smtp-mail.outlook.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'crissxcross2022@hotmail.com'
app.config['MAIL_PASSWORD'] = os.getenv("PASSWORD")
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

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
def home():
    return render_template("home.html")

@app.route("/main")
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
            return errorify("must provide username", "", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return errorify("must provide password", "", 403)

        # Ensure password has at least 6 characters
        if len(request.form.get("password")) < 6:
            return errorify("password must have at least 6 characters", "", 403)

        # Ensure password has a number
        if not has_number(request.form.get("password")):
            return errorify("password must have a number", "", 403)

        # Ensure confirmation matches password
        elif request.form.get("password") != request.form.get("confirmation"):
            return errorify("passwords do not match", "", 403)

        # Ensure that username does not already exist
        rows = db.execute("SELECT * FROM Users WHERE username = :username",
                          username=request.form.get("username"))
        if len(rows) != 0:
            return errorify("username already exists", "", 403)

        # Insert username and password hash
        db.execute("INSERT INTO Users (username, hash) VALUES(?, ?)", request.form.get("username"), generate_password_hash(request.form.get("password")))


        # Remember which user has logged in
        rows = db.execute("SELECT * FROM Users WHERE username = :username",
                          username=request.form.get("username"))
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/main")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    # Forgets any current user
    session.clear()

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return errorify("must provide username", "invalidlogin", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return errorify("must provide password", "invalidlogin", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return errorify("invalid username and/or password", "invalidlogin", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/main")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/main")

@app.route("/game", methods=["GET", "POST"])
def game():
    global new_game
    if request.method == "POST":
        # Ensure both names were submitted
        if not request.form.get("player1") or not request.form.get("player2"):
            return errorify("must provide names for both players", "", 403)
        
        # Create new game with players
        new_game = Game()
        players = [request.form.get("player1"), request.form.get("player2")]
        new_game.set_players(players)
        new_game.start_game()
        return redirect("/turn")
    else:
        return render_template("game.html")
    
@app.route("/turn", methods=["GET", "POST"])
def turn():
    if new_game.game_over:
        return render_template("game-over.html", winner=new_game.end_game())

    if request.method == "POST":
        word_in = request.form.get("word")
        row_in = request.form.get("row")
        col_in = request.form.get("col")
        direction_in = request.form.get("direction")

        # Ensure word exists
        if not word_in:
            return errorify("word not provided", "", 403)
        
        # Check row and col numbers
        if not 0 <= int(row_in) < BOARD_SIZE or not 0 <= int(col_in) < BOARD_SIZE:
            return errorify("row or column number invalid", "", 403)
        
        # Check direction
        if not direction_in:
            return errorify("direction not chosen", "", 403)
        else:
            direction_in = Direction.down if direction_in == "down" else Direction.right
        
        new_game.turn(word_in, [int(row_in), int(col_in)], direction_in)
        return render_template("turn.html", board=new_game.board.board, player=new_game.current_player, rack=new_game.current_player.rack)
        
    else:
        return render_template("turn.html", board=new_game.board.board, player=new_game.current_player, rack=new_game.current_player.rack)

@app.route("/test")
def test():
    return render_template("game-over.html", winner=["Denzel", 83])

@app.route("/why-crissxcross")
def whycrissxcross():
    return render_template("why-crissxcross.html")

@app.route("/what-is-scrabble")
def whatisscrabble():
    return render_template("what-is-scrabble.html")

@app.route("/gameplay-tutorial")
def gameplaytutorial():
    return render_template("gameplay-tutorial.html")

@app.route("/wordoftheday")
def wordoftheday():
    return render_template("wordoftheday.html")

@app.route("/contact-us", methods=["GET", "POST"])
def contactus():
    # Forgets any current user
    session.clear()

    if request.method == "POST":

        full_name = request.form.get("full_name")
        username = request.form.get("username")
        email = request.form.get("email")
        subject = request.form.get("subject")
        feedback = request.form.get("feedback")
        files = request.files.get("uploaded_file")
        msg = Message("Feedback", sender="crissxcross2022@hotmail.com",  recipients=["crissxcross2022@hotmail.com"])
        msg.html = "This is the feedback we received from the following user: <br><br> Full name: <strong>{}</strong> <br><br> Username: <strong>{}</strong> <br><br> Email: <strong>{}</strong> <br><br> Subject: <strong>{}</strong> <br><br> Message: {}".format(full_name,username,email,subject,feedback)
  
        # mime = magic.from_file(files, mime=True)
        
        # with open(files,'rb') as f:
        #         msg.attach(filename=file_name, content_type=mime, data=f.read(), disposition=None, headers=None) 
        mail.send(msg)
        return render_template("form-submit.html")  
    else:
        return render_template("contact-us.html")

     

if __name__ == "__main__":
    app.run()