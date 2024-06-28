from flask import Flask, render_template
from waitress import serve
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = uuid.uuid4().hex

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8080)