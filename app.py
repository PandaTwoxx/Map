import time
import uuid
import os
import random
import pickle
import os.path

from flask import Flask, render_template, request, redirect, make_response, jsonify
from waitress import serve
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from pathlib import Path



load_dotenv()

api_key = os.getenv("SECRET_KEY")
class Location:

    def __init__(self) -> None:
        self.name = ""
        self.location = ""

class User:
    
    def __init__(self,un,e,p,fn,ln, location: Location = None) -> None:
        self.username = un
        self.email = e
        self.password = p
        self.firstname = fn
        self.lastname = ln
        self.locations = [location]


yan = User("yan", "yk2602@nyu.edu", "password", "Yan", "Konichshev", Location("NYU", "New York"))
print(yan.locations[0].name)
print(yan.locations[0].location)

users = [User]
identifiers = {str,User}

app = Flask(__name__)
app.config['SECRET_KEY'] = uuid.uuid4().hex



def keygen(hash = uuid.uuid4().hex):
    """
    Generates a key for the User to use
    """
    return generate_password_hash(hash)


# TODO: think about the naming convention
@app.route('/login_page')
def login_page():
    if 'e' in request.form:
        return render_template('login.html', e = 'Username or password incorrect')
    return render_template('login.html')



@app.route('/')
def index():
    """Root URL response"""
    return render_template('index.html')



@app.route('/signup')
def signup():
    if 'e' in request.form:
        return render_template('signup.html', e = 'Email already in use')
    if 'f' in request.form:
        return render_template('signup.html', e = 'Username already in use')
    return render_template('signup.html')


# POST users/
@app.route('/users', methods = ['POST'])
def newacc():
    """
    This endpoint is creating new User account.
    """
    if 'email' in request.form and 'username' in request.form and 'password' in request.form and 'firstname' in request.form and 'lastname' in request.form:
        for i in users:
            
            if i.email == request.form['email']:
                return redirect("/signup", code=302)
            
            if i.username == request.form['username']:
                # TODO: do some research on how do we notify the user of the particular issue?
                return redirect("/signup", code=302)
        
        # TODO: need to validate data (hint: Regex)
        acc = User(
            un = request.form['username'], 
            e = request.form['email'],
            p = request.form['password'], 
            fn = request.form['firstname'], 
            ln = request.form['lastname']
        )

        users.append(acc)
        # TODO: figure out what is it doing?
        resp = make_response('loading')
        otp = keygen()
        resp.set_cookie('key',otp)
        identifiers.update({otp,acc})

        # TODO: think what should be returned
        return '<body onload=location.replace("/home")></body>'
    
    # TODO: think what should be returned
    return '<body onload=location.replace("/signup")></body>'


@app.route('/login', methods = ['POST'])
def login():
    # TODO: how to make this look better?
    if 'email' in request.form and 'password' in request.form:
        for i in users:
            if i.username == request.form['email'] and i.password == request.form['password']:
                resp = make_response('loading')
                otp = keygen()
                resp.set_cookie('key',otp)
                identifiers.update({otp,i})
                # TODO: think about what we should be returning here
                return '<body onload=location.replace("/home")></body>'
    return '<body onload=location.replace("/login?e=e")></body>'



@app.route('/home')
def home():
    key = request.cookies.get('key')
    if key in identifiers:
        acc = identifiers[key]
        return render_template('home.html', username = acc.username)
    return '<body onload=location.replace("/login?e=e")></body>'
    


def logger(session_id):
    os.mkdir(f'Session_Logs/Server_Logs_Session_Id_{session_id}')
    with open(f'Session_Logs/Server_Logs_Session_Id_{session_id}/logs.txt', 'w') as Session_Logs:
        Session_Logs.write(f'Session ID: {session_id}\n')
        Session_Logs.write(f'Time Took: {delta}\n')
        Session_Logs.close()
    with open(f'Session_Logs/Server_Logs_Session_Id_{session_id}/User-data.pkl', 'wb') as Session_Logs:
        Session_Logs.write(pickle.dumps(users))
        Session_Logs.close()
    with open(f'Session_Logs/Server_Logs_Session_Id_{session_id}/otp-data.pkl', 'wb') as Session_Logs:
        Session_Logs.write(pickle.dumps(identifiers))
        Session_Logs.close()
    with open('Session_Logs/previous_session.txt', 'w') as prev:
        prev.write(str(session_id))
        prev.close()



if __name__ == '__main__':
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
        with open(f'Session_Logs/Server_Logs_Session_Id_{session_id}/otp-data.pkl', 'rb') as Session_Logs:
            identifiers = pickle.load(Session_Logs)
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