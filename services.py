import logging
import time

# SQLAlchemy Imports
from sqlalchemy.sql.coercions import StrAsPlainColumnImpl

# Local Imports
from authenticate import (makeGetRequest, makePostRequest, makePutRequest,
                          refreshToken)
from db_actions import (dbAddTracksPlaylist, dbClearPlaylist,
                        dbGetTopTracksURI, dbGetTracksPlaylist)
from main import Base, Session
from user_operations import User


def createPlaylist(session, playlist_name):
	"""Creates a group of a songs (playlist) with the parameter session and pulls the 
	user inputted playlist name


	Args:
		session (Session): Flask Session Object
		playlist_name (String): Name of the playlist which is being called for

	Returns:
		Tuple : 
	"""
	url = 'https://api.spotify.com/v1/users/' + session['user_id'] + '/playlists'
	data = "{\"name\":\"" + playlist_name + "\",\"description\":\"Created by Discover Daily\"}"
	payload = makePostRequest(session, url, data)

	if payload == None:
		return None

	return payload['id'], payload['uri']

def updatePlaylists():
	"""Function to literally update playlists. Authorization with spotify is checked. Authorization 
	with user is also checked to see if playlist is deleted or not. 

	Args:
		No arguments 


	Returns: 
		No returns. (Checks throughout code for authorization and playlist deleted/updated)
	"""
	session = Session()

	# attempt to update each user's playlists
	for user in session.query(User):
		is_active = False

		# authorize the application with Spotify API
		payload = refreshToken(user.refresh_token)

		# if user account has been removed or authorization revoked, user is deleted
		if payload == None:
			session.delete(user)
		else:		
			access_token = payload[0]

			playlist = user.playlist_id_short
			if playlist != None:

				# if the playlist has not been deleted
				if (dbClearPlaylist(access_token, playlist) != None):
					uri_list = dbGetTopTracksURI(access_token, 'short_term', 50)
					dbAddTracksPlaylist(access_token, playlist, uri_list)
					is_active = True
				else:
					user.playlist_id_short = None

			playlist = user.playlist_id_medium
			if playlist != None:
				if (dbClearPlaylist(access_token, playlist) != None):
					uri_list = dbGetTopTracksURI(access_token, 'medium_term', 50)
					dbAddTracksPlaylist(access_token, playlist, uri_list)
					is_active = True
				else:
					user.playlist_id_medium = None

			playlist = user.playlist_id_long
			if playlist != None:
				if (dbClearPlaylist(access_token, playlist) != None):
					uri_list = dbGetTopTracksURI(access_token, 'long_term', 50)
					dbAddTracksPlaylist(access_token, playlist, uri_list)
					is_active = True
				else:
					user.playlist_id_long = None

			# if no playlists could be updated, then remove user
			if not is_active:
				session.delete(user)

	session.commit()
	session.close()

	logging.info('Updated TopTracks Playlists')

def addTracksPlaylist(session, playlist_id, uri_list):
	"""Using the spotify API to add sigular tracks to a playlist. 

	Args:
		session (Session): Flask Session Object
		playlist_id (int): ID for the playlist for spotify API to function 
		uri_list (): [description] **Will come back to

	Return: 
		No return. 
	"""
	url = 'https://api.spotify.com/v1/playlists/' + playlist_id + '/tracks'

	uri_str = ""
	for uri in uri_list:
		uri_str += "\"" + uri + "\","

	data = "{\"uris\": [" + uri_str[0:-1] + "]}"
	makePostRequest(session, url, data)

	return

def getTracksPlaylist(session, playlist_id, limit=100):
	"""Get function which uses the spotify API along as the playlist ID in order to get all the 
	tracks from the playlist.


	Args:
		session (Session): Flask Session Object
		playlist_id (int): ID for the playlist for spotify API to function
		limit (int, optional): The literal limit of songs per tracks on the playlist. Defaults to 100.

	Returns:
		[type]: Track uri **Come back to this
	"""
	url = 'https://api.spotify.com/v1/playlists/' + playlist_id + '/tracks'

	offset = 0
	track_uri = []

	# iterate through all tracks in a playlist (Spotify limits number per request)
	total = 1
	while total > offset:
		params = {'limit': limit, 'fields': 'total,items(track(uri))', 'offset': offset}
		payload = makeGetRequest(session, url, params)

		if payload == None:
			return None
		
		for item in payload['items']:
			track_uri.append(item['track']['uri'])

		total = payload['total']
		offset += limit

	return track_uri

