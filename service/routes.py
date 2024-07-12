import uuid
import os
import pickle
import os.path
import re

from service.classes import User, Location
from flask import Flask, render_template, request, redirect, url_for, abort
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


users = [User]

app = Flask(__name__)
app.config["SECRET_KEY"] = uuid.uuid4().hex

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
        return "Invalid password(Must be 5 characters)"
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


# TODO: think about the naming convention
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
        and "location" in request.form
    ):
        coordinate = geo_code(request.form["location"])
        new_location = None
        if coordinate is not None:
            new_location = Location(
                name=request.form["name"],
                description=request.form["description"],
                location=coordinate,
            )
        else:
            return redirect(url_for("add_location"))
        for i in users:
            if i == current_user:
                i.locations.append(new_location)
        return
    return redirect(url_for("add_location"))


@app.route("/add_location", methods=["GET"])
@login_required
def add_location():
    """
    This endpoint is for adding a location
    """
    return render_template("add_location.html")


@app.route("/signup", methods=["GET"])
def signup():
    if request.args.get("status") != None:
        return render_template("signup.html", e = request.args.get("status"))
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
        # TODO: need to validate data (hint: Regex)
        acc = User(
            un=request.form["username"],
            e=request.form["email"],
            p=generate_password_hash(request.form["password"]),
            fn=request.form["firstname"],
            ln=request.form["lastname"],
        )
        if validate_form(acc) != 'valid':
            return redirect(url_for(f"signup?status={validate_form(acc)}"), code=401)
        users.append(acc)
        login_user(acc)

        # TODO: think what should be returned
        return redirect(url_for("home"), code=200)

    # TODO: think what should be returned
    return redirect(url_for("signup"), code=401)


@app.route('/logout', methods = ['GET'])
@login_required
def logout():
    logout_user()
    return redirect('/')


@login_manager.user_loader
def user_loader(user_id):
    for i in users:
        if i.id == user_id:
            return i


@app.route("/login", methods=["POST"])
def login():
    # TODO: how to make this look better?
    if "username" in request.form and "password" in request.form:
        for i in users:
            if i.username == request.form["username"] and check_password_hash(
                i.password, request.form["password"]
            ):
                login_user(i)
                # TODO: think about what we should be returning here
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