from service.__init__ import beginServer
import shutil



def run():
    # Begin the server here
    print('Starting server')
    beginServer()



def clear_cache():
    dir_path = 'Session_Logs/'
    shutil.rmtree(dir_path)