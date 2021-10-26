import logging
import time

# Flask Imports
from flask import (abort, jsonify, make_response, redirect, render_template,
                   request, session)

# Local Imports
from authenticate import createStateKey, getToken
from main import app
from services import (addTracksPlaylist, createPlaylist, getAllTopTracks,
                      getRecommendedTracks, getTopTracksURI, getTrack,
                      getTrackAfterResume, pausePlayback, searchSpotify,
                      shuffle, skipTrack, startPlayback, startPlaybackContext)
from user_operations import (addUser, getUserDevices, getUserInformation,
                             getUserPlaylists)

@app.route('/')
@app.route('/index')
def index():
	""" 
	Homepage.
	"""
	return render_template('index.html')

@app.route('/authorize')
def authorize():
	""" 
	This feature activates when, the user decides to not allow 
	the app to use their account and the page redirects them to the account 
	page. 
	"""
	client_id = app.config['CLIENT_ID']
	redirect_uri = app.config['REDIRECT_URI']
	scope = app.config['SCOPE']

	# state key used to protect against cross-site forgery attacks
	state_key = createStateKey(15)
	session['state_key'] = state_key

	# redirect user to Spotify authorization page
	authorize_url = 'https://accounts.spotify.com/en/authorize?'
	parameters = 'client_id=' + client_id + '&response_type=code' + '&redirect_uri=' + redirect_uri + '&scope=' + scope + '&state=' + state_key
	app.logger.info(authorize_url + parameters)
	response = make_response(redirect(authorize_url + parameters))

	return response

@app.route('/callback')
def callback():
	"""
	Called after a new user has authorized the application through the Spotift API page.
	Stores user information in a session and redirects user back to the page they initally
	attempted to visit.
	"""
	# make sure the response came from Spotify
	if request.args.get('state') != session['state_key']:
		return render_template('index.html', error='State failed.')
	if request.args.get('error'):
		return render_template('index.html', error='Spotify error.')
	else:
		code = request.args.get('code')
		session.pop('state_key', None)

		# get access token to make requests on behalf of the user
		payload = getToken(code)
		#app.logger.info(f'(Callback) Payload: {payload}')
		if payload != None:
			session['token'] = payload[0]
			session['refresh_token'] = payload[1]
			session['token_expiration'] = time.time() + payload[2]
		else:
			return render_template('index.html', error='Failed to access token.')

	current_user = getUserInformation(session)
	session['user_id'] = current_user['id']
	logging.info('new user:' + session['user_id'])

	return redirect(session['previous_url'])

@app.route('/information',  methods=['GET'])
def information():
	"""
	This page displays policies and information about the 
	features on the app.
	"""
	return render_template('information.html')

@app.route('/tracks',  methods=['GET'])
def tracks():
	"""
	This page shows most played tracks by the user over many differnet 
	time peiords.
	"""
	# make sure application is authorized for user 
	if session.get('token') == None or session.get('token_expiration') == None:
		session['previous_url'] = '/tracks'
		return redirect('/authorize')

	# collect user information
	if session.get('user_id') == None:
		current_user = getUserInformation(session)
		session['user_id'] = current_user['id']

	track_ids = getAllTopTracks(session)

	if track_ids == None:
		return render_template('index.html', error='Failed to gather top tracks.')
		
	return render_template('tracks.html', track_ids=track_ids)
	
@app.route('/create',  methods=['GET'])
def create():
	"""
	This feature allows the user to create a 
	plalist by searching song title/artist.
	"""
	# make sure application is authorized for user 
	if session.get('token') == None or session.get('token_expiration') == None:
		session['previous_url'] = '/create'
		return redirect('/authorize')

	# collect user information
	if session.get('user_id') == None:
		current_user = getUserInformation(session)
		session['user_id'] = current_user['id']

	return render_template('create.html')
	
@app.route('/timer',  methods=['GET'])
def timer():
	"""
	Activates when the user access the interval timer, it shows the platfrom 
	of device an playlist being played from. it also includes a timer set 
	and timer countdown.
	"""
	# make sure application is authorized for user 
	if session.get('token') == None or session.get('token_expiration') == None:
		session['previous_url'] = '/timer'
		return redirect('/authorize')

	# collect user information
	if session.get('user_id') == None:
		current_user = getUserInformation(session)
		session['user_id'] = current_user['id']

	device_names = getUserDevices(session)
	playlist_names = getUserPlaylists(session)

	if device_names == None or playlist_names == None:
		return render_template('index.html', error='Failed to get device ID and playlists.')

	# length is needed to iterate properly with Jinja
	device_length = len(device_names)
	playlist_length = len(playlist_names)

	return render_template('timer.html', playlist_names=playlist_names, playlist_length=playlist_length, device_names=device_names, device_length=device_length)
	
