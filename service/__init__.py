"""A simple flask project that runs on port 8080"""
import os
import time
import threading
import sys
import uuid

from waitress import serve
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from service.routes import app, login_manager

load_dotenv()

def config():
    """App configuration
    """

    # DB parameters
    user = os.getenv('user')
    password = os.getenv('password')
    host = os.getenv('host')
    port = os.getenv('port')
    database = os.getenv('database')

    # App Configurations
    app.config["SECRET_KEY"] = os.urandom(24).hex()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://\
        {user}:{password}@{host}:{port}/{database}'

    # Init Login Manager
    print('Initilizing login_manager')
    login_manager.init_app(app)

    login_manager.login_view = "/login_page"
    login_manager.refresh_view = "/login_page"
    login_manager.needs_refresh_message = (
        "To protect your account, please reauthenticate to access this page."
    )
    login_manager.needs_refresh_message_category = "info"
    print('Initilization Complete!')

##############################################################################
print('Initilizing')                                                        ##
config()                                                                    ##
# Init db instance                                                          ##
print('Waiting for db to attach')                                           ##
db = SQLAlchemy(app)                                                        ##
with app.app_context():                                                     ##
    print('Creating DB tables')                                             ##
    db.create_all()                                                         ##
##############################################################################
def run_thread():
    """Starts thread
    """
    time.sleep(1)
    print(f"ID of sub-thread: {os.getpid()}")
    print(f"Sub thread name: {threading.current_thread().name}")
    serve(app, host='0.0.0.0', port=8080, _quiet=True)

def begin_server():
    """Runs server initilization
    """
    print(f"ID of main thread: {os.getpid()}")
    print(f"Main thread name: {threading.current_thread().name}")

    start = time.time()
    print('Creating new task')
    print('Waiting for task to attach')
    t1 = threading.Thread(target=run_thread, name=str(uuid.uuid4()), daemon=True)
    t1.start()

    print("Task running")
    while True:
        if input("Enter \"Stop\" to terminate: ").lower() == "stop":
            break

    print("Stopping server...")
    # No need to join since the thread is a daemon
    print("Task ended")

    end = time.time()
    delta = end - start

    print(f"Thread stopped. Ran for {delta} seconds")
    print("Server Session Ended")
    print('Killing task')
    sys.exit()


def run():
    """Begins the Flask application
    """


    # Begin the server here
    print('Starting application')
    begin_server()
