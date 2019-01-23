#!/usr/bin/python

import json
import pytest
import spotipy

from api_responses import TEST_URL2API_RESPONSE
from conftest import _get_app_client
from listen_local_app.functions import get_access_token
from listen_local_app.functions import get_concert_information
from listen_local_app.functions import lookup_spotify_artist_track
from listen_local_app.functions import make_spotify_play_button
from listen_local_app.functions import NoConcertsFound, FailedApiRequestError
from listen_local_app.functions import process_daterange
from spotipy.oauth2 import SpotifyClientCredentials
from unittest import mock


@pytest.mark.parametrize("daterange,expected", [
    ('2011-02-01', ('2011-02-01', None)),
    ('2011-02-01 to 2011-02-04', ('2011-02-01', '2011-02-04')),
])
def test_process_daterange(daterange, expected):
    date1, date2 = process_daterange(daterange)
    if date2:
        assert date1 == expected[0] and date2 == expected[1]
    else:
        assert date1 == expected[0] and date2 is expected[1]


def test_make_spotify_play_button():
    height = 300
    width = 400
    uri = 'spotify:album:1DFixLWuPkv3KT3TnV35m3'
    expected = (f'<iframe src="https://open.spotify.com/embed/album/1DFixLWuPkv3KT3TnV35m3"'
                f' width="{width}" height="{height}" frameborder="0"'
                ' allowtransparency="true" allow="encrypted-media"></iframe>')

    assert make_spotify_play_button(uri, height=height, width=width) == expected


# This method will be used by the mock to replace requests.get
# https://stackoverflow.com/questions/15753390/how-can-i-mock-requests-and-the-response
def mocked_requests(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_text, status_code):
            self.text = json_text
            self.status_code = status_code

        def json(self):
            if self.text:
                return json.loads(self.text)
            else:
                return None

    if args[0] in TEST_URL2API_RESPONSE.keys():
        return MockResponse(TEST_URL2API_RESPONSE[args[0]], 200)
    else:
        return MockResponse(None, 404)


@mock.patch('requests.post', side_effect=mocked_requests)
def test_get_access_token(mock_post):
    app, client = _get_app_client()
    with app.test_request_context():
        code = "1234567890"
        token = get_access_token(code)
        assert token == "Bearer test-access-token-1234"


@mock.patch('requests.get', side_effect=mocked_requests)
def test_get_concert_information_success(mock_get):
    data = get_concert_information("19130", "2019-01-22", None, per_page=1,
                                   client_id="this_aint_real")
    assert data == {"events": [{}]}


@mock.patch('requests.get', side_effect=mocked_requests)
def test_get_concert_information_no_concerts(mock_get):
    with pytest.raises(NoConcertsFound):
        get_concert_information("11111", "2019-01-22", None, per_page=1,
                                client_id="this_aint_real")


@mock.patch('requests.get', side_effect=mocked_requests)
def test_get_concert_information_404(mock_get):
    with pytest.raises(FailedApiRequestError):
        get_concert_information("11112", "2019-01-22", None, per_page=1,
                                client_id="this_aint_real")


def test_lookup_spotify_artist_track():
    config = pytest.importorskip("config")
    client_credentials_manager = SpotifyClientCredentials(client_id=config.spotify_client_id.decode('utf-8'),  # noqa
                                                          client_secret=config.spotify_client_secret.decode('utf-8'))  # noqa
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    print(lookup_spotify_artist_track(sp, "Jay-Z"))
