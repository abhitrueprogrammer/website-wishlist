#TODO:  Clean register and login, add remove button
from flask import Flask , render_template, flash, redirect, request, session
from flask_session import Session
from helper import login_required, apology, watchExists, get_image_url
from werkzeug.security import check_password_hash, generate_password_hash
# from flask_session import Session
# from werkzeug.security import check_password_hash, generate_password_hash
# Session(app)
import sqlite3
app = Flask(__name__)
db = sqlite3.connect("watch.db", check_same_thread=False)
#TODO Use signed cookies instead
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
#understand this and make button show username. Later add ability to show user profile
@app.context_processor
def base():
    login_verb = "login" 
    if session.get("user_id") is not None:
        login_verb = "logout"
    return dict(login_verb = login_verb)

@app.route("/", methods=["POST", "GET"])
def index():
    # if request.method() == "POST":
    return render_template("index.html")
@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "GET":
        keyword = request.args.get("searched")
        print("Keyboard is", keyword)
        if keyword == None:
            return apology("Please enter a watchname", 400)
        watches = db.execute("SELECT id, watchname, reference FROM watches WHERE watchname LIKE ? or reference LIKE ?", ("%" + keyword + "%","%" + keyword + "%")).fetchall()
        print(watches)
        return render_template("search.html", watches = watches)
    if request.method == "POST":
        watch_id = request.form.get("watchinfo")
        if request.form.get("type") == "info":
            if not(watchExists(watch_id)):
                return apology("INTERNAL ERROR(watch not found)", 400)
            watch_info = db.execute("SELECT * FROM watches WHERE id == ?", (watch_id,))
            return render_template("info.html", watch_info=watch_info)
        # CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, 
        # hash TEXT NOT NULL, cash NUMERIC NOT NULL DEFAULT 10000.00);
@app.route("/addCart", methods=["POST"])
@login_required
def addCart():
        number = 1
        watch_id = request.form.get("watchid")
        print(watch_id)
        if request.form.get("type") == "cart":
            if  not(watchExists(watch_id)):
                return apology("INTERNAL ERROR: Watch not found in DB", 400)
            db.execute(
                "INSERT INTO cart (userid, watchid, quantity) VALUES(?,?,?);",
                (session["user_id"],
                watch_id,
                number)
            )
            db.commit()
            flash("Added to cart", category="message")
            return redirect("/")
        else:
            return apology("not implemented yet", 404)

@app.route("/cart")
@login_required
def cart():
    basket = db.execute("SELECT watches.id, watches.watchname, watches.image_url FROM cart, users, watches where users.id == cart.userid and watches.id == cart.watchid and users.id == ?;",(session["user_id"],)).fetchall()
    for row in basket:
        print("checking image for", row[2])
        if row[2] == None:
            db.execute("""UPDATE watches
    SET image_url = ?
    WHERE
    id == ?""", (get_image_url(row[1]),row[0]))
    basket = basket = db.execute("SELECT watches.watchname, watches.image_url FROM cart, users, watches where users.id == cart.userid and watches.id == cart.watchid and users.id == ?;",(session["user_id"],)).fetchall()
    return render_template("cart.html", basket = basket)
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username == ?", (request.form.get("username"),)
        ).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1:
            return apology("invalid username and/or password", 400)
        print(rows[0][2], request.form.get("password"))
        if not(check_password_hash(rows[0][2], request.form.get("password"))):
            return apology("invalid password", 400)
        # Remember which user has logged in
        session["user_id"] = rows[0][0]
        flash("You are logged  in", category="message")
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

# @app.route("/logout")
# def logout():
#     """Log user out"""

#     # Forget any user_id
#     session.clear()

#     # Redirect user to login form
#     return redirect("/")
@app.route("/register", methods=["GET", "POST"])
def register():
    # get a register of top 100 used passwords from web and don't allow user to select those as password
    """Register user"""
    if request.method == "POST":
        user = request.form.get("username")
        # Ensure username was submitted
        if not user:
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password and confirmation passwords are the same
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("The passwords do not match!", 400)
        users_with_same_name = db.execute("SELECT COUNT(*) FROM users WHERE username == ?", (user,)).fetchall()[0][0]
        if ( users_with_same_name!= 0):
            return apology("Duplicate username!", 400)

            # TODO Display a warning instead of a new webpage.
        print(request.form.get("password"))
        password_hash = generate_password_hash(request.form.get("password"))

        db.execute(
            "INSERT INTO users(username, hash) VALUES(?, ?)", (user, password_hash)
        )
        db.commit()
        return render_template("success.html")
    else:
        return render_template("register.html")