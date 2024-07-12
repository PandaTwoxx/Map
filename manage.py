from service.runtime import run, clear_cache
import sys
sys.argv
def start():
    catch = input("Server status: Idle (Press S + Enter to start or any other key to abort)")
    if catch == 'S' or catch == 's':
        run()

if __name__ == '__main__':
    if 'run' in sys.argv:
        print('Management console: Started Server')
        start()
    print('Management console: Idle')
    while True:
        command = input('Enter command: ')
        if command == 'run':
            print('Management console: Started Server')
            start()
        if command == 'exit':
            print('Abort: Ending session')
            break
        if command == 'clear-cache':
            print('Management console: Clearing save data')
            clear_cache()
        if command == 'help':
            print('Help')
            print('exit: Abort')
            print('run: Run server')
            print('clear-cahce: Clears all data in Session_Logs/')