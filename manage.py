from service.runtime import run, clear_cache
import sys

if __name__ == '__main__':
    if 'run' in sys.argv:
        print('Management console: Started Server')
        run()
    print('Management console: Idle')
    while True:
        command = input('Enter command: ')
        if command == 'run':
            print('Management console: Started Server')
            run()
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