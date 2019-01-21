import base64

# FILL IN THE BLANKS IN THIS FILE AND SAVE AS config.py

# Get Spotify API credenitals by registering an app
# https://developer.spotify.com
spotify_client_id = b''
spotify_client_secret = b''
spotify_authorization = 'Basic ' + base64.b64encode(spotify_client_id + b':' + spotify_client_secret).decode("utf-8")

# Get a Seatgeek API key
# https://seatgeek.com/account/develop
seatgeek_client_id = ''

# Generate your own key here
secret_key = b''

debug = False # or true if dev mode