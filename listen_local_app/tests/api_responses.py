
fake_client_id = "this_aint_real"
test_seatgeek_url = f"https://api.seatgeek.com/2/events?client_id={fake_client_id}&geoip=19130&type=concert&per_page=1&range=3mi&datetime_local.gte=2019-01-22T00:00:00&datetime_local.lte=2019-01-22T23:00:00"  # noqa
test_seatgeek_response = '{"events": [{}]}'

test_seatgeek_noconcert_url = f"https://api.seatgeek.com/2/events?client_id={fake_client_id}&geoip=11111&type=concert&per_page=1&range=3mi&datetime_local.gte=2019-01-22T00:00:00&datetime_local.lte=2019-01-22T23:00:00"  # noqa
test_seatgeek_noconcert_response = '{"events": []}'

test_auth_url = 'https://accounts.spotify.com/api/token'
test_auth_response = '{"access_token": "test-access-token-1234", "token_type": "Bearer", "expires_in": 3600, "refresh_token": "test-refresh-token", "scope": "playlist-read-private user-library-read user-follow-read playlist-modify-private playlist-modify-public user-read-email user-top-read"}'  # noqa


TEST_URL2API_RESPONSE = {test_seatgeek_url: test_seatgeek_response,
                         test_auth_url: test_auth_response,
                         test_seatgeek_noconcert_url: test_seatgeek_noconcert_response}  # noqa