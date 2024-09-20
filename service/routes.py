"""Modules and libraries"""

import uuid
import os
import time
import os.path
import re
from http import HTTPStatus
import mysql.connector

from flask import Flask, render_template, request, redirect, url_for, abort, flash
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    current_user,
    logout_user,
)
from service.classes import User, Location, LocationDetails
from service.utils import geo_code


load_dotenv()

geocoding_api_key = os.getenv("GEO_CODING_API")
googlemaps_api_key = os.getenv("GOOGLE_MAPS_API")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
db_host = os.getenv("DB_HOST")


app = Flask(__name__)

# Flask init
app.config["SECRET_KEY"] = os.urandom(24).hex()
app.config["MYSQL_HOST"] = os.getenv("DB_HOST", "db")
app.config["MYSQL_USER"] = os.getenv("DB_USER", "root")
app.config["MYSQL_ROOT_PASSWORD"] = os.getenv("DB_ROOT_PASSWORD")
app.config["MYSQL_DATABASE"] = os.getenv("DB_NAME")


print("Connecting to database.")
time.sleep(5)
mysql = mysql = mysql.connector.connect(
    host=app.config["MYSQL_HOST"],
    user=app.config["MYSQL_USER"],
    password=app.config["MYSQL_ROOT_PASSWORD"],
    database=app.config["MYSQL_DATABASE"],
    port=3306,
)


def test_connection():
    """Tests connection to database"""
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


test_connection()

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "/login_page"
login_manager.refresh_view = "/login_page"
login_manager.needs_refresh_message = (
    "To protect your account, please reauthenticate to access this page."
)
login_manager.needs_refresh_message_category = "info"


def validate_form(user: User):
    """Validates user

    Args:
        user (User): User type

    Returns:
       str: validation message
    """
    email_regex = ""
    with open("regex.txt", "r", encoding="utf8") as file:
        email_regex = file.readline()
        file.close()
    pattern = re.compile(email_regex)

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
    if not pattern.match(user.email):
        return "Invalid email"
    return "valid"


@app.route("/login_page", methods=["GET"])
def login_page():
    """The login page

    Returns:
        str: rendered template
    """
    if "status" in request.form:
        return render_template("login.html", e="Username or password incorrect")
    return render_template("login.html")


@login_manager.unauthorized_handler
def unauthorized():
    """Endpoint for unauthorized
    Returns:
        Response: redirects to login page, http code 302
        NoReturn: aborts with unauthorized status
    """
    if request.blueprint == "api":
        abort(HTTPStatus.UNAUTHORIZED)
    return redirect(url_for("login_page")), 302


@app.route("/", methods=["GET"])
def index():
    """Root URL response"""
    return render_template("index.html")


