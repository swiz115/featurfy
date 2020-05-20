"""Database API."""
import sqlite3
import flask
import featurfy
import requests
import six
import base64
import time


def dict_factory(cursor, row):
    """Convert database row objects to a dictionary.

    This is useful for building dictionaries which
    are then used to render a template.
    Note that this would be inefficient for large queries.
    """
    output = {}
    for idx, col in enumerate(cursor.description):
        output[col[0]] = row[idx]
    return output


def get_db():
    """Open a new database connection."""
    if not hasattr(flask.g, 'sqlite_db'):
        flask.g.sqlite_db = sqlite3.connect(
            featurfy.app.config['DATABASE_FILENAME'])
        flask.g.sqlite_db.row_factory = dict_factory

        # Foreign keys have to be enabled per-connection.  This is an sqlite3
        # backwards compatibility thing.
        flask.g.sqlite_db.execute("PRAGMA foreign_keys = ON")

    return flask.g.sqlite_db


@featurfy.app.teardown_appcontext
def close_db(error):
    """Close the database at the end of a request."""
    # Assertion needed to avoid style error
    assert error or not error
    if hasattr(flask.g, 'sqlite_db'):
        flask.g.sqlite_db.commit()
        flask.g.sqlite_db.close()


def getTokens(code):
  '''
    This function retrives a access token and refresh token 

    :param code: a string that is used to allow request for a access token
    :return: dictionary with access token and refresh token 
  '''
  spotifyTokenUrl = 'https://accounts.spotify.com/api/token'
  
  headers = makeAuthorizationHeaders()
  payload = {
    'redirect_uri': featurfy.app.config['REDIRECT_URI'],
    'code': code,
    'grant_type': 'authorization_code',
    # 'scope': scopes
  }
  response = requests.post(spotifyTokenUrl, headers=headers, data=payload)
  if response.status_code != 200:
    return 'error'
  tokenInfo = response.json()
  return tokenInfo

def makeAuthorizationHeaders():
  '''
    This function creates a header that is needed for getting access and request tokens 

    :return: a dictionary with a formated header 
  '''
  encodedIds = base64.b64encode(
    six.text_type(featurfy.app.config['CLIENT_ID'] + ':' + featurfy.app.config['CLIENT_SECRET']).encode('ascii')
  )
  return {'Authorization': 'Basic %s' % encodedIds.decode('ascii')}

def makeRequestEndpointHeaders(token):
  '''
    This function creates a header that is needed for requesting data from a users account

    :param token: a access token that is not expired
    :return: a dictionary with a formated header 
  '''
  return {'Authorization': 'Bearer {0}'.format(token)}


def refresh_access_tokens(refresh_token, username):
  '''
    This function gets a new access token with the refresh token and updates the users access token after 

    :param refresh_token: a refresh token
    :param username: a users username
    :return:
  '''
  spotifyTokenUrl = 'https://accounts.spotify.com/api/token'
  headers = makeAuthorizationHeaders()
  headers['Content-type'] = 'application/x-www-form-urlencoded'
  body = {'grant_type': 'refresh_token', 'refresh_token': refresh_token}

  response = requests.post(spotifyTokenUrl, headers=headers, data=body)
  data = response.json()
  # SQL update on access token and token_expire
  access_token_expire = int(time.time()) + data['expires_in']
  get_db().cursor().execute('UPDATE users SET access_token=?, token_expire=? WHERE username=?', \
                              [data['access_token'], access_token_expire, username])

  return 

def check_valid_access_tokens(username):
  '''
    This function checks whether the access token has expired

    :param username: a users username
    :return:
  '''
  query = get_db().cursor().execute('SELECT token_expire, access_token, refresh_token FROM users WHERE username=?',[username]).fetchall()
  if not query:
    return False

  # Access token has expired, refresh it with refresh token
  if query[0]['token_expire'] <= int(time.time()):
    refresh_access_tokens(query[0]['refresh_token'], username)

  return True









