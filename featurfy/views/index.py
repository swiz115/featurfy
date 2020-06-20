'''Featurfy url routing/user authentication'''
import urllib
import flask
from flask import request
import featurfy
from featurfy.model import get_db, getTokens, makeAuthorizationHeaders, makeRequestEndpointHeaders, check_valid_access_tokens, consistant_session
import json
import time
import requests

# Client Keys
CLIENT_ID = featurfy.app.config['CLIENT_ID']
CLIENT_SECRET = featurfy.app.config['CLIENT_SECRET']

#Spotify URLS
SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_API_URL = 'https://api.spotify.com/v1'

#Server-side Parameters
REDIRECT_URI = featurfy.app.config['REDIRECT_URI']
SCOPE = featurfy.app.config['SCOPE']
SHOW_DIALOG = 'true'

@featurfy.app.route('/', methods=['GET',])
def get_index():
    '''
    Index route: 
    This brings user to index template
    '''
    if 'username' not in flask.session or not consistant_session(flask.session['username']):
        return flask.redirect(flask.url_for('logout'))

    if request.method == 'GET':
        return flask.render_template('index.html')

    else:
        flask.abort(404) 

@featurfy.app.route('/callback/', methods=['GET',])
def spotify_callback():
    '''
    Callback route:
    This is the route the Spotify API calls back to after user accepts or declines access to their account
    '''
    if 'error' in request.args or 'code' not in request.args:
        return flask.redirect(flask.url_for('get_index'))

    token_info = getTokens(request.args['code'])
    if token_info == 'error':
        return flask.redirect(flask.url_for('get_index'))

    headers = makeRequestEndpointHeaders(token_info['access_token'])

    response = requests.get(SPOTIFY_API_URL + '/me', headers=headers)
    data = response.json()
    if 'error' in data:
        return flask.redirect(flask.url_for('get_index'))

    flask.session['username'] = data['display_name']
    # A new session is created. Check if this is a returning user or not. if new user: add to database, else: update access and refresh tokens
    query = get_db().cursor().execute('SELECT username, token_expire FROM users WHERE username=?',[data['display_name']]).fetchall()
    if not query:
        access_token_expire = int(time.time()) + token_info['expires_in']
        get_db().cursor().execute('INSERT INTO users(username, access_token, refresh_token, token_expire) VALUES(?, ?, ?, ?)', \
                                    [data['display_name'], token_info['access_token'], token_info['refresh_token'], access_token_expire])
    elif query[0]['token_expire'] <= int(time.time()):
      '''
      If session expires, user gets new access and refresh token, however if this is a previous user the 
      access and refresh token could still be valid so only update if the access token has expired. 
      '''
      access_token_expire = int(time.time()) + token_info['expires_in']
      get_db().cursor().execute('UPDATE users SET access_token=?, refresh_token=?, token_expire=? WHERE username=?', \
                                    [token_info['access_token'], token_info['refresh_token'], access_token_expire, data['display_name']])


    return flask.redirect(flask.url_for('get_index'))

@featurfy.app.route('/audiofeat/', methods=['GET',])
def audiofeat():
    '''
    Audio feature route:
    This route brings user to Audio feature template
    '''
    if 'username' not in flask.session or not consistant_session(flask.session['username']):
        return flask.redirect(flask.url_for('logout'))

    if request.method == 'GET':
        # Check access tokens
        check_valid_access_tokens(flask.session['username'])
        return flask.render_template('audiofeat.html')
    else:
        flask.abort(404)


@featurfy.app.route('/artistfinder/', methods=['GET',])   
def artistfinder():
    '''
    Artist Finder route:
    This route brings user to Artist Finder template
    '''
    if 'username' not in flask.session or not consistant_session(flask.session['username']):
        return flask.redirect(flask.url_for('logout'))

    if request.method == 'GET':
        # Check access tokens
        check_valid_access_tokens(flask.session['username'])
        return flask.render_template('artistfinder.html')
    else:
        flask.abort(404)

@featurfy.app.route('/logout/', methods=['GET',])
def logout():
    '''
    Logout route:
    This route logs out a user and routes them back to the index route 
    '''
    flask.session.clear()
    return flask.redirect(flask.url_for('login'))

@featurfy.app.route('/login/', methods=['GET','POST',])
def login():
    '''
    Login route:
    This route logs in a user and routes them to the index route 
    '''
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('get_index'))

    if request.method == 'GET':
        return flask.render_template('login.html')
        
    elif request.method == 'POST':
        auth_query_parameters = {
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'scope': SCOPE,
            'show_dialog': SHOW_DIALOG,
            'client_id': CLIENT_ID
        }
        url_args = '&'.join(['{}={}'.format(key,urllib.parse.quote(val)) for key,val in auth_query_parameters.items()])
        auth_url = '{}/?{}'.format(SPOTIFY_AUTH_URL, url_args)

        return flask.redirect(auth_url)

    else:
        flask.abort(404)
