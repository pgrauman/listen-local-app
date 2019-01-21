from flask import Flask
import config

app = Flask(__name__)
# from local_concert_playlist import callback, views
from listen_local_app import views

app.secret_key = config.secret_key
