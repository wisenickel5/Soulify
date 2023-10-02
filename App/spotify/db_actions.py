import requests

def db_add_tracks_playlist(access_token, playlist_id, uri_list):
	"""
	Submits ADD Request to Spotify API with resource to be added
	until a status code that equals 201 is received or log the error.

	Args:
		access_token (str): Key used for authorization check
		playlist_id (str): Key used to identify the playlist of tracks
		uri_list (list): A list of tracks as URIs

	Returns:
		string : Success log
	"""
	url = 'https://api.spotify.com/v1/playlists/' + playlist_id + '/tracks'

	headers = {"Authorization": "Bearer {}".format(access_token), 'Accept': 'application/json', 'Content-Type': 'application/json'}
	uri_str = ""
	for uri in uri_list:
		uri_str += "\"" + uri + "\","

	data = "{\"uris\": [" + uri_str[0:-1] + "]}"

	payload = requests.post(url, headers=headers, data=data)

	if payload.status_code == 201:
		return "success"
	else:
		return None

def db_get_tracks_playlist(access_token, playlist_id, limit=100):
	"""
	Submits GET Request to Spotify API with resource to receive tracks
	until a status code that equals 200 is received or log the error.

	Args:
		access_token:
		playlist_id:
		limit (int): Maximum number of tracks per request

	Returns:
		string : Success log
		track_uri (list): List of tracks URI from playlist
	"""
	url = 'https://api.spotify.com/v1/playlists/' + playlist_id + '/tracks'

	headers = {"Authorization": "Bearer {}".format(access_token)}
	offset = 0
	track_uri = []

	# iterate through all tracks in a playlist (Spotify limits number per request)
	total = 1
	while total > offset:
		params = {'limit': limit, 'fields': 'total,items(track(uri))', 'offset': offset}
		payload = requests.get(url, headers=headers, params=params)

		if payload.status_code == 200:
			payload = payload.json()
		else:
			return None
		
		for item in payload['items']:
			track_uri.append(item['track']['uri'])

		total = payload['total']
		offset += limit

	return track_uri

def db_clear_playlist(access_token, playlist_id):
	"""
	Submits DELETE Request to Spotify API with resource to remove tracks
	until a status code that equals 200 is received or log the error.

	Args:
		access_token (str): Key used for authorization check
		playlist_id (str): Key used to identify the playlist of tracks
	Returns:
		string : Success log
	"""
	url = 'https://api.spotify.com/v1/playlists/' + playlist_id + '/tracks'
	uri_list = db_get_tracks_playlist(access_token, playlist_id)

	uri_str = ""
	for uri in uri_list:
		uri_str += "{\"uri\":\"" + uri + "\"},"

	data = "{\"tracks\": [" + uri_str[0:-1] + "]}"
	headers = {"Authorization": "Bearer {}".format(access_token), 'Accept': 'application/json', 'Content-Type': 'application/json'}
	payload = requests.delete(url, headers=headers, data=data)

	if payload.status_code == 200:
		return "success"
	else:
		return None

def db_get_top_tracks_uri(access_token, time: str, limit: int=25):
	"""
	Submits GET Request to Spotify API with resource to receive tracks
	until a status code that equals 200 is received or log the error.

	Args:
		access_token:
		time (str): Maximum number of tracks per request
		limit (int): Maximum number of tracks per request

	Returns:
		track_uri (list): List of tracks URI from playlist
	"""
	url = 'https://api.spotify.com/v1/me/top/tracks'
	params = {'limit': limit, 'time_range': time}
	headers = {"Authorization": "Bearer {}".format(access_token)}
	payload = requests.get(url, headers=headers, params=params)

	if payload.status_code == 200:
		payload = payload.json()
	else:
		return None

	track_uri = []
	for track in payload['items']:
		track_uri.append(track['uri'])

	return track_uri
