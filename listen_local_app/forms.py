#!/usr/bin/python

'''
Flask_WTF Forms are defined here for use elsewhere in the app
'''

import re

from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms import SubmitField
from wtforms import StringField
from wtforms import ValidationError


class SearchForm(FlaskForm):
    # csrf = False
    zipcode = StringField("Zipcode")
    daterange = StringField("Date")
    distance = SelectField('Search Radius', choices=[(str(x), str(x)+'mi') for x in range(1, 51)],
                           default=5)
    submit = SubmitField("Send")

    def validate_zipcode(form, field):
        if not re.match(r'^[0-9]{5}(?:-[0-9]{4})?$', field.data):
            raise ValidationError('Must be a valid zip code')

    def validate_daterange(form, field):
        def _is_date(date):
            expr = "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
            return bool(re.match(expr, date))

        if not all(_is_date(d) for d in field.data.split(" to ")):
            raise ValidationError('Must be a valid date')

        # Add check that date is greater than today?
        today = datetime.now().date()
        if " to " in field.data:
            date2 = field.data.split(" to ")[1]
        else:
            date2 = field.data
        date2 = datetime(*[int(x) for x in date2.split("-")]).date()
        if date2 < today:
            raise ValidationError("Dates cannot be in the past")
