from gestures.app import *

if __name__ == '__main__':
    app = Gestures()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)
