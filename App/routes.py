import logging
import time

# Flask Imports
from flask import (jsonify, make_response,
                   redirect, render_template,
                   request, session)

# Local Imports
from App.spotify.authenticate import create_state_key, get_token
from flask import current_app
from App import app

from App.spotify.api_handler import SpotifyAPIHandler
from App.spotify.data_processing import DataProcessing
from App.spotify.user_operations import (add_user, get_user_information)

SAPI = SpotifyAPIHandler(session)


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
    client_id = current_app.config['CLIENT_ID']
    redirect_uri = current_app.config['REDIRECT_URI']
    scope = current_app.config['SCOPE']

    # state key used to protect against cross-site forgery attacks
    state_key = create_state_key(15)
    session['state_key'] = state_key

    # redirect user to Spotify authorization page
    authorize_url = 'https://accounts.spotify.com/en/authorize?'
    parameters = ('client_id=' + client_id + '&response_type=code' + '&redirect_uri=' +
                  redirect_uri + '&scope=' + scope + '&state=' + state_key)
    current_app.logger.info(authorize_url + parameters)
    response = make_response(redirect(authorize_url + parameters))

    return response


@app.route('/callback')
def callback():
    """
    Called after a new user has authorized the application through the Spotify API page.
    Stores user information in a session and redirects user back to the page they initially
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
        payload = get_token(code)
        # app.logger.info(f'(Callback) Payload: {payload}')
        if payload is not None:
            session['token'] = payload[0]
            session['refresh_token'] = payload[1]
            session['token_expiration'] = time.time() + payload[2]
        else:
            return render_template('index.html', error='Failed to access token.')

    current_user = get_user_information(session)
    session['user_id'] = current_user['id']
    logging.info('new user:' + session['user_id'])
    return redirect(session['previous_url'])


@app.route('/information', methods=['GET'])
def information():
    """
    This page displays policies and information about the
    features on the app.
    """
    return render_template('information.html')


@app.route('/tracks', methods=['GET'])
def tracks():
    """
    This page shows most played tracks by the user over multiple
    time periods.
    """

    # make sure application is authorized for user
    if session.get('token') is None or session.get('token_expiration') is None:
        session['previous_url'] = '/tracks'
        return redirect('/authorize')

    # collect user information
    if session.get('user_id') is None:
        current_user = get_user_information(session)
        session['user_id'] = current_user['id']

    top_track_ids = SAPI.get_all_top_tracks()
    # if top_track_ids == None:
    # return render_template('index.html', error='Failed to gather top tracks.')

    liked_track_ids = SAPI.get_liked_track_ids()
    if liked_track_ids is None:
        return render_template('index.html', error='Failed to get liked tracks')
    elif liked_track_ids is not None:
        dp = DataProcessing(liked_track_ids)
        lt_df = dp.liked_track_ids_df()
        music_attributes = dp.normalize_df(lt_df)
        dp.create_radar_chart(music_attributes)

    return render_template('tracks.html', track_ids=top_track_ids)


@app.route('/create', methods=['GET'])
def create():
    """
    This feature allows the user to create a
    playlist by searching song title/artist.
    """
    # make sure application is authorized for user
    if session.get('token') is None or session.get('token_expiration') is None:
        session['previous_url'] = '/create'
        return redirect('/authorize')

    # collect user information
    if session.get('user_id') is None:
        current_user = get_user_information(session)
        session['user_id'] = current_user['id']

    return render_template('create.html')


@app.route('/project', methods=['GET'])
def project():
    """
    This page displays policies and information about the
    features on the app.
    """
    return render_template('project.html')


@app.route('/tracks/topplaylist', methods=['POST'])
def create_top_playlist():
    """
    Activates whenever the user saves a new playlist in which, creates
    another new entity of playlists and stores new tracks.
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
        playlist_id_short, playlist_uri = SAPI.create_playlist(request.form['short_term_name'])
        uri_list = SAPI.get_top_tracks_uri('short_term', 50)
        SAPI.add_tracks_playlist(playlist_id_short, uri_list)

    if 'medium_term' in request.form:
        playlist_id_medium, playlist_uri = SAPI.create_playlist(request.form['medium_term_name'])
        uri_list = SAPI.get_top_tracks_uri('medium_term', 50)
        SAPI.add_tracks_playlist(playlist_id_medium, uri_list)

    if 'long_term' in request.form:
        playlist_id_long, playlist_uri = SAPI.create_playlist(request.form['long_term_name'])
        uri_list = SAPI.get_top_tracks_uri('long_term', 50)
        SAPI.add_tracks_playlist(playlist_id_long, uri_list)

    # if user selects autoupdate, add them to the database
    if 'auto_update' in request.form:
        add_user(session['user_id'], session['refresh_token'], playlist_id_short=playlist_id_short,
                 playlist_id_medium=playlist_id_medium, playlist_id_long=playlist_id_long)

    # send back the created playlist URI so the user is redirected to Spotify
    return playlist_uri


@app.route('/create/playlist', methods=['POST'])
def create_selected_playlist():
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

    playlist_id, playlist_uri = SAPI.create_playlist(request.form['playlist_name'])
    uri_list = SAPI.get_recommended_tracks(search, tuneable_dict)
    SAPI.add_tracks_playlist(playlist_id, uri_list)

    # send back the created playlist URI so the user is redirected to Spotify
    return playlist_uri


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    """
    Activates as the user types into search bar in the create feature
    it automatically finishes the statement for user and sends back possible
    outcomes.
    """
    search = request.args.get('q')
    results = SAPI.search_spotify(search)

    return jsonify(matching_results=results)
