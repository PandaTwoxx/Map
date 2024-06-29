from flask import Flask, render_template, request, redirect, make_response
from waitress import serve
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import uuid
import os

load_dotenv()

api_key = os.getenv("SECRET_KEY")

class user:
    username = ''
    firstname = ''
    lastname = ''
    email = ''
    password = ''

    def __init__(un,e,p,fn,ln):
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
        for i in user:
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
    return '<body onload=location.replace("/login")></body>'
@app.route('/home')
def home():
    key = request.cookies.get('key')
    if key in identifiers:
        acc = identifiers[key]
        return render_template('home.html', username = acc.username)
    redirect('/login')
    

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8080)