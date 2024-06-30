from flask import Flask, render_template, request, redirect, make_response
from waitress import serve
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import uuid
import os
import random
import pickle
import os.path
from pathlib import Path
import time


load_dotenv()

api_key = os.getenv("SECRET_KEY")

class user:
    username = ''
    firstname = ''
    lastname = ''
    email = ''
    password = ''

    def __init__(self,un,e,p,fn,ln):
        username = un
        email = e
        password = p
        firstname = fn
        lastname = ln

users = [user]
identifiers = {str,user}

app = Flask(__name__)
app.config['SECRET_KEY'] = uuid.uuid4().hex

def keygen(hash = uuid.uuid4().hex):
    return generate_password_hash(hash)

@app.route('/login')
def login():
    if 'e' in request.form:
        return render_template('login.html', e = 'Username or password incorrect')
    return render_template('login.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    if 'e' in request.form:
        return render_template('signup.html', e = 'Email already in use')
    if 'f' in request.form:
        return render_template('signup.html', e = 'Username already in use')
    return render_template('signup.html')

@app.route('/newacc', methods = ['POST'])
def newacc():
    if 'email' in request.form and 'username' in request.form and 'password' in request.form and 'firstname' in request.form and 'lastname' in request.form:
        for i in users:
            if i.email == request.form['email']:
                return '<body onload=location.replace("/signup?e=e")></body>'
            if i.username == request.form['username']:
                return '<body onload=location.replace("/signup?f=f")></body>'
        acc = user(un = request.form['username'], e = request.form['email'], p = request.form['password'], fn = request.form['firstname'], ln = request.form['lastname'])
        users.append(acc)
        resp = make_response('loading')
        otp = keygen()
        resp.set_cookie('key',otp)
        identifiers.update({otp,acc})
        return '<body onload=location.replace("/home")></body>'
    return '<body onload=location.replace("/signup")></body>'
@app.route('/sso', methods = ['POST'])
def sso():
    if 'email' in request.form and 'password' in request.form:
        for i in users:
            if i.username == request.form['email'] and i.password == request.form['password']:
                resp = make_response('loading')
                otp = keygen()
                resp.set_cookie('key',otp)
                identifiers.update({otp,i})
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
    with open(f'Session_Logs/Server_Logs_Session_Id_{session_id}/user-data.pkl', 'wb') as Session_Logs:
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
        with open(f'Session_Logs/Server_Logs_Session_Id_{session_id}/user-data.pkl', 'rb') as Session_Logs:
            users = pickle.load(Session_Logs)
            Session_Logs.close()
        with open(f'Session_Logs/Server_Logs_Session_Id_{session_id}/otp-data.pkl', 'rb') as Session_Logs:
            identifiers = pickle.load(Session_Logs)
            Session_Logs.close()
        print('Sucessfully read save data')
    start = time.time()
    session_seed = uuid.uuid4().hex
    random.seed(session_seed)
    session_id = random.randint(0,999999999999999999)
    from waitress import serve
    i = input('Start server?(y/n)')
    if i == 'y':
        print(f"Starting server, session id: {session_id}")
        serve(app,host = "0.0.0.0", port = 8080)
        end = time.time()
        delta = end-start
        print('Completed running app.py on port 8080, 80, 443, took %.2f seconds' % delta)
        logger(session_id)
    print('Server Session Ended')