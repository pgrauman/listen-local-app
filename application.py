#!flask/bin/python

from listen_local_app import app
import config

app.run(debug=config.debug)
