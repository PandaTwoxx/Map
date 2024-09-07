import uuid
import os
import os.path
import re
import mysql.connector

from service.classes import User, Location
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
from http import HTTPStatus
from service.utils import geo_code


load_dotenv()

geocoding_api_key = os.getenv("GEO_CODING_API")
googlemaps_api_key = os.getenv("GOOGLE_MAPS_API")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
db_host = os.getenv("DB_HOST")


app = Flask(__name__)

# Flask init
app.config["SECRET_KEY"] = uuid.uuid4().hex
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = db_host
app.config["MYSQL_ROOT_PASSWORD"] = db_password
app.config["MYSQL_DATABASE"] = db_name

print("Connecting to database.")

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
        location_details = geo_code(request.form["address"])
        cursor = mysql.cursor()
        new_location = None
        if location_details is not None:
            new_location = Location(
                name=request.form["name"],
                description=request.form["description"],
                address=location_details['formatted_address'],
                location=location_details['coordinate'],
            )
        else:
            flash('Invalid address, try again','error')
            return redirect(url_for("add_location"))
        user_id = current_user.id
        # TODO: Avoid duplicates
        # Populate location_details
        query = 'INSERT INTO location_details(coordinate) VALUES (ST_GeomFromText(\'POINT(%s %s)\'));'
        cursor.execute(query, (new_location.location.lon, new_location.location.lat, ))

        query = 'SELECT id FROM location_details WHERE coordinate = ST_GeomFromText(\'POINT(%s %s)\');'
        cursor.execute(query, (new_location.location.lon, new_location.location.lat, ))
        location_details_id = cursor.fetchone()
        # Populate locations
        query = 'INSERT INTO locations(address,name,description,location_details_id) VALUES (%s,%s,%s,%s);'
        cursor.execute(query,(new_location.address, new_location.name, new_location.description, location_details_id[0], ))
        query = 'SELECT id FROM locations WHERE address = %s AND name = %s AND description = %s AND location_details_id = %s;'
        cursor.execute(query,(new_location.address, new_location.name, new_location.description, location_details_id[0], ))
        location_id = cursor.fetchone()
        # Populate user_locations
        query = 'INSERT INTO users_locations(user_id,location_id) VALUES (%s,%s);'
        cursor.execute(query,(user_id, location_id[0], ))

        # Commit and close cursor
        mysql.commit()
        cursor.close()

        flash(
            'Address added successfully',
            'success'
        )
        return redirect(url_for("home"))
    return redirect(url_for("add_location"))



@login_required
@app.route('/locations/<name>', methods = ['GET'])
def location(name):
    location_object = None # Location
    if current_user.is_authenticated:
        for i in current_user.locations:
            if i is None:
                continue
            if i.name == name:
                location_object = i
                break
            count += 1
        if location_object is not None:
            return render_template('view_location.html', api_key = googlemaps_api_key, i = location_object)
        flash("Location not found", category="info")
        return redirect(url_for('home'))
    return redirect(url_for('login_page'))



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
    cursor = mysql.cursor()
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
        if validate_form(acc) != "valid":
            flash(validate_form(acc), 'error')
            return redirect(url_for("signup"))
        
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (acc.username, ))
        data = cursor.fetchone()
        if data is not None:
            flash("Username '{}' already exsists".format(acc.username), 'error')
            return redirect(url_for("signup"))
        
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (acc.email, ))
        data = cursor.fetchone()
        if data is not None:
            flash("Email '{}' already exsists".format(acc.email), 'error')
            return redirect(url_for("signup"))
        
        insert_query = "INSERT INTO users(firstname,lastname,username,PASSWORD,email) VALUES(%s,%s,%s,%s,%s);"
        cursor.execute(insert_query, (acc.firstname,acc.lastname,acc.username,acc.password,acc.email, ))
        mysql.commit()
        cursor.execute("SELECT id FROM users WHERE username = %s AND email = %s;", (acc.username, acc.email, ))
        data = cursor.fetchone()
        acc.id = data[0]
        cursor.close()
        login_user(acc)

        flash('User registered successfully', category="success")

        return redirect(url_for("home"), code=200)

    abort(401)



@login_manager.user_loader
def user_loader(user_id):
    query = "SELECT * FROM users WHERE id = %s;"
    cursor = mysql.cursor()
    cursor.execute(query, (user_id, ))
    data = cursor.fetchone()

    user = User(
                    un = data[3],
                    e = data[5],
                    p = data[4],
                    fn = data[1],
                    ln = data[2]
                )
    

    cursor.execute('SELECT id FROM users WHERE username = %s AND email = %s;', (user.username,user.email, ))
    data = cursor.fetchone()
    user.id = data[0]
    cursor.close()

    return user


@app.route("/login", methods=["POST"])
def login():
    if "username" in request.form and "password" in request.form:
        cursor = mysql.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s;", (request.form['username'], ))
        data = cursor.fetchone()
        if data is None:
            flash('Username or password incorrect', category='error')
            return redirect(url_for("login_page"), code=401)
        if check_password_hash(data[4],request.form['password']):
            user = User(
                    un = data[3],
                    e = data[5],
                    p = data[4],
                    fn = data[1],
                    ln = data[2]
                )
            user.id = str(data[0])
            login_user(user)
            return redirect(url_for("home"), code=200)
    flash('Username or password incorrect', category='error')
    return redirect(url_for("login_page"), code=401)


@app.route("/home", methods=["GET"])
@login_required
def home():
    return render_template("home.html")

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect('/')