@app.route("/location_adder", methods=["POST", "GET"])
@login_required
# whenever they add 2 exact same locations
def location_adder():
    """Adds location to database

    Returns:
        Response: redirects to /home if location is valid
        Response: redirects to /add_location if location is not valid and flashes message
    """
    if (
        "name" in request.form
        and "description" in request.form
        and "address" in request.form
    ):
        location_details = geo_code(request.form["address"])
        cursor = mysql.cursor()
        new_location = None
        if location_details is not None:
            new_location = Location(
                name=request.form["name"],
                description=request.form["description"],
                address=location_details["formatted_address"],
                location=location_details["coordinate"],
            )
        else:
            flash("Invalid address, try again", "error")
            return redirect(url_for("add_location"))

        user_id = current_user.id

        # Check if location name already exsists in users location data
        query = "SELECT * FROM users_locations WHERE user_id = %s;"
        cursor.execute(query, (current_user.id,))
        all_locations = cursor.fetchall()
        for i in all_locations:
            query = "SELECT * FROM locations WHERE id = %s AND name = %s;"
            cursor.execute(
                query,
                (
                    i[2],
                    request.form["name"],
                ),
            )
            safety_check = cursor.fetchone()
            if safety_check is not None:
                flash("Location name is in use", category="error")
                return redirect("/add_location"), 302

        # Add changes to current_user
        current_user.locations.append(new_location)

        # Check if location already exsists
        query = "SELECT * FROM locations WHERE name = %s AND description = %s AND address = %s;"
        cursor.execute(
            query,
            (
                new_location.name,
                new_location.description,
                new_location.address,
            ),
        )
        data = cursor.fetchone()
        if data is not None:
            location_details_id = data[4]
            location_id = data[0]
            query = "SELECT * FROM location_details WHERE id = %s;"
            cursor.execute(query, (location_details_id,))
            data = cursor.fetchone()
            if data is not None:
                query = (
                    "INSERT INTO users_locations(user_id,location_id) VALUES (%s,%s);"
                )
                cursor.execute(
                    query,
                    (
                        current_user.id,
                        location_id,
                    ),
                )
                flash("Address added successfully", "success")
                return redirect(url_for("home"))
        # Insert into location_details
        cursor.reset()
        query = "INSERT INTO location_details(coordinate)\
        VALUES (ST_GeomFromText('POINT(%s %s)'));"
        cursor.execute(query, (new_location.location.lon, new_location.location.lat))

        # Fetch the location_details ID
        query = "SELECT id FROM location_details WHERE\
        coordinate = ST_GeomFromText('POINT(%s %s)');"
        cursor.execute(query, (new_location.location.lon, new_location.location.lat))
        location_details_id = cursor.fetchone()

        # Insert into locations
        query = "INSERT INTO locations(address, name, description\
        , location_details_id) VALUES (%s, %s, %s, %s);"
        cursor.execute(
            query,
            (
                new_location.address,
                new_location.name,
                new_location.description,
                location_details_id[0],
            ),
        )

        # Fetch the location ID
        query = "SELECT id FROM locations WHERE address = %s AND name = %s\
        AND description = %s AND location_details_id = %s;"
        cursor.execute(
            query,
            (
                new_location.address,
                new_location.name,
                new_location.description,
                location_details_id[0],
            ),
        )
        location_id = cursor.fetchone()

        # Insert into users_locations
        query = "INSERT INTO users_locations(user_id, location_id) VALUES (%s, %s);"
        cursor.execute(query, (user_id, location_id[0]))

        # Commit the change and close the cursor
        mysql.commit()
        cursor.close()

        flash("Address added successfully", "success")
        return redirect(url_for("home"))

    return redirect(url_for("add_location"))


@login_required
@app.route("/locations/<name>", methods=["GET"])
def location(name):
    """Displays location

    Args:
        name (str): The name of the location

    Returns:
        str: Displays location
    """
    location_object = None  # Location
    count = 0
    if current_user.is_authenticated:
        for i in current_user.locations:
            if i is None:
                continue
            if i.name == name:
                location_object = i
                break
            count += 1
        if location_object is not None:
            return render_template(
                "view_location.html", api_key=googlemaps_api_key, i=location_object
            )
        flash("Location not found", category="info")
        return redirect(url_for("home")), 302
    return redirect(url_for("login_page")), 302


@app.route("/add_location", methods=["GET"])
@login_required
def add_location():
    """
    This endpoint is for adding a location
    """
    return render_template("add_location.html", current_user=current_user)


@app.route("/signup", methods=["GET"])
def signup():
    """The signup page endpoint

    Returns:
        str: The signup page in html
    """
    return render_template("signup.html")


# POST users/
@app.route("/users", methods=["POST"])
def newacc():
    """Endpoint for creating a new user

    Returns:
        Response: Redirects to /home or /signup if error
    """
    cursor = mysql.cursor()
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
        if validate_form(acc) != "valid":
            flash(validate_form(acc), "error")
            return redirect(url_for("signup"))

        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (acc.username,))
        data = cursor.fetchone()
        if data is not None:
            flash(f"Username '{acc.username}' already exsists", "error")
            return redirect(url_for("signup"))

        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (acc.email,))
        data = cursor.fetchone()
        if data is not None:
            flash(f"Email '{acc.email}' already exsists", "error")
            return redirect(url_for("signup"))

        insert_query = "INSERT INTO users(firstname,lastname,username,PASSWORD,email)\
        VALUES(%s,%s,%s,%s,%s);"
        cursor.execute(
            insert_query,
            (
                acc.firstname,
                acc.lastname,
                acc.username,
                acc.password,
                acc.email,
            ),
        )
        mysql.commit()
        cursor.execute(
            "SELECT id FROM users WHERE username = %s\
                        AND email = %s;",
            (
                acc.username,
                acc.email,
            ),
        )
        data = cursor.fetchone()
        acc.id = data[0]
        cursor.close()
        login_user(acc)

        flash("User registered successfully", category="success")

        return redirect(url_for("home")), 302

    abort(401)


