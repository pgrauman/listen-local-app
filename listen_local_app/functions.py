#!/usr/bin/python

'''
This file holds the functions necessary to process the data behind the scenes
'''


import config
import json
import pandas as pd
import requests
import spotipy

from flask import Flask
from flask import request
from numpy import nan
from spotipy.oauth2 import SpotifyClientCredentials


app = Flask(__name__)
app.config.from_object('config')

client_id = config.seatgeek_client_id


def process_daterange(daterange):
    '''
    Process daterange from datepicker input.

    Args:
        daterange (str): string with daterange formatted as
            'YYYY-MM-DD to YYYY-MM-DD'
    '''
    daterange = daterange.strip()
    if "to" in daterange:
        date1, date2 = daterange.split(" to ")
    else:
        date1, date2 = (daterange, None)
    return date1, date2


def submit_api_request(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise FailedApiRequestError


def get_local_concerts(zipcode, date1, date2, dist=3, per_page=100):
    '''
    Build Datafrae of concerts and related songs in a range of a given zipcode

    Args:
        zipcode (str): zipcode to search near
        date1 (str): min date of search
        date2 (str): max date of search
        dist (str): distance (mi) around zipcode for search (default 3)
        per_page (int): maximum number of results (default: 100)
    '''

    # Use spotipy for its great support for large volume of requests
    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Get dates in formate seatgeek likes
    if not date2:
        date2 = date1
    datetime1 = f'{date1}T00:00:00'
    datetime2 = f'{date2}T23:00:00'

    # seatgeek API request
    params = {"geoip": zipcode, "type": "concert",
              "per_page": per_page, "range": f"{dist}mi",
              "datetime_local.gte": datetime1, "datetime_local.lte": datetime2}
    base = f"https://api.seatgeek.com/2/events?client_id={client_id}"
    param_str = "&".join([f"{i}={v}" for i, v in params.items()])
    data = submit_api_request(base + "&" + param_str)

    # If there are no concerts raise exception
    if len(data['events']) < 1:
        raise NoConcertsFound

    # Pull select data fields and put into pandas dataframe
    df_dict = {}
    for event in data['events']:
        for performer in event['performers']:
            d = {}
            d['performer'] = performer['short_name']
            try:
                d['genre'] = ",".join(x['name'] for x in performer['genres'])
            except KeyError:
                d['genre'] = "NA"
            d['datetime_local'] = event['datetime_local']
            date, time = event['datetime_local'].split("T")
            d['date_local'] = date
            d['time_local'] = time
            d['event_id'] = event['id']
            d['event_title'] = event['title']
            d['venue_name'] = event['venue']['name']
            d['venue_id'] = event['venue']['id']
            d['venue_address'] = f"{event['venue']['address']}, {event['venue']['extended_address']}"  # noqa

            # # Spotify searching
            spotify_artist_id, spotify_top_track_id = lookup_spotify_artist_track(sp, d['performer'])  # noqa
            d['spotify_artist_id'] = spotify_artist_id
            d['spotify_top_track_id'] = spotify_top_track_id

            # Performer information to dictionary
            df_dict[performer['id']] = d

    df = pd.DataFrame(df_dict).T
    df['spotify_top_track_uri'] = df.spotify_top_track_id.dropna().apply(lambda x: f"spotify:track:{x}")  # noqa
    return df


def lookup_spotify_artist_track(sp, performer_name):
    '''
    Look up the artist id and the top song by said artist for a given performer

    Args:
        sp (spotipy.Spotify): actively credentialed ``spotipy.Spotify`` object
        performer_name (str): name of performer to look up info on
    '''
    artist_sp_results = sp.search(q='artist:' + performer_name, type='artist')
    # NEED TO MATCH EXACT MATCH THEN TOP RESULT
    if len(artist_sp_results['artists']['items']) == 0:
        return nan, nan
    spotify_artist_id = artist_sp_results['artists']['items'][0]['id']
    top_track_results = sp.artist_top_tracks(artist_id=spotify_artist_id)
    if len(top_track_results['tracks']) == 0:
        return spotify_artist_id, nan
    spotify_top_track_id = top_track_results['tracks'][0]['id']
    return spotify_artist_id, spotify_top_track_id


def get_access_token(code):
    '''
    Get access token from spotify (second handshake)
    Code taken from `https://github.com/siquick/mostplayed<https://github.com/siquick/mostplayed/blob/master/mp/functions.py#L113-L133>`_  # noqa

    Args:
        code (str): code recieved from first spotify handshake
    '''
    print('Getting the access token')
    post_url = 'https://accounts.spotify.com/api/token'
    grant_type = 'authorization_code'
    callback_url = request.url_root + 'callback'
    authorization = config.spotify_authorization

    post = {'redirect_uri': callback_url, 'code': code, 'grant_type': grant_type}
    headers = {'Authorization': authorization, 'Accept': 'application/json',
               'Content-Type': 'application/x-www-form-urlencoded'}

    r = requests.post(post_url, headers=headers, data=post)
    auth_json = json.loads(r.text)
    try:
        access_token = 'Bearer ' + auth_json['access_token']
        # print(access_token)
        return access_token
    except Exception:
        print("Something went wrong at the Spotify end")
        return "Something went wrong at the Spotify end"


def make_spotify_play_button(uri, height=380, width=300):
    '''
    Make Spotify play button from the uri

    Args:
        uri (str): spotify uri for playlist/trak/artist
        height (int): height for play button in px (default=380)
        width (int): width for play button in px (default=300)
    '''
    uri2url = "/".join(uri.split(":")[1:])
    return (f'<iframe src="https://open.spotify.com/embed/{uri2url}"'
            f' width="{width}" height="{height}" frameborder="0"'
            ' allowtransparency="true" allow="encrypted-media"></iframe>')


# Exceptions defined Here
class NoConcertsFound(Exception):
    """Raised when no seat geek results are found"""
    pass


class FailedApiRequestError(Exception):
    """Raised when api request is unscuccessful"""
    pass
