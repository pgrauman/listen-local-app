from flask import Flask
from flask_wtf.csrf import CSRFProtect
import config


app = Flask(__name__)
csrf = CSRFProtect(app)

# from local_concert_playlist import callback, views
from listen_local_app import views  # noqa

app.secret_key = config.secret_key
