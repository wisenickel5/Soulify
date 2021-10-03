import requests

"""
access_token - the unique key from authorization used to access the payload data
playlist_id - the identification number for an existing playlist
uri_list - a collection of uris in strings 
"""
def dbAddTracksPlaylist(access_token, playlist_id, uri_list):
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


"""
limit - the maximum number of tracks per request to avoid overloading the server
"""
def dbGetTracksPlaylist(access_token, playlist_id, limit=100):
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

def dbClearPlaylist(access_token, playlist_id):
	url = 'https://api.spotify.com/v1/playlists/' + playlist_id + '/tracks'
	uri_list = dbGetTracksPlaylist(access_token, playlist_id)

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

"""
time - short_term, medium_term, or long_term
"""
def dbGetTopTracksURI(access_token, time, limit=25):
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
