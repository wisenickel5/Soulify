from flask import current_app
import requests
import string as string
import time
import random as rand
import logging

def create_state_key(size):
	"""Provides a state key for authorization request. To prevent forgery attacks, the state key
	is used to make sure that the response comes from the same place that the request was sent from.
	Reference: https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
	
	Args:
		size (int): Determines the size of the State Key

	Returns:
		string: A randomly generated code with the length of the size parameter
	"""
	return ''.join(rand.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(size))

def get_token(code):
	"""Requests an access token from Spotify API. This function is only called if
	the current user does not have a refresh token.

	Args:
		code (string): Value returned from HTTP GET Request

	Returns:
		tuple(str, str, str) : Access Token, Refresh Token, Expiration Time
	"""	
	grant_type = current_app.config['GRANT_TYPE']
	redirect_uri = current_app.config['REDIRECT_URI']
	client_id = current_app.config['CLIENT_ID']
	client_secret = current_app.config['CLIENT_SECRET']
	token_url = current_app.config['TOKEN_URL']
	request_body = {
        "grant_type": grant_type,
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }
	post_request = requests.post(url=token_url, data=request_body)
	p_response = post_request.json()

	# Log POST Response output in terminal
	current_app.logger.debug(f"\n\nCurrent code {code}")
	current_app.logger.debug(f'\n\n(getToken) Post Response Status Code -> {post_request.status_code}')
	current_app.logger.debug(f'\n\nPost Response Formatted -> {post_request}\n\n')

	if post_request.status_code == 200:
		return p_response['access_token'], p_response['refresh_token'], p_response['expires_in']
	else:
		logging.error('getToken: ' + str(post_request.status_code))
		return None

def check_token_status(session):
	"""Determines if the new access token must be requested based on time expiration
	of previous token.

	Args:
		session (Session): Flask Session Object

	Returns:
		string: Success log
	"""
	payload = None
	if time.time() > session['token_expiration']:
		payload = refresh_token(session['refresh_token'])

	if payload is not None:
		session['token'] = payload[0]
		session['token_expiration'] = time.time() + payload[1]
	else:
		logging.error('checkTokenStatus')
		return None
	return "Success"

def refresh_token(token):
	"""
	POST Request is made to Spotify API with refresh token (only if access token and
	refresh token were previously acquired) creating a new access token

	Args:
		token (string)

	Returns:
		tuple(str, str): Access Token, Expiration Time
	"""
	token_url = 'https://accounts.spotify.com/api/token'
	authorization = current_app.config['AUTHORIZATION']

	headers = {'Authorization': authorization, 'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
	body = {'refresh_token': token, 'grant_type': 'refresh_token'}
	post_response = requests.post(token_url, headers=headers, data=body)

	# 200 code indicates access token was properly granted
	if post_response.status_code == 200:
		token = post_response.json()['access_token']
		exp_time = post_response.json()['expires_in']
		current_app.logger.info(f"Refresh Token: {token}\nExpiration time: {exp_time}")
		return token, exp_time
	else:
		logging.error('refreshToken:' + str(post_response.status_code))
		return None

def make_get_request(session, url, params={}):
	"""
	Recursively make GET Request to Spotify API with necessary headers
	until a status code that equals 200 is received or log the error.

	Args:
		session (Session): Flask Session Object
		url (string): URL
		params (dict, optional): Parameters being sent to API. Defaults to {}.

	Returns:
		dictionary: JSON Response
	"""
	headers = { 'Accept': 'application/json',
				'Content-Type': 'application/json',
				'Authorization': f"Bearer {session['token']}" }
	get_response = requests.get(url, headers=headers, params=params)

	# Log GET Response output in terminal
	current_app.logger.debug(f'\n\n(makeGetRequest) GET Response Status Code -> {get_response.status_code}')

	if get_response.status_code == 200:
		return get_response.json()
	elif get_response.status_code == 401 and check_token_status(session) is not None:
		return make_get_request(session, url, params)
	else:
		logging.error('makeGetRequests:' + str(get_response.status_code))
		return None

def make_put_request(session, url, params={}, data={}):
	"""
	Recursively make PUT Request to Spotify API with necessary headers
	until a status code that equals 204, 403, 404 is received or log the error.

	Args:
		session (Session): Flask Session Object
		url (string): URL
		params (dict, optional): Parameters being sent to API. Defaults to {}.
		data (dict, optional): Resource to be created or replaced. Defaults to {}.

	Returns:
		int: Status Code
	"""
	headers = {"Authorization": "Bearer {}".format(session['token']), 'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
	response = requests.put(url, headers=headers, params=params, data=data)

	# if request succeeds or specific errors occurred, status code is returned
	if response.status_code == 204 or response.status_code == 403 or response.status_code == 404 or response.status_code == 500:
		return response.status_code

	# if a 401 error occurs, update the access token
	elif response.status_code == 401 and check_token_status(session) is not None:
		return make_put_request(session, url, data)
	else:
		logging.error('makePutRequest:' + str(response.status_code))
		return None

def make_post_request(session, url, data):
	"""Recursively make POST Request to Spotify API with resource to be created
	until a status code that equals 201/204 is received or log the error.

	Args:
		session (Session): Flask Session Object
		url (string): URL
		data (dict): Resource to be created

	Returns:
		[type]: [description]
	"""
	headers = {"Authorization": "Bearer {}".format(session['token']), 'Accept': 'application/json', 'Content-Type': 'application/json'}
	response = requests.post(url, headers=headers, data=data)

	# both 201 and 204 indicate success, however only 201 responses have body information
	if response.status_code == 201:
		return response.json()
	if response.status_code == 204:
		return response

	# if a 401 error occurs, update the access token
	elif response.status_code == 401 and check_token_status(session) is not None:
		return make_post_request(session, url, data)
	elif response.status_code == 403 or response.status_code == 404:
		return response.status_code
	else:
		logging.error('makePostRequest:' + str(response.status_code))
		return None

def make_delete_request(session, url, data):
	"""
	Recursively make DELETE Request to Spotify API with resource to be deleted
	until a status code that equals 200 is received or log the error.

	Args:
		session (Session): Flask Session Object
		url (string): URL
		data (dict): Resource to be deleted

	Returns:
		dict : JSON Response
	"""
	headers = {"Authorization": "Bearer {}".format(session['token']), 'Accept': 'application/json', 'Content-Type': 'application/json'}
	response = requests.delete(url, headers=headers, data=data)

	# 200 code indicates request was successful
	if response.status_code == 200:
		return response.json()

	# if a 401 error occurs, update the access token
	elif response.status_code == 401 and check_token_status(session) is not None:
		return make_delete_request(session, url, data)
	else:
		logging.error('makeDeleteRequest:' + str(response.status_code))
		return None
