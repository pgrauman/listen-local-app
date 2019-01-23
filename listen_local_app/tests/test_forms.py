#!/usr/bin/python

import pytest

from conftest import _get_app_client
from datetime import datetime
from datetime import timedelta
from listen_local_app.forms import SearchForm


def _today_shift(delta=0):
    return datetime.now().date() + timedelta(days=delta)


def _make_test_form_input(field, value):
    data = {'zipcode': '19130', 'daterange': _today_shift(), 'distance': '1', 'submit': True}
    data[field] = value
    return data


# Test zipcode form intput validation code
@pytest.mark.parametrize("data,expect_valid", [
    (_make_test_form_input('zipcode', '19130'), True),
    (_make_test_form_input('zipcode', '19130a'), False),
    (_make_test_form_input('zipcode', '19130-5555'), True),
    (_make_test_form_input('zipcode', 'adagarbageinput888'), False),
    (_make_test_form_input('zipcode', 'evil_garbage();'), False),
])
def test_zipcode_input(data, expect_valid):
    app, client = _get_app_client()

    @app.route('/', methods=['POST'])
    def index():
        form = SearchForm()
        test_valid = form.validate()
        assert test_valid == expect_valid
        if expect_valid:
            assert not form.errors.keys()
        else:
            assert 'zipcode' in form.errors.keys()
        return

    client.post('/', data=data)


# Test daterange form input validation code
@pytest.mark.parametrize("data,expect_valid", [
    (_make_test_form_input('daterange', _today_shift(0)), True),
    (_make_test_form_input('daterange', f'{_today_shift(0)} to {_today_shift(3)}'), True),
    (_make_test_form_input('daterange', _today_shift(-10)), False),
    (_make_test_form_input('daterange', f'{_today_shift(-10)} to {_today_shift(-3)}'), False),
    (_make_test_form_input('daterange', 'adagarbageinput888'), False),
    (_make_test_form_input('daterange', 'evil_garbage();'), False),
])
def test_daterange_input(data, expect_valid):
    app, client = _get_app_client()

    @app.route('/', methods=['POST'])
    def index():
        form = SearchForm()
        test_valid = form.validate()
        assert test_valid == expect_valid
        if expect_valid:
            assert not form.errors.keys()
        else:
            assert 'daterange' in form.errors.keys()
        return

    client.post('/', data=data)
