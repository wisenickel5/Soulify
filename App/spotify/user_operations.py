#from App import Base, Session
from App.database import Base, Session
import logging
from App.spotify.authenticate import make_get_request
from sqlalchemy import Column, Integer, String

class User(Base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	username = Column(String(64), index=True, unique=True)
	refresh_token = Column(String(150), index=True, unique=True)
	playlist_id_short = Column(String(30), index=True, unique=True)
	playlist_id_medium = Column(String(30), index=True, unique=True)
	playlist_id_long = Column(String(30), index=True, unique=True)

	# Represent our User Class's object as a string
	def __repr__(self):
		return '<User {}>'.format(self.username)

def add_user(username, refresh_token, playlist_id_short=None, playlist_id_medium=None, playlist_id_long=None):
	"""Function called when a user signs up for a new TopTracks playlist. If the user is new,
	then a new row is created with the appropriate column information. If the user already exists
	in the table, then only the playlist IDs are updated

	Args:
		username (string): the username that is store in the User table in the database
		refresh_token (string): the refresh_token that is store in the User table in the database
		playlist_id_short (string): The playlist_id that is stored in the User table in the database for new users
		playlist_id_medium (string): The playlist_id that is stored in the User table in the database for new users
		playlist_id_long (string): The playlist_id that is stored in the User table in the database for new users

	Returns:
		str: username
	"""
	session = Session()
	id_exists = session.query(User.id).filter_by(username=username).scalar()

	# new user
	if id_exists is None:
		user = User(username=username, refresh_token=refresh_token, playlist_id_short=playlist_id_short,
					playlist_id_medium=playlist_id_medium, playlist_id_long=playlist_id_long)
		session.add(user)
		logging.info('New auto user: ' + username)

	#user already exists
	else:
		user = session.query(User).get(id_exists)
		logging.info('Auto user updated: ' + user.username)

		# only update playlist IDs that are new
		if playlist_id_short is not None:
			user.playlist_id_short = playlist_id_short
		if playlist_id_medium is not None:
			user.playlist_id_medium = playlist_id_medium
		if playlist_id_long is not None:
			user.playlist_id_long = playlist_id_long

	session.commit()
	session.close()

def get_user_information(session):
	"""Gets user information such as username, user ID, and user location

	Args:
		session (Session): Flask Session Object

	Returns:
		dict : JSON Response
	"""
	url = 'https://api.spotify.com/v1/me'
	payload = make_get_request(session, url)

	if payload is None:
		return None

	return payload