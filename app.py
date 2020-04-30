#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form, CsrfProtect
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
csrf= CsrfProtect()
csrf.init_app(app)
migrate = Migrate(app, db)

# DONE: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    genres = db.Column(db.ARRAY(db.String))
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    show = db.relationship('Show', backref='venue', lazy=True)
    # DONE: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    genres = db.Column(db.ARRAY(db.String))
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venues = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(500))
    show = db.relationship('Show', backref='artist', lazy=True)
    # DONE: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  start_time = db.Column(db.DateTime(), nullable=False)
# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # DONE: replace with real venues data.
  # DONE: num_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  data=[]
  for venue in venues:
    venue_dif = (
      Venue.query.filter(Venue.city == venue[0]).filter(Venue.state == venue[1]).all()
    )
    data.append({"city": venue.city, "state": venue.state, "venues": venue_dif})
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # DONE search for Hop should return "The Musical Hop".
  # DONE search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form.get('search_term')
  venues = Venue.query.with_entities(Venue.id, Venue.name).filter(Venue.name.ilike(f'%{search_term}%')).all()
  responses = {"count": 0, "data": []}
  today = datetime.today()
  count = 0
  for venue in venues:
    count += 1
    shows = Show.query.filter_by(venue_id = venue.id)
    show_count = 0
    for show in shows:
      if show.start_time < today:
        show_count += 1
    responses['data'].append({'id': venue.id, "name": venue.name, "num_upcoming_shows": show_count})

  responses.update({'count': count})
  print(responses)
  return render_template('pages/search_venues.html', results=responses, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id
  # DONE fix past show count & future show count
  data = Venue.query.filter_by(id=venue_id).first()
  shows = Show.query.filter_by(venue_id= data.id).all()
  today = datetime.now()
  past_count = 0
  future_count = 0
  print(shows)
  formated_data ={
    "id": data.id,
    "name": data.name,
    "genres": data.genres,
    "address": data.address,
    "city": data.city,
    "state": data.state,
    "phone": data.phone,
    "website": data.website_link,
    "facebook_link": data.facebook_link,
    "seeking_talent": data.seeking_talent,
    "seeking_description": data.seeking_description,
    "image_link": data.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  for show in shows:
    if show.start_time < today:
      past_count += 1
      formated_data['past_shows'].append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
      })
    else:
        future_count += 1
        formated_data['upcoming_shows'].append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
      })
  formated_data.update({'past_shows_count': past_count, 'upcoming_shows_count': future_count})
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=formated_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  form = VenueForm()
  error= False
  if not form.validate():
    flash(form.errors)
    return redirect(url_for('create_venue_form'))
  try:
    data = request.form
    seeking = len(data.get('seeking_description'))
    seeking_talent = False
    if seeking != 0:
      seeking_talent = True

    venue = Venue(
    name= data.get('name'),
    city= data.get('city'),
    state= data.get('state'),
    genres= data.getlist('genres'),
    address= data.get('address'),
    phone= data.get('phone'),
    website_link= data.get('website_link'),
    image_link= data.get('image_link'),
    facebook_link= data.get('facebook_link'),
    seeking_talent= seeking_talent,
    seeking_description= data.get('seeking_description')
    )
    db.session.add(venue)
    db.session.commit()
  except:
    error= True
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

    # on successful db insert, flash success
      
    # DONE: on unsuccessful db insert, flash an error instead.
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.filter_by(id=venue_id).first()
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # TODO :BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database
  artists = Artist.query.all()
  data=[]
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # DONE: add num upcoming shows
  search_term = request.form.get('search_term')
  artists = Artist.query.with_entities(Artist.id, Artist.name).filter(Artist.name.ilike(f'%{search_term}%')).all()
  responses = {"count": 0, "data": []}
  today = datetime.today()
  count = 0
  num_show = Show.query.all()
  for artist in artists:
    count += 1
    shows = Show.query.filter_by(artist_id = artist.id)
    show_count = 0
    for show in shows:
      if show.start_time < today:
        show_count += 1

    responses['data'].append({'id': artist.id, "name": artist.name, "num_upcoming_shows": show_count})
  
  responses.update({'count': count})
  print(responses)
  return render_template('pages/search_artists.html', results=responses, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id
  # DONE: FIX GENRE ARRAY
  artist = Artist.query.filter_by(id=artist_id).first()
  shows = Show.query.filter_by(artist_id = artist_id).all()
  today = datetime.now()
  past_count = 0
  future_count = 0
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venues,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  for show in shows:
    if show.start_time < today:
      past_count += 1
      data['past_shows'].append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
      })
    else:
      future_count += 1
      data['upcoming_shows'].append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
      })

  data.update({'past_shows_count': past_count, 'upcoming_shows_count': future_count})
 #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    artist= Artist.query.filter_by(id=artist_id).first()
    data = request.form
    seeking_description= len(data.get('seeking_description'))
    artist.name = data.get('name')
    artist.genres= data.getlist('genres')
    artist.city= data.get('city')
    artist.state= data.get('state')
    artist.phone = data.get('phone')
    artist.image_link= data.get('image_link')
    artist.website_link=data.get('website_link')
    artist.facebook_link= data.get('facebook_link')
    if seeking_description != 0:
      artist.seeking_venues = True
      artist.seeking_description = data.get('seeking_description')
    else:
      artist.seeking_venues = False
      artist.seeking_description = ''
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter_by(id=artist_id).first()
  form.name.default = artist.name
  form.genres.default = artist.genres
  form.city.default= artist.city
  form.state.default= artist.state
  form.phone.default= artist.phone
  form.image_link.default= artist.image_link
  form.website_link.default= artist.website_link
  form.facebook_link.default= artist.facebook_link
  form.seeking_description.default= artist.seeking_description
  form.process()
  # DONE: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    venue= Venue.query.filter_by(id=venue_id).first()
    data = request.form
    seeking_description= len(data.get('seeking_description'))
    venue.name = data.get('name')
    venue.genres= data.getlist('genres')
    venue.city= data.get('city')
    venue.state= data.get('state')
    venue.phone = data.get('phone')
    venue.image_link= data.get('image_link')
    venue.website_link=data.get('website_link')
    venue.facebook_link= data.get('facebook_link')
    if seeking_description != 0:
      venue.seeking_talent = True
      venue.seeking_description = data.get('seeking_description')
    else:
      venue.seeking_talent = False
      venue.seeking_description = ''
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # DONE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first()
  form.name.default = venue.name
  form.genres.default = venue.genres
  form.address.default= venue.address
  form.city.default= venue.city
  form.state.default= venue.state
  form.phone.default= venue.phone
  form.image_link.default= venue.image_link
  form.website_link.default= venue.website_link
  form.facebook_link.default= venue.facebook_link
  form.seeking_description.default= venue.seeking_description
  form.process()
  # DONE: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  error = False
  form = ArtistForm()
  if not form.validate():
    flash(form.errors)
    return redirect(url_for('create_artist_form'))
  try:
    data = request.form
    seeking_venues = len(data.get('seeking_description'))
    seeking = False
    if seeking_venues != 0:
      seeking = True  
    artist= Artist(
      name= data.get('name'),
      city= data.get('city'),
      state= data.get('state'),
      phone= data.get('phone'),
      genres = data.getlist('genres'),
      image_link= data.get('image_link'),
      website_link = data.get('website_link'),
      facebook_link= data.get('facebook_link'),
      seeking_venues= seeking,
      seeking_description = data.get('seeking_description')
    )
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # on successful db insert, flash success
  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  results = Show.query.all()
  shows= []
  for result in results:
    shows.append({
    "venue_id": result.venue_id,
    "venue_name": result.venue.name,
    "artist_id": result.artist_id,
    "artist_name": result.artist.name,
    "artist_image_link": result.artist.image_link,
    "start_time": result.start_time.strftime("%m/%d/%Y, %H:%M")
    })
  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # DONE: insert form data as a new Show record in the db, instead
  error = False
  try:
    data = request.form
    show = Show(
      artist_id = data.get('artist_id'),
      venue_id = data.get('venue_id'),
      start_time = data.get('start_time')
    )
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
    

  if not error:
    flash('Show was successfully listed!')
  # on successful db insert, flash success
  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
