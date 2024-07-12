from service.runtime import run

def start():
    catch = input("Server status: Idle (Press S + Enter to start or any other key to abort)")
    if catch == 'S' or catch == 's':
        run()

if __name__ == '__main__':
    print('Management console: Idle')
    while True:
        command = input('Enter command: ')
        if command == 'run':
            print('Management console: Started Server')
            start()
        if command == 'exit':
            print('Abort: Ending session')
            break
        if command == 'help':
            print('Help')
            print('exit: Abort')
            print('run: Run server')