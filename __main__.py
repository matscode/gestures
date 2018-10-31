from gestures.app import *
from sys import exit

if __name__ == '__main__':
    app = Gestures()
    exit_status = app.run()
    exit(exit_status)