@login_manager.user_loader
def user_loader(user_id):
    """Returns user object

    Args:
        user_id (str): The id of the user

    Returns:
        User: The loaded user object
    """
    query = "SELECT * FROM users WHERE id = %s;"
    cursor = mysql.cursor()
    cursor.reset()
    cursor.execute(query, (user_id,))
    data = cursor.fetchone()

    user = User(un=data[3], e=data[5], p=data[4], fn=data[1], ln=data[2])

    cursor.execute(
        "SELECT id FROM users WHERE username = %s AND\
                    email = %s;",
        (
            user.username,
            user.email,
        ),
    )
    data = cursor.fetchone()
    user.id = data[0]
    cursor.reset()
    cursor.execute("SELECT * FROM users_locations WHERE user_id = %s", (data[0],))
    users_locations_reference = cursor.fetchall()
    for i in users_locations_reference:
        cursor.execute("SELECT * FROM locations WHERE id = %s", (i[2],))
        location_data = cursor.fetchone()
        cursor.execute(
            "SELECT ST_X(coordinate) AS lon, ST_Y(coordinate) AS lat\
                        FROM location_details WHERE id = %s",
            (location_data[4],),
        )
        location_details = cursor.fetchone()
        location_object = Location(
            name=location_data[2],
            description=location_data[3],
            address=location_data[1],
            location=LocationDetails(
                lon=location_details[0],
                lat=location_details[1],
            ),
        )
        user.locations.append(location_object)

    cursor.reset()
    cursor.close()

    return user


@app.route("/login", methods=["POST"])
def login():
    """Logs in user

    Returns:
        Response: Redirects user to /home or /login if user is incorrect
    """
    if "username" in request.form and "password" in request.form:
        cursor = mysql.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = %s;", (request.form["username"],)
        )
        data = cursor.fetchone()
        if data is None:
            flash("Username or password incorrect", category="error")
            return redirect(url_for("login_page")), 302
        if check_password_hash(data[4], request.form["password"]):
            user = User(un=data[3], e=data[5], p=data[4], fn=data[1], ln=data[2])
            user.id = str(data[0])
            login_user(user)
            return redirect(url_for("home"))
    flash("Username or password incorrect", category="error")
    return redirect(url_for("login_page")), 302


@app.route("/home", methods=["GET"])
@login_required
def home():
    """The home endpoint

    Returns:
        str: The rendered html template
    """
    return render_template("home.html", current_user=current_user)


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """The logout endpoint

    Returns:
        Response: Redirects client to / with 302 endpoint
    """
    logout_user()
    return redirect("/"), 302


@app.route("/delete_location/<name>")
@login_required
def delete_location(name):
    """Deletes location

    Args:
        name (str): The location name

    Returns:
        Response: Redirects client to /home
    """
    cursor = mysql.cursor()
    cursor.reset()
    query = "SELECT * FROM users_locations WHERE user_id = %s"
    cursor.execute(query, (current_user.id,))
    data = cursor.fetchall()
    for i in data:
        # DELETE instance of location
        query = "SELECT * FROM locations WHERE id = %s AND name = %s;"
        cursor.execute(
            query,
            (
                i[2],
                name,
            ),
        )
        location_data = cursor.fetchone()
        if location_data is None:
            continue
        cursor.reset()
        query = "DELETE FROM users_locations WHERE user_id = %s AND location_id = %s;"
        cursor.execute(
            query,
            (
                current_user.id,
                location_data[0],
            ),
        )
        cursor.reset()
    # Commit and close cursor
    mysql.commit()
    cursor.close()
    # Return redirect response
    flash("Location deleted", category="info")
    return redirect("/home"), 302
