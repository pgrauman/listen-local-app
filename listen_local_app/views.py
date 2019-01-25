#!/usr/bin/python

'''
This file contains all the code to run the app pages
'''

import config
import json
import requests
# import spotipy

from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import session

from listen_local_app import app
from listen_local_app.forms import SearchForm
from listen_local_app.functions import build_df_and_get_spotify_info
from listen_local_app.functions import get_access_token
from listen_local_app.functions import get_concert_information
from listen_local_app.functions import make_spotify_play_button
from listen_local_app.functions import NoConcertsFound
from listen_local_app.functions import process_daterange


app.config.from_object('config')
client_id = config.spotify_client_id.decode("utf-8")


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    session.clear()
    form = SearchForm(request.form)
    if request.method == 'POST' and form.validate():
        session['zipcode'] = form.zipcode.data
        session['daterange'] = form.daterange.data
        session['distance'] = form.distance.data
        callback_url = request.url_root + 'callback'
        base_url = 'https://accounts.spotify.com/en/authorize?client_id=' + client_id + '&response_type=code&redirect_uri=' + callback_url + '&scope=user-read-email%20playlist-read-private%20user-follow-read%20user-library-read%20user-top-read%20playlist-modify-private%20playlist-modify-public&state=34fFs29kd09'  # noqa

        # this is how we set the Cookie when its a Redirect instead of return_response
        # https://stackoverflow.com/questions/12272418/in-flask-set-a-cookie-and-then-re-direct-user
        response = make_response(redirect(base_url, 302))
        return response
    print(form.errors)
    return render_template('index.html', form=form)


@app.route('/callback')
def process():
    # Get varaibles in more usable namespace
    if request.args.get('error'):
        return request.args.get('error')
    code = request.args.get('code')
    zipcode = session.get('zipcode')
    daterange = session.get('daterange')
    distance = session.get('distance')
    access_token = get_access_token(code)

    date1, date2 = process_daterange(daterange)

    # Get Concert information
    try:
        concert_data = get_concert_information(zipcode, date1=date1, date2=date2, dist=distance)
    except NoConcertsFound:
        msg = f"We didn't find any concerts near {zipcode} :-("
        return render_template("error.html", error_text=msg)

    df = build_df_and_get_spotify_info(concert_data)

    # Find out who the user is
    me_headers = {'Authorization': access_token}
    r_me = requests.get('https://api.spotify.com/v1/me', headers=me_headers)
    r_me_json = json.loads(r_me.text)
    user_id = r_me_json['id']

    # Make a Playlist
    playlist_name = f"Concerts near {zipcode} {daterange}"
    cp_headers = {'Authorization': access_token, 'Content-Type': 'application/json'}
    cp_post = {'name': playlist_name, 'public': 'true', 'collaborative': 'false',
               'description': 'created by protype app'}
    cp_url = 'https://api.spotify.com/v1/users/' + user_id + '/playlists'
    r_cp = requests.post(cp_url, headers=cp_headers, data=json.dumps(cp_post))
    playlist_id = json.loads(r_cp.text)['id']
    playlist_uri = json.loads(r_cp.text)['uri']

    # Post Tracks to the playlist
    tracks_headers = {'Authorization': access_token, 'Content-Type': 'application/json'}
    tracks = df.spotify_top_track_uri.dropna().tolist()
    tracks_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    tracks_post = {"uris": tracks}
    r_tracks = requests.post(tracks_url, headers=tracks_headers, data=json.dumps(tracks_post))  # noqa

    # Create listings table from df
    listing_fields = ["date_local", "time_local", "event_title", "performer",
                      "genre", "venue_name", "venue_address"]
    listings_df = df[listing_fields].sort_values(by=["date_local", "time_local"])
    listings_df.columns = ["Date", "Time", "Event", "Performer",
                           "Genre(s)", "Venue", "Address"]

    listings_html = listings_df.to_html(index=False, classes=["dataframe", "text-left"])
    return render_template("results.html",
                           playlist_html=make_spotify_play_button(playlist_uri),
                           listings=listings_html)
