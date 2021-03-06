import os
import datetime
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
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


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///student.db")


# Essential methods connected with corresponding routes.
@app.route("/")
def index():
    """Show login page"""
    return render_template("home.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method=="GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        if (not username):
            return apology("You must provide Username.")
        password = request.form.get("password")
        if (not password):
            return apology("You must provide Password.")
        confirmation = request.form.get("confirmation")
        if (not confirmation):
            return apology("You must confirm your password.")
        if (password != confirmation):
            return apology("Password must match.")

        id_type = request.form.get("type")

        # Check if the username already exists or not.
        lis = db.execute("SELECT username FROM USERS")
        user_exists = False
        for j in range(len(lis)):
            if username == lis[j]['username']:
                user_exists = True
                break

        if user_exists:
            return apology("User already exist")
        else:
            k = generate_password_hash(password)
            db.execute("INSERT INTO USERS (username, hash, type) VALUES (?, ?, ?)", username, k, id_type)
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    # session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM USERS WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        if rows[0]["type"] == 'Teacher':
            return redirect("/teacher_dashboard")
        else:
            return render_template("student_dashboard.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/teacher_dashboard")
@login_required
def teacher_dashboard():
    return render_template("teacher_dashboard.html")

@app.route("/marks")
@login_required
def marks():
    return render_template("marks.html")


@app.route("/fees")
@login_required
def fees():
    return render_template("fees.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Get student record."""
    if request.method == "GET":
        return render_template("search.html")
    else:
        unique = request.form.get("unique")

        if unique == "":
            return apology("provide complete details")
        else:
            name = request.form.get("name")
            std = request.form.get("class")
            rows = db.execute("SELECT * FROM stud WHERE name=? and class=?",name, std)
            remaining_month_fees = datetime.datetime.now().month

            return render_template("profile.html",rows=rows, remaining_month_fees=remaining_month_fees)


@app.route("/enter", methods=["GET", "POST"])
@login_required
def enter():
    if(request.method == "GET"):
        return render_template("new.html")
    else:
        name = request.form.get("name")
        std = request.form.get("class")
        fees = request.form.get("fees")
        month = request.form.get("month")
        # print(month)

        # Validating student data.
        if not name:
            return apology('Enter student name.')
        if not month:
            return apology('Enter month of joining.')
        db.execute("INSERT INTO stud ('name', 'class', 'fees', 'month') VALUES (?,?,?,?)", name, std, fees, month)
        return render_template("unique.html")



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
