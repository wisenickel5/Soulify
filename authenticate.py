from main import app
import requests
import string as string
import time
import random as rand
import logging

def createStateKey(size):
	#https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
	return ''.join(rand.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(size))

def getToken(code):
        token_url = 'https://accounts.spotify.com/api/token'
        authorization = app.config['AUTHORIZATION']
        redirect_uri = app.config['REDIRECT_URI']

        headers = { 'Authorization': authorization,
                'Accept': 'Soulify/json',
                'Content-Type': 'application/x-www-form-urlencoded'}
        body = {'code': code, 'redirect_uri': redirect_uri,
                'grant-type': 'authorization_code'}

        post_response = requests.post(token_url, headers=headers, data=body)

        if post_response.status_code == 200:
                pr = post_response.json()
                return pr['access_token'], pr['refresh_token'], pr['expires_in']
        else:
                logging.error('getToken: ' + str(post_response.status_code))
                return None

def checkTokenStatus(session):
        if time.time() > session['token_expiration']:
                payload = refreshToken(session['refresh_token'])

        if payload != None:
                session['token'] = payload[0]
                session['token_expiration'] = time.time() + payload[1]
        else:
                logging.error('checkTokenStatus')
                return None
        return "Success"

def refreshToken(refresh_token):
	token_url = 'https://accounts.spotify.com/api/token'
	authorization = app.config['AUTHORIZATION']

	headers = {'Authorization': authorization, 'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
	body = {'refresh_token': refresh_token, 'grant_type': 'refresh_token'}
	post_response = requests.post(token_url, headers=headers, data=body)

	# 200 code indicates access token was properly granted
	if post_response.status_code == 200:
		return post_response.json()['access_token'], post_response.json()['expires_in']
	else:
		logging.error('refreshToken:' + str(post_response.status_code))
		return None

def makeGetRequest(session, url, params={}):
        headers = {'Authorization': "Bearer {}".format(session['token'])}
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
                return response.json()
        elif response.status_code == 401 and checkTokenStatus(session) != None:
                return makeGetRequest(session, url, params)
        else:
                logging.error('makeGetRequests:' + str(response.status_code))
                return None

def makePutRequest(session, url, params={}, data={}):

	headers = {"Authorization": "Bearer {}".format(session['token']), 'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
	response = requests.put(url, headers=headers, params=params, data=data)

	# if request succeeds or specific errors occured, status code is returned
	if response.status_code == 204 or response.status_code == 403 or response.status_code == 404 or response.status_code == 500:
		return response.status_code

	# if a 401 error occurs, update the access token
	elif response.status_code == 401 and checkTokenStatus(session) != None:
		return makePutRequest(session, url, data)
	else:
		logging.error('makePutRequest:' + str(response.status_code))
		return None

def makePostRequest(session, url, data):

	headers = {"Authorization": "Bearer {}".format(session['token']), 'Accept': 'application/json', 'Content-Type': 'application/json'}
	response = requests.post(url, headers=headers, data=data)

	# both 201 and 204 indicate success, however only 201 responses have body information
	if response.status_code == 201:
		return response.json()
	if response.status_code == 204:
		return response

	# if a 401 error occurs, update the access token
	elif response.status_code == 401 and checkTokenStatus(session) != None:
		return makePostRequest(session, url, data)
	elif response.status_code == 403 or response.status_code == 404:
		return response.status_code
	else:
		logging.error('makePostRequest:' + str(response.status_code))
		return None

def makeDeleteRequest(session, url, data):
	headers = {"Authorization": "Bearer {}".format(session['token']), 'Accept': 'application/json', 'Content-Type': 'application/json'}
	response = requests.delete(url, headers=headers, data=data)

	# 200 code indicates request was successful
	if response.status_code == 200:
		return response.json()

	# if a 401 error occurs, update the access token
	elif response.status_code == 401 and checkTokenStatus(session) != None:
		return makeDeleteRequest(session, url, data)
	else:
		logging.error('makeDeleteRequest:' + str(response.status_code))
		return None
