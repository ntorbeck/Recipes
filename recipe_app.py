from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import get_dict, login_required
from cs50 import SQL

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

# Configure CS50 class to use SQLite database
db = SQL("sqlite:///recipe.db")

@app.route('/')
@login_required
def index():
    """Show user's favorites"""

    # Query database and convert lists to dicts
    type_rows = db.execute("SELECT * FROM types")
    types = get_dict("type_id", type_rows)

    cuisine_rows = db.execute("SELECT * FROM cuisines")
    cuisines = get_dict("cuisine_id", cuisine_rows)

    appliance_rows = db.execute("SELECT * FROM appliances")
    appliances = get_dict("appliance_id", appliance_rows)

    # https://stackoverflow.com/questions/10562915/selecting-rows-with-id-from-another-table
    # Query database for all the recipes the user has favorited
    recipes = db.execute("SELECT recipe_id, title, veggie, vegan, gluten, type_id, cuisine_id, prep_time, cook_time, appliance_id, servings FROM recipes WHERE recipe_id IN (SELECT recipe_id FROM favorites WHERE user_id = :user_id)",
                           user_id=session["user_id"])

    # Maps ids to names without need for complicated INNER JOIN
    for recipe in recipes:
        recipe['type_id'] = types[recipe['type_id']]['type_name']
        recipe['subtype'] = types[recipe['type_id']]['subtype']
        recipe['cuisine_id'] = cuisines[recipe['cuisine_id']]['cuisine_name']
        recipe['appliance_id'] = appliances[recipe['appliance_id']]['appliance_name']

    return render_template("table.html", favorites=True, recipes=recipes)


@app.route("/browse")
@login_required
def browse():
    """Show all recipes"""

    type_rows = db.execute("SELECT * FROM types")
    types = get_dict("type_id", type_rows)

    cuisine_rows = db.execute("SELECT * FROM cuisines")
    cuisines = get_dict("cuisine_id", cuisine_rows)

    appliance_rows = db.execute("SELECT * FROM appliances")
    appliances = get_dict("appliance_id", appliance_rows)

    # Query database for all recipes
    recipes = db.execute("SELECT recipe_id, title, veggie, vegan, gluten, type_id, cuisine_id, prep_time, cook_time, appliance_id, servings FROM recipes")

    for recipe in recipes:
        recipe['type_id'] = types[recipe['type_id']]['type_name']
        recipe['subtype'] = types[recipe['type_id']]['subtype']
        recipe['cuisine_id'] = cuisines[recipe['cuisine_id']]['cuisine_name']
        recipe['appliance_id'] = appliances[recipe['appliance_id']]['appliance_name']

    return render_template("table.html", browse=True, recipes=recipes)


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    valid_name = False
    username = request.args.get("username")

    # If no username is provided return false
    if len(username) < 1:
        valid_name = False

    else:
        # Query database for username
        rows = db.execute("SELECT username FROM users WHERE username = :username",
                          username=username)

        # If username exists return false, else true
        if len(rows) >= 1:
            valid_name = False
        else:
            valid_name = True

    return jsonify(valid_name)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Inialize error checking
        errors = []

        # Ensure username was submitted
        if not request.form.get("username"):
            errors.append('Please provide a username.')

        # Ensure password was submitted
        elif not request.form.get("password"):
            errors.append('Please provide a password.')

        # If errors exist, render error template
        if not errors == []:
            code = '403'
            return render_template("error.html", code=code, message=errors)

        # Query database for username
        rows = db.execute("SELECT user_id, username, hash FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if not len(rows) == 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("error.html", code='403', message=['Invalid username and/or password.'])

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
# Modified login
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Inialize error checking
        errors = []

        # Ensure a username was provided
        if not request.form.get("username"):
            errors.append('Please provide username.')

        # Ensure a password was provided
        elif not request.form.get("password"):
            errors.append('Please provide password.')

        # Ensure password was retyped
        elif not request.form.get("confirmation"):
            errors.append('Please retype password.')

        # Ensure retyped password matches original password
        elif not request.form.get("password") == request.form.get("confirmation"):
            errors.append('Passwords do not match.')

        # Ensure user gave the correct secret code
        elif not request.form.get("secret_code") == "tacos":
            errors.append('Secret Code is invalid.')

        # If errors exist, render error template
        if not errors == []:
            code = '400'
            return render_template("error.html", code=code, message=errors)

        # Hash password for security
        password = generate_password_hash(request.form.get("password"))

        # Insert new user into database
        new = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                         username=request.form.get("username"), hash=password)

        # If INSERT fails, return error
        if not new:
            return render_template("error.html", code='400', message=['Username unavailable'])

        # Log in new user
        rows = db.execute("SELECT user_id FROM users WHERE username = :username",
                          username=request.form.get("username"))

        session["user_id"] = rows[0]["user_id"]

        # Show success message
        flash('You were successfully registered and logged in!', category='info')

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/recipe_gen", methods=["GET"])
@login_required
def get_char_gen():
    """Renders recipe creator"""
    return render_template("recipe_gen.html")


@app.route('/your_recipes')
@login_required
def your_recipes():
    """Show user's submitted recipes"""

    type_rows = db.execute("SELECT * FROM types")
    types = get_dict("type_id", type_rows)

    cuisine_rows = db.execute("SELECT * FROM cuisines")
    cuisines = get_dict("cuisine_id", cuisine_rows)

    appliance_rows = db.execute("SELECT * FROM appliances")
    appliances = get_dict("appliance_id", appliance_rows)

    # Query database for all the recipes the user has submitted
    recipes = db.execute("SELECT recipe_id, title, veggie, vegan, gluten, type_id, cuisine_id, prep_time, cook_time, appliance_id, servings FROM recipes WHERE user_id = :user_id",
                           user_id=session["user_id"])

    for recipe in recipes:
        recipe['type_id'] = types[recipe['type_id']]['type_name']
        recipe['subtype'] = types[recipe['type_id']]['subtype']
        recipe['cuisine_id'] = cuisines[recipe['cuisine_id']]['cuisine_name']
        recipe['appliance_id'] = appliances[recipe['appliance_id']]['appliance_name']

    return render_template("table.html", your_rep=True, recipes=recipes)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template("error.html", code=e.code, message=[e.name])


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)