@app.route('/tracks/topplaylist',  methods=['POST'])
def createTopPlaylist():
	"""
	Activates whenever the user saves a new playlist in which, creates 
	another new enity of playlists and stores new tracks.
	also when the user chooses to autoupdate the playlist, the ids are 
	stored into the data to be updated in the future 
	"""

	# save IDs in case user chose autoupdate
	playlist_id_short = None
	playlist_id_medium = None
	playlist_id_long = None
	playlist_uri = ''

	# create playlist, then get TopTracks, then fill playlist with TopTracks
	if 'short_term' in request.form:
		playlist_id_short, playlist_uri = createPlaylist(session, request.form['short_term_name'])
		uri_list = getTopTracksURI(session, 'short_term', 50)
		addTracksPlaylist(session, playlist_id_short, uri_list)

	if 'medium_term' in request.form:
		playlist_id_medium, playlist_uri =  createPlaylist(session, request.form['medium_term_name'])
		uri_list = getTopTracksURI(session, 'medium_term', 50)
		addTracksPlaylist(session, playlist_id_medium, uri_list)

	if 'long_term' in request.form:
		playlist_id_long, playlist_uri = createPlaylist(session, request.form['long_term_name'])
		uri_list = getTopTracksURI(session, 'long_term', 50)
		addTracksPlaylist(session, playlist_id_long, uri_list)

	# if user selects autoupdate, add them to the database
	if 'auto_update' in request.form:
		addUser(session['user_id'], session['refresh_token'], playlist_id_short=playlist_id_short, playlist_id_medium=playlist_id_medium, playlist_id_long=playlist_id_long)

	# send back the created playlist URI so the user is redirected to Spotify
	return playlist_uri

@app.route('/create/playlist',  methods=['POST'])
def createSelectedPlaylist():
	"""
	Activates when the user useses the create feature. The users 
	artist/track id before date, are gathered to fill playlist as well as 
	recomened tracks.
	"""
	# collect the IDs of the artists/tracks the user entered
	search = []
	for i in range(0, 5):
		if str(i) in request.form:
			search.append(request.form[str(i)])
		else:
			break

	# store all selected attributes in a dict which can be easily added to GET body
	tuneable_dict = {}
	if 'acoustic_level' in request.form:
		tuneable_dict.update({'acoustic': request.form['slider_acoustic']})

	if 'danceability_level' in request.form:
		tuneable_dict.update({'danceability': request.form['slider_danceability']})

	if 'energy_level' in request.form:
		tuneable_dict.update({'energy': request.form['slider_energy']})

	if 'popularity_level' in request.form:
		tuneable_dict.update({'popularity': request.form['slider_popularity']})

	if 'valence_level' in request.form:
		tuneable_dict.update({'valence': request.form['slider_valence']})

	playlist_id, playlist_uri = createPlaylist(session, request.form['playlist_name'])
	uri_list = getRecommendedTracks(session, search, tuneable_dict)
	addTracksPlaylist(session, playlist_id, uri_list)

	# send back the created playlist URI so the user is redirected to Spotify
	return playlist_uri
	
@app.route('/timer/start',  methods=['POST'])
def intervalStart():
	"""
	Activates when user uses the intervel timer,
	the user selected playlist is started with the timer.
	"""
	playlist = request.form['playlist']
	session['device'] = request.form['device']

	# toggle shuffle on/off depending on user
	is_shuffle = False
	if 'shuffle' in request.form:
		is_shuffle = True

	response = shuffle(session, session['device'], is_shuffle)

	# if the user does not have a premium account, this feature cannot be used
	if response == 403:
		abort(403)

	# if playback cannot be started on the selected device
	if response == 404:
		abort(404)


	response = startPlaybackContext(session, playlist, session['device'])
	if response == 403:
		abort(403)
	if response == 404:
		abort(404)

	# playback takes a while to start
	time.sleep(0.25)

	# return current track so picture and name can be displayed to user
	current_playing = getTrackAfterResume(session)
	return jsonify(current_playing)
	
@app.route('/autocomplete', methods=['GET'])
def autocomplete():
	"""
	Activates as the user types into search bar in the create feature
	it automatically finishes the statmnent for user an sends back possible 
	outcomes.
	"""
	search = request.args.get('q')
	results = searchSpotify(session, search)

	return jsonify(matching_results=results)

@app.route('/playback/skip')
def playbackSkip():
	"""
	Activates when song time is over it skips to the next song
	"""
	response = skipTrack(session)

	if response == 403:
		abort(403)
	if response == 404:
		abort(404)

	# return current track so picture and name can be displayed to user
	current_playing = getTrack(session)
	return jsonify(current_playing)
	
@app.route('/playback/pause')
def playbackPause():
	"""
	Activates when the user hits the pause button which, stops the
	song timer.
	"""
	response = pausePlayback(session)

	if response == 403:
		abort(403)
	if response == 404:
		abort(404)
	return "success"
	
@app.route('/playback/resume')
def playbackResume():
	"""
	Activates when the user has touched the pause button for a second time.
	"""
	response = startPlayback(session, session['device'])

	if response == 403:
		abort(403)
	if response == 404:
		abort(404)

	# return current track so picture and name can be displayed to user
	current_playing = getTrackAfterResume(session)
	return jsonify(current_playing)