def getAllTopTracks(session, limit=10):
	"""Creates a list of tracks which are in the top 10 in the spotify API list. 

	Args:
		session (Session): Flask Session Object
		limit (int, optional): Number of songs per top tracks. Defaults to 10. **

	Returns:
		int: Returns the id of the top 10 tracks.
	"""
	url = 'https://api.spotify.com/v1/me/top/tracks'
	track_ids = []
	time_range = ['short_term', 'medium_term', 'long_term']

	for time in time_range:
		track_range_ids = []

		params = {'limit': limit, 'time_range': time}
		payload = makeGetRequest(session, url, params)

		if payload == None:
			return None

		for track in payload['items']:
			track_range_ids.append(track['id'])

		track_ids.append(track_range_ids)

	return track_ids

def getTopTracksID(session, time, limit=25):
	"""Creates a list of tracks which are top 25 on the spotify API list.

	Args:
		session (Session): Flask Session Object
		time (int): The range of time per song. 
		limit (int, optional): Number of tracks per playlist. Defaults to 25.

	Returns:
		int: Returns the id of the top 10 tracks.
	"""
	url = 'https://api.spotify.com/v1/me/top/tracks'
	params = {'limit': limit, 'time_range': time}
	payload = makeGetRequest(session, url, params)

	if payload == None:
		return None

	track_ids = []
	for track in payload['items']:
		track_ids.append(track['id'])

	return track_ids

def getTopTracksURI(session, time, limit=25):  
	"""[summary]

	Args:
		session (Session): Flask Session Object
		time (int): The range of time per song. 
		limit (int, optional): [description]. Defaults to 25.

	Returns:
		[type]: [description]
	"""
	url = 'https://api.spotify.com/v1/me/top/tracks'
	params = {'limit': limit, 'time_range': time}
	payload = makeGetRequest(session, url, params)

	if payload == None:
		return None

	track_uri = []
	for track in payload['items']:
		track_uri.append(track['uri'])

	return track_uri

def getTopArtists(session, time, limit=10):
	"""[summary]

	Args:
		session (Session): Flask Session Object
		time (int): The range of time per song. 
		limit (int, optional): Gets the top 10 artists onto the list.. Defaults to 10. **

	Returns:
		int: Returns the id of the top 10 artists.
	"""
	url = 'https://api.spotify.com/v1/me/top/artists'
	params = {'limit': limit, 'time_range': time}
	payload = makeGetRequest(session, url, params)

	if payload == None:
		return None

	artist_ids = []
	for artist in payload['items']:
		artist_ids.append(artist['id'])

	return artist_ids

def getRecommendedTracks(session, search, tuneable_dict, limit=25):
	"""This call pulls the top 25 tracks which are directed to a playlist. 

	Args:
		session (Session): Flask Session Object
		search ([type]): [description]
		tuneable_dict (dict): 
		limit (int, optional): Number of tracks which the call will pull. Defaults to 25.

	Returns:
		int (?): rec_track_uri
	"""
	track_ids = ""
	artist_ids = ""
	for item in search:

		# tracks IDs start with a 't:' to identify them
		if item[0:2] == 't:':
			track_ids += item[2:] + ","

		# artist IDs start with an 'a:' to identify them
		if item[0:2] == 'a:':
			artist_ids += item[2:] + ","

	url = 'https://api.spotify.com/v1/recommendations'
	params = {'limit': limit, 'seed_tracks': track_ids[0:-1], 'seed_artists': artist_ids[0:-1]}
	params.update(tuneable_dict)
	payload = makeGetRequest(session, url, params)

	if payload == None:
		return None

	rec_track_uri = []
	
	for track in payload['tracks']:
		rec_track_uri.append(track['uri'])

	return rec_track_uri

