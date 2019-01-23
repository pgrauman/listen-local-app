#!/usr/bin/python

from flask import Flask as _Flask


class Flask(_Flask):
    testing = True
    secret_key = __name__

    def make_response(self, rv):
        if rv is None:
            rv = ''

        return super(Flask, self).make_response(rv)


# Initialize mock app
def _get_app_client():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    client = app.test_client()
    return app, client
