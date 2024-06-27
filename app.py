from flask import Flask, render_template
import uuid

app = Flask(__name__)
app.config(uuid.uuid4().hex)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/index')
def index():
    return render_template('index.html')