def shuffle(session, device, is_shuffle=True):
	"""Shuffle call. Shuffles all songs on the platform.

	Args:
		session (Session): Flask Session Object
		device (int): Device ID of the user device. 
		is_shuffle (bool, optional): Checks if the device's playlist is shuffled. Defaults to True.

	Returns:
		tuple : Session, url, params
	"""
	url = 'https://api.spotify.com/v1/me/player/shuffle'
	params = {'state': is_shuffle, 'device_id': device}
	payload = makePutRequest(session, url, params)
	return payload

def startPlayback(session, device):
	"""Starts the playback of the session on a user device.

	Args:
		session (Session): Flask Session Object
		device (int): Device ID of the user device.

	Returns:
		tuple:  Session, url, params
	"""
	url = 'https://api.spotify.com/v1/me/player/play'
	params = {'device_id': device}
	payload = makePutRequest(session, url, params)
	return payload

def startPlaybackContext(session, playlist, device):
	"""Starts playback from the playlist on a user device. 

	Args:
		session (Session): Flask Session Object
		playlist (int): Selected user playlist
		device (int): Device ID of the user device.

	Returns:
		tuple:  Session, url, params
	"""
	url = 'https://api.spotify.com/v1/me/player/play'
	params = {'device_id': device}
	data = "{\"context_uri\":\"" + playlist + "\",\"offset\":{\"position\":0},\"position_ms\":0}"
	payload = makePutRequest(session, url, params, data)
	return payload

 
def pausePlayback(session):
	"""Stops the user session from playing tracks. 

	Args:
		session (Session): Flask Session Object

	Returns:
		Tuple: session, url
	"""
	url = 'https://api.spotify.com/v1/me/player/pause'
	payload = makePutRequest(session, url)
	return payload

def skipTrack(session):
	"""Skips a track.

	Args:
		session (Session): Flask Session Object

	Returns:
		Tuple: session, url, data
	"""
	url = 'https://api.spotify.com/v1/me/player/next'
	data = {}
	payload = makePostRequest(session, url, data)
	return payload


def getTrack(session):
	"""Call to get the track ID from the user session. 

	Args:
		session (Session): Flask Session Object

	Returns:
		tuple: name, img 
	"""
	url = 'https://api.spotify.com/v1/me/player/currently-playing'
	payload = makeGetRequest(session, url)

	if payload == None:
		return None

	# check to make sure the newest track is being grabbed (progress must be under 5000ms)
	if payload['progress_ms'] != None and payload['progress_ms'] > 5000:
		time.sleep(0.2)
		payload = makeGetRequest(session, url)

		if payload == None:
			return None

	name = payload['item']['name']
	img = payload['item']['album']['images'][0]['url']

	return {'name': name, 'img': img}

def getTrackAfterResume(session):
	"""Gets the track after resuming the user session.

	Args:
		session (Session): Flask Session Object

	Returns:
			tuple: name, img 
	"""
	url = 'https://api.spotify.com/v1/me/player/currently-playing'
	payload = makeGetRequest(session, url)

	if payload == None :
		return None

	name = payload['item']['name']
	img = payload['item']['album']['images'][0]['url']

	return {'name': name, 'img': img}

def searchSpotify(session, search, limit=4):
	"""Searches the entire spotify library using the spotify API call

	Args:
		session (Session): Flask Session Object
		search ([type]): [description]
		limit (int, optional): Limit of searches shown in the search bar. Defaults to 4.

	Returns:
		Tuple: label, item
	"""
	url = 'https://api.spotify.com/v1/search'
	params = {'limit': limit, 'q': search + "*", 'type': 'artist,track'}
	payload = makeGetRequest(session, url, params)

	if payload == None:
		return None

	# response includes both artist and track names
	results = []
	for item in payload['artists']['items']:

		# append 'a:' to artist URIs so artists and tracks can be distinguished 
		results.append([item['name'], 'a:' + item['id'], item['popularity']])

	for item in payload['tracks']['items']:

		# track names will include both the name of the track and all artists
		full_name = item['name'] + " - "
		for artist in item['artists']:
			full_name += artist['name'] + ", "

		# append 't:' to track URIs so tracks and artists can be distinguished 
		results.append([full_name[0:-2], 't:' + item['id'], item['popularity']])


	# sort them by popularity (highest first)
	results.sort(key=lambda x: int(x[2]), reverse=True)

	results_json = []
	for item in results:
		results_json.append({'label': item[0], 'value': item[1]})

	return results_json
