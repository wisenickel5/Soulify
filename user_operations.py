from main import Base, Session
import logging
from authenticate import makeGetRequest
from sqlalchemy import Column, Integer, String

class User(Base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	username = Column(String(64), index=True, unique=True)
	refreshToken = Column(String(150), index=True, unique=True)
	playlist_id_short = Column(String(30), index=True, unique=True)
	playlist_id_medium = Column(String(30), index=True, unique=True)
	playlist_id_long = Column(String(30), index=True, unique=True)

	# Represent our User Class's object as a string
	def __repr__(self):
		return '<User {}>'.format(self.username)

def addUser(username, refresh_token, playlist_id_short=None, playlist_id_medium=None, playlist_id_long=None):
	"""Function called when a user signs up for a new TopTracks playlist. If the user is new, 
	then a new row is created with the appropriate column information. If the user already exists 
	in the table, then only the playlist IDs are updated

	Args:
		username (string): the username that is store in the User table in the database
		refresh_token (string): the refresh_token that is store in the User table in the database
		playlist_id_short (string): The plalist_id that is stored in the User table in the database for new users 
		playlist_id_medium (string): The plalist_id that is stored in the User table in the database for new users
		playlist_id_long (string): The plalist_id that is stored in the User table in the database for new users

	Returns:
		str: username
	"""
	session = Session()
	id_exists = session.query(User.id).filter_by(username=username).scalar()

	# new user
	if id_exists == None:
		user = User(username=username, refresh_token=refresh_token, playlist_id_short=playlist_id_short, playlist_id_medium=playlist_id_medium, playlist_id_long=playlist_id_long)
		session.add(user)
		logging.info('New auto user: ' + username)

	#user already exists
	else:
		user = session.query(User).get(id_exists)
		logging.info('Auto user updated: ' + user.username)

		# only update playlist IDs that are new
		if playlist_id_short != None:
			user.playlist_id_short = playlist_id_short
		if playlist_id_medium != None:
			user.playlist_id_medium = playlist_id_medium
		if playlist_id_long != None:
			user.playlist_id_long = playlist_id_long

	session.commit()
	session.close()

def getUserInformation(session):
	"""Gets user information such as username, user ID, and user location

	Args:
		session (Session): Flask Session Object

	Returns:
		dict : JSON Response
	"""
	url = 'https://api.spotify.com/v1/me'
	payload = makeGetRequest(session, url)

	if payload == None:
		return None

	return payload

def getUserDevices(session):
	"""Gets all of a user's available devices.

	Args:
		session (Session): Flask Session Object

	Returns:
		device_list:
		string: name
		Integer: ID primary key

	"""
	url = 'https://api.spotify.com/v1/me/player/devices'
	payload = makeGetRequest(session, url)

	if payload == None:
		return None

	device_list = []
	for device in payload['devices']:

		# restricted devices cannot be accessed by the application
		if device['is_restricted'] != True:
			device_list.append([device['name'], device['id']])

	return device_list

def getUserPlaylists(session, limit=20):
	"""Gets all of a user playlists

	Args:
		session (Session): Flask Session Object
		limit (int): [description]. Defaults to 20.

	Returns:
		list of playlist:
		string: name
		string: uri, identify a physical or logical resource 
	"""
	url = 'https://api.spotify.com/v1/me/playlists'
	offset = 0
	playlist = []

	# iterate through all playlists of a user (Spotify limits amount returned with one call)
	total = 1
	while total > offset:
		params = {'limit': limit, 'offset': offset}
		payload = makeGetRequest(session, url, params)

		if payload == None:
			return None
		
		for item in payload['items']:
			playlist.append([item['name'], item['uri']])

		total = payload['total']
		offset += limit

	return playlist