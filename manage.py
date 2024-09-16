"""Used for reading args"""
import sys

import service

if __name__ == '__main__':
    if 'run' in sys.argv:
        print('Management console: Started Server')
        service.run()
    while True:
        command = input('Enter command: ')
        if command == 'run':
            print('Management console: Started Server')
            service.run()
        if command == 'exit':
            print('Abort: Ending session')
            break
        if command == 'help':
            print('Help')
            print('exit: Abort')
            print('run: Run server')