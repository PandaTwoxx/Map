"""A simple flask project that runs on port 8080"""
from service.runtime import begin_server


def run():
    """Begins the Flask application
    """
    # Begin the server here
    print('Starting server')
    begin_server()
