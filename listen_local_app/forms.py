from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField, ValidationError
import re


class SearchForm(FlaskForm):
    # csrf = False
    zipcode = TextField("Zipcode")
    daterange = TextField("Date")
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
