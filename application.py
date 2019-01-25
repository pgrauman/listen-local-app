#!flask/bin/python

from listen_local_app import application
import config

if __name__ == '__main__':
    application.run(debug=config.debug)
