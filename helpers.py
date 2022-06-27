from flask import redirect, render_template, session
from functools import wraps

def errorify(message, error, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    if error == "invalidlogin" :
        return render_template("login.html", top=code, alertmsg=escape(message)) # im not sure if this messes it up by rendering login.html
    else: 
        return render_template("error.html", top=code, alertmsg=escape(message))
    

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def has_number(password):
    return any(char.isdigit() for char in password)