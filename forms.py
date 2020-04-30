from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField
from wtforms.validators import DataRequired, AnyOf, URL, Length, Optional, ValidationError
from enums import State, Genre

def anyof_multiple_field(values):
  message = 'Invalid value, must be one of: {0}.'.format( ','.join(values) )

  def _validate(form, field):
    error = False
    for value in field.data:
      if value not in values:
        error = True

    if error:
      raise ValidationError(message)

  return _validate

class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(), AnyOf([choice.value for choice in State])],
        choices=State.choices()
    )
    address = StringField(
        'address', validators=[DataRequired(), Length(-1, 200)]
    )
    phone = StringField(
        'phone', validators=[Length(-1, 10)]
    )
    image_link = StringField(
        'image_link', validators=[Length(-1, 500), URL(), Optional()]
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired(), anyof_multiple_field([choice.value for choice in Genre])],
        choices= Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link', validators=[Length(-1, 500), URL(), Optional()]
    )
    website_link = StringField(
        'website_link', validators=[Length(-1, 500), URL(), Optional()]
    )
    seeking_description = StringField(
        'seeking_description', validators=[Optional()]
    )

class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(), AnyOf([choice.value for choice in State])],
        choices= State.choices()
    )
    phone = StringField(
        # DONE implement validation logic for state
        'phone' , validators=[Length(-1, 10)]
    )
    image_link = StringField(
        'image_link', validators=[Length(-1, 500), URL(), Optional()]
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired(), anyof_multiple_field([choice.value for choice in Genre])],
        choices=Genre.choices()
    )
    facebook_link = StringField(
        # TODO implement enum restriction
        'facebook_link', validators=[Length(-1, 500), URL(), Optional()]
    )
    website_link = StringField(
        'website_link', validators=[Length(-1, 500), URL(), Optional()]
    )
    seeking_description = StringField(
        'seeking_description', validators=[Optional()]
    )

# DONE IMPLEMENT NEW ARTIST FORM AND NEW SHOW FORM

