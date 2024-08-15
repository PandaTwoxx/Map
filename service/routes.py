import uuid
import os
import pickle
import os.path
import re
import mysql.connector

from service.classes import User, Location
from flask import Flask, render_template, request, redirect, url_for, abort, flash
from waitress import serve
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    current_user,
    logout_user,
)
from http import HTTPStatus
from service.utils import keygen, geo_code


load_dotenv()

geocoding_api_key = os.getenv("GEO_CODING_API")
googlemaps_api_key = os.getenv("GOOGLE_MAPS_API")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
db_host = os.getenv("DB_HOST")

users = [User]

app = Flask(__name__)

# Flask init
app.config["SECRET_KEY"] = uuid.uuid4().hex
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = db_host
app.config["MYSQL_ROOT_PASSWORD"] = db_password
app.config["MYSQL_DATABASE"] = db_name

mysql = mysql.connector.connect(
    host=app.config["MYSQL_HOST"],
    user=app.config["MYSQL_USER"],
    password=app.config["MYSQL_ROOT_PASSWORD"],
    database=app.config["MYSQL_DATABASE"],
    port=3306,
)

# Create mysql cursor
cursor = mysql.cursor()

# test the connection
cursor.execute("SELECT DATABASE()")
data = cursor.fetchone()
# if you see the following message in your terminal -- you did everything correct
print("_________________________SUCCESS!___________________________")
print("Connected to database:", data[0])

# close the cursor and connection objects
cursor.close()

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "/login_page"
login_manager.refresh_view = "/login_page"
login_manager.needs_refresh_message = (
    "To protect your account, please reauthenticate to access this page."
)
login_manager.needs_refresh_message_category = "info"


def validate_form(user: User):
    email_regex = ""
    with open("regex.txt", "r") as file:
        email_regex = file.readline()
        file.close()
    pattern = re.compile(email_regex)

    for i in users:
        if i.email == user.email:
            return "Email in use"
        if i.username == user.username:
            return "Username in use"
    if len(user.password) < 8:
        return "Invalid password(Must be 8 characters)"
    if len(user.username) < 1:
        return "Invalid username"
    if len(user.email) < 1:
        return "Invalid Email"
    if len(user.firstname) < 1:
        return "Invalid first name"
    if len(user.lastname) < 1:
        return "Invalid last name"
    if not (pattern.match(user.email)):
        return "Invalid email"
    return "valid"


@app.route("/login_page", methods=["GET"])
def login_page():
    if "status" in request.form:
        return render_template("login.html", e="Username or password incorrect")
    return render_template("login.html")


@login_manager.unauthorized_handler
def unauthorized():
    if request.blueprint == "api":
        abort(HTTPStatus.UNAUTHORIZED)
    return redirect(url_for("login_page"))


@app.route("/", methods=["GET"])
def index():
    """Root URL response"""
    return render_template("index.html")


@app.route("/location_adder", methods=["POST", "GET"])
@login_required
def location_adder():
    if (
        "name" in request.form
        and "description" in request.form
        and "address" in request.form
    ):
        coordinate = geo_code(request.form["address"])

        new_location = None
        if coordinate is not None:
            new_location = Location(
                name=request.form["name"],
                description=request.form["description"],
                address=request.form["address"],
                location=coordinate,
            )
        else:
            flash('Invalid address, try again','error')
            return redirect(url_for("add_location"))
        for i in users:
            if i == current_user:
                i.locations.append(new_location)
        flash(
            'Address added successfully',
            'success'
        )
        return redirect(url_for("home"))
    return redirect(url_for("add_location"))



@login_required
@app.route('/locations/<name>', methods = ['GET'])
def location(name):
    thing = Location()
    for i in current_user.locations:
        if i.name == name:
            thing = i
    if thing != None:
        return render_template('view_location.html', api_key = googlemaps_api_key, i = thing)
    return redirect(url_for('home'))



@app.route("/add_location", methods=["GET"])
@login_required
def add_location():
    """
    This endpoint is for adding a location
    """
    return render_template("add_location.html")


@app.route("/signup", methods=["GET"])
def signup():
    return render_template("signup.html")


# POST users/
@app.route("/users", methods=["POST"])
def newacc():
    """
    This endpoint is creating new User account.
    """
    if (
        "email" in request.form
        and "username" in request.form
        and "password" in request.form
        and "firstname" in request.form
        and "lastname" in request.form
    ):
        acc = User(
            un=request.form["username"],
            e=request.form["email"],
            p=generate_password_hash(request.form["password"]),
            fn=request.form["firstname"],
            ln=request.form["lastname"],
        )
        if validate_form(acc) != 'valid':
            flash(validate_form(acc), 'error')
            return redirect(url_for("signup"))
        users.append(acc)
        login_user(acc)

        return redirect(url_for("home"), code=200)

    abort(401)



@login_manager.user_loader
def user_loader(user_id):
    for i in users:
        if i.id == user_id:
            return i


@app.route("/login", methods=["POST"])
def login():
    if "username" in request.form and "password" in request.form:
        for i in users:
            if i.username == request.form["username"] and check_password_hash(
                i.password, request.form["password"]
            ):
                login_user(i)
                return redirect(url_for("home"), code=200)
    return redirect(url_for("login_page", status="unauthorized"), code=401)


@app.route("/home", methods=["GET"])
@login_required
def home():
    return render_template("home.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


def logger(session_id, delta):
    os.mkdir(f"Session_Logs/Server_Logs_Session_Id_{session_id}")
    with open(
        f"Session_Logs/Server_Logs_Session_Id_{session_id}/logs.txt", "w"
    ) as Session_Logs:
        Session_Logs.write(f"Session ID: {session_id}\n")
        Session_Logs.write(f"Time Took: {delta}\n")
        Session_Logs.close()
    with open(
        f"Session_Logs/Server_Logs_Session_Id_{session_id}/User-data.pkl", "wb"
    ) as Session_Logs:
        Session_Logs.write(pickle.dumps(users))
        Session_Logs.close()
    with open("Session_Logs/previous_session.txt", "w") as prev:
        prev.write(str(session_id))
        prev.close()

def load():
    session_id = 0
    with open("Session_Logs/previous_session.txt", "r") as prev:
        session_id = prev.read()
    with open(
        f"Session_Logs/Server_Logs_Session_Id_{session_id}/User-data.pkl", "rb"
    ) as Session_Logs:
        users = pickle.load(Session_Logs)
        Session_Logs.close()