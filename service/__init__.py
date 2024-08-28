import time
import os
import threading
import sys
import uuid

from waitress import serve
from service.routes import app

def run_thread():
    print("ID of sub-thread: {}".format(os.getpid()))
    print("Sub thread name: {}".format(threading.current_thread().name))
    serve(app, host='0.0.0.0', port=8080, _quiet=True)

def beginServer():
    print("ID of main thread: {}".format(os.getpid()))
    print("Main thread name: {}".format(threading.current_thread().name))

    start = time.time()
    print('Creating new task')

    t1 = threading.Thread(target=run_thread, name=str(uuid.uuid4()), daemon=True)
    t1.start()

    print("Task running")
    while True:
        if input("Enter \"Stop\" to terminate: ") == "Stop":
            break

    print("Stopping server...")
    # No need to join since the thread is a daemon
    print("Task ended")

    end = time.time()
    delta = end - start

    print("Thread stopped. Ran for %.2f seconds" % delta)
    print("Server Session Ended")
    sys.exit()

if __name__ == "__main__":
    beginServer()
