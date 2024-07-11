import os
import time
import random
import uuid

from pathlib import Path
from waitress import serve
from service.routes import app, load, logger

def beginServer():
    if not (os.path.exists(Path("Session_Logs/"))):
        os.mkdir("Session_Logs")
    file_path = Path("Session_Logs/previous_session.txt")
    i = input("Should server read save data (y/n)")
    if os.path.exists(file_path) and i == "y":
        print("Reading save data")
        load()
        print("Sucessfully read save data")
    start = time.time()
    session_seed = uuid.uuid4().hex
    random.seed(session_seed)
    session_id = random.randint(10000000000000000000, 99999999999999999999)
    i = input("Start application?(y/n)")
    if i == "y":
        print(f"Starting server, session id: {session_id}")
        serve(app, host="0.0.0.0", port=8080)
        end = time.time()
        delta = end - start
        print(
            "Completed running app.py on port 8080, 80, 443, took %.2f seconds" % delta
        )
        logger(session_id, delta)
    print("Server Session Ended")
