#!/usr/bin/python

'''
This file holds the functions necessary to process the data behind the scenes
'''


import config
import json
import pandas as pd
import requests
import spotipy

from datetime import datetime
from flask import Flask
from flask import request
from numpy import nan
from spotipy.oauth2 import SpotifyClientCredentials


app = Flask(__name__)
app.config.from_object('config')

spotify_client_id = config.spotify_client_id.decode('utf-8')
spotify_client_secret = config.spotify_client_secret.decode('utf-8')
seatgeek_client_id = config.seatgeek_client_id


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


def get_concert_information(zipcode, date1, date2, dist=3, per_page=100,
                            client_id=seatgeek_client_id):
    '''
    Fetch concert information from seatgeek

    Args:
        zipcode (str): zipcode to search near
        date1 (str): min date of search
        date2 (str): max date of search
        dist (str): distance (mi) around zipcode for search (default 3)
        per_page (int): maximum number of results (default: 100)
        client_id (str): seatgeek client id (default: from config.py)
    '''
    # Get dates in formate seatgeek likes
    if not date2:
        date2 = date1
    datetime1 = f'{date1}T00:00:00'
    datetime2 = f'{date2}T23:00:00'

    # seatgeek API request
    params = {"geoip": zipcode, "type": "concert",
              "per_page": per_page, "range": f"{dist}mi",
              "datetime_local.gte": datetime1, "datetime_local.lte": datetime2}
    base_url = f"https://api.seatgeek.com/2/events?client_id={client_id}"
    param_str = "&".join([f"{i}={v}" for i, v in params.items()])
    response = requests.get(base_url + "&" + param_str)
    data = response.json()
    if response.status_code == 200:
        # If there are no concerts raise exception
        if len(data['events']) < 1:
            raise NoConcertsFound
        return data
    else:
        raise FailedApiRequestError


def build_df_and_get_spotify_info(data):
    '''
    Take cocert information from the seatgeek API, make a dataframe, and populate
    with Spotify artist and track infomration

    Args:
        data (dict): dictionary from seatgeek api response

    Returns:
        pandas.DataFrame: dataframe with cncert and artist information in it
    '''

    # Use spotipy for its great support for large volume of requests
    client_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id,
                                                          client_secret=spotify_client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Pull select data fields and put into pandas dataframe
    df_dict = {}
    for event in data['events']:
        for performer in event['performers']:
            d = {}
            d['performer'] = performer['short_name']
            try:
                d['genre'] = performer['genres'][0]['name']
            except KeyError:
                d['genre'] = "NA"
            d['datetime_local'] = event['datetime_local']
            dt = datetime.strptime(d['datetime_local'], "%Y-%m-%dT%H:%M:%S")
            d['date_local'] = dt.strftime("%b %d %Y")
            d['time_local'] = dt.strftime("%I:%M%p")
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
            ' allowtransparency="true" allow="encrypted-media" class="p-1"></iframe>')


# Exceptions defined Here
class NoConcertsFound(Exception):
    """Raised when no seat geek results are found"""
    pass


class FailedApiRequestError(Exception):
    """Raised when api request is unscuccessful"""
    pass
