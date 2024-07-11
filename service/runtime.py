from service.__init__ import beginServer
from service.health import check_health, close_server
def run():
    # Run server health checks here
    print('Checking server health...')
    if check_health() != None:
        print(f'Server health error:{check_health()}')
        return f'Health check failed{check_health()}'
    print('Server health: OK')
    # Begin the server here
    print('Starting server')
    beginServer()
    # Run server closing processes here
    close_server()
    print('Server closed')