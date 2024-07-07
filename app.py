import time
import uuid
import os
import random
import pickle
import os.path
import re

from flask import Flask, render_template, request, redirect, url_for, abort
from waitress import serve
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from pathlib import Path
from flask_login import LoginManager, login_user, login_required, current_user, logout_user, UserMixin
from http import HTTPStatus


load_dotenv()

api_key = os.getenv("SECRET_KEY")
class Location:
    name = ''
    location = ''
    description = ''
    def __init__(self, name, location, description) -> None:
        self.name = name
        self.location = location
        self.description = description

class User(UserMixin):
    id = ''
    email = ''
    username = ''
    password = ''
    firstname = ''
    lastname = ''
    locations = [Location]
    def __init__(self,un,e,p,fn,ln, location: Location = None) -> None:
        self.username = un
        self.email = e
        self.password = p
        self.firstname = fn
        self.lastname = ln
        self.locations = [location]
        self.id = uuid.uuid4().hex
    def get_id(self):
        return self.id

users = [User]

app = Flask(__name__)
app.config['SECRET_KEY'] = uuid.uuid4().hex

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "/login_page"
login_manager.refresh_view = "/login_page"
login_manager.needs_refresh_message = (
    u"To protect your account, please reauthenticate to access this page."
)
login_manager.needs_refresh_message_category = "info"

def validate_form(user: User):
    email_regex = ''
    with open('regex.txt', 'r') as file:
        email_regex = file.readline()
        file.close()
    pattern = re.compile(email_regex)
    for i in users:         
        if i.email == user.email:
            return 'bademail'
        if i.username == user.username:
            return 'badusername'
    if len(user.password) < 8:
        return 'invalidpass'
    if len(user.username) < 1:
        return 'invalidusername'
    if len(user.email) < 1:
        return 'invalidemail'
    if len(user.firstname) < 1:
        return 'badfname'
    if len(user.lastname) < 1:
        return 'invalidlnames'
    if not(pattern.match(user.email)):
        return 'invalidemail'
    return 'valid'

def keygen(hash = uuid.uuid4().hex):
    """
    Generates a key for the User to use
    """
    return generate_password_hash(hash)


# TODO: think about the naming convention
@app.route('/login_page', methods = ['GET'])
def login_page():
    if 'status' in request.form:
        return render_template('login.html', e = 'Username or password incorrect')
    return render_template('login.html')

@login_manager.unauthorized_handler
def unauthorized():
    if request.blueprint == 'api':
        abort(HTTPStatus.UNAUTHORIZED)
    return redirect(url_for('login_page'))

@app.route('/', methods = ['GET'])
def index():
    """Root URL response"""
    return render_template('index.html')

@app.route('/location_adder', methods = ['PUT'])
@login_required
def location_adder():
    if 'name' in request.form:
        new_location = Location(
            name = request.form['name'],
            description = request.form['description'],
            location = request.form['location'],
        )
        for i in users:
            if i == current_user:
                i.locations.append(new_location)
    return redirect('/add_location')


@app.route('/add_location', methods = ['GET'])
@login_required
def add_location():
    """
    This endpoint is for adding a location
    """
    return render_template('add_location.html')



@app.route('/signup', methods = ['GET'])
def signup():
    if 'status' in request.form:
        pass
    return render_template('signup.html')


# POST users/
@app.route('/users', methods = ['POST'])
def newacc():
    """
    This endpoint is creating new User account.
    """
    if 'email' in request.form and 'username' in request.form and 'password' in request.form and 'firstname' in request.form and 'lastname' in request.form:
        # TODO: need to validate data (hint: Regex)
        acc = User(
            un = request.form['username'], 
            e = request.form['email'],
            p = generate_password_hash(request.form['password']), 
            fn = request.form['firstname'], 
            ln = request.form['lastname']
        )

        #if validate_form(acc) != 'valid':
            #return redirect(location = f'/signup?status={validate_form(acc)}', code = 401)
        users.append(acc)
        login_user(acc)

        # TODO: think what should be returned
        return redirect('/home', code = 200)
    
    # TODO: think what should be returned
    return redirect('/signup', code = 401)

@login_manager.user_loader
def user_loader(user_id):
    for i in users:
        if i.id == user_id:
            return i

@app.route('/login', methods = ['POST'])
def login():
    # TODO: how to make this look better?
    if 'username' in request.form and 'password' in request.form:
        for i in users:
            if i.username == request.form['username'] and check_password_hash(i.password, request.form['password']):
                login_user(i)
                # TODO: think about what we should be returning here
                return redirect('/home', code = 200)
    return redirect('/login_page?status=unauthorized', code = 401)



@app.route('/home', methods = ['GET'])
@login_required
def home():
    return render_template('home.html')
    

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


def logger(session_id):
    os.mkdir(f'Session_Logs/Server_Logs_Session_Id_{session_id}')
    with open(f'Session_Logs/Server_Logs_Session_Id_{session_id}/logs.txt', 'w') as Session_Logs:
        Session_Logs.write(f'Session ID: {session_id}\n')
        Session_Logs.write(f'Time Took: {delta}\n')
        Session_Logs.close()
    with open(f'Session_Logs/Server_Logs_Session_Id_{session_id}/User-data.pkl', 'wb') as Session_Logs:
        Session_Logs.write(pickle.dumps(users))
        Session_Logs.close()
    with open('Session_Logs/previous_session.txt', 'w') as prev:
        prev.write(str(session_id))
        prev.close()



if __name__ == '__main__':
    if not(os.path.exists(Path('Session_Logs/'))):
        os.mkdir('Session_Logs')
    file_path = Path('Session_Logs/previous_session.txt')
    i = input("Should server read save data (y/n)")
    if os.path.exists(file_path) and i == "y":
        print('Reading save data')
        session_id = 0
        with open('Session_Logs/previous_session.txt', 'r') as prev:
            session_id = prev.read()
        with open(f'Session_Logs/Server_Logs_Session_Id_{session_id}/User-data.pkl', 'rb') as Session_Logs:
            users = pickle.load(Session_Logs)
            Session_Logs.close()
        print('Sucessfully read save data')
    start = time.time()
    session_seed = uuid.uuid4().hex
    random.seed(session_seed)
    session_id = random.randint(10000000000000000000,99999999999999999999)
    i = input('Start server?(y/n)')
    if i == 'y':
        print(f"Starting server, session id: {session_id}")
        serve(app,host = "0.0.0.0", port = 8080)
        end = time.time()
        delta = end-start
        print('Completed running app.py on port 8080, 80, 443, took %.2f seconds' % delta)
        logger(session_id)
    print('Server Session Ended')