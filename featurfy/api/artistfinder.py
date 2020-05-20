#Artist Finder API
import flask
import json
import featurfy
import requests
from featurfy.model import get_db, makeRequestEndpointHeaders, check_valid_access_tokens

SPOTIFY_API_URL = 'https://api.spotify.com/v1'

@featurfy.app.route('/api/v1/searchartist/<search>/', methods=['GET',])
def search_artist(search):
    '''
    Search artist route:
    POST: Performs a search for artists with a provided string
    '''
    if 'username' not in flask.session:
        #session expired redirect to index page
        return flask.make_response(flask.jsonify({}), 401) 

    # POST: Performs a search for artists with a string sent in request
    if flask.request.method == 'GET':
        search_artist_endpoint = SPOTIFY_API_URL + '/search'
        search_artist_params = {'q': search, 'limit': 50, 'type': 'artist'}
        # Implement function to check if the access token is expired. If the access token is expired here we need to update it and use the new one
        check_valid_access_tokens(flask.session['username'])
        query = get_db().cursor().execute('SELECT access_token FROM users WHERE username=?',[flask.session['username']]).fetchall()
        headers = makeRequestEndpointHeaders(query[0]['access_token'])

        search_artist_response = requests.get(search_artist_endpoint, headers=headers, params=search_artist_params)
        search_artist_data = search_artist_response.json()

        if 'error' in search_artist_data:
            return flask.make_response(flask.jsonify({}), 500) 

        artist_matches = []
        for artist in search_artist_data['artists']['items']:
            # print(artist['name'] +': ' + artist['id'])
            artist_matches.append({'name': artist['name'], 'id': artist['id'], 'images': artist['images']})

        return flask.make_response(flask.jsonify({'artists': artist_matches}), 200)

    return flask.make_response(flask.jsonify({}), 405) 


@featurfy.app.route('/api/v1/relatedartist/<artist_id>/', methods=['GET',])
def related_artist(artist_id):
    '''
    Search artist route:
    GET: Performs a search for unpopular artists related to single artist 
    '''
    if 'username' not in flask.session:
        #session expired redirect to index page
        return flask.make_response(flask.jsonify({}), 401) 

    # GET: Performs a search for unpopular artists related to single artist 
    if flask.request.method == 'GET':
        related_artist_endpoint = SPOTIFY_API_URL + '/artists/{}/related-artists'
        follow_artist_endpoint = SPOTIFY_API_URL + '/me/following/contains'
        # Implement function to check if the access token is expired. If the access token is expired here we need to update it and use the new one
        check_valid_access_tokens(flask.session['username'])
        query = get_db().cursor().execute('SELECT access_token FROM users WHERE username=?',[flask.session['username']]).fetchall()
        headers = makeRequestEndpointHeaders(query[0]['access_token'])

        related_artist_response = requests.get(related_artist_endpoint.format(artist_id), headers=headers)
        related_artist_data = related_artist_response.json()


        related_artist_dic = {}
        related_artist_list = []

        for artist in related_artist_data['artists']:
            related_artist_list.append(artist['id'])
            related_artist_dic[artist['id']] = {
                'name': artist['name'],
                'images': artist['images'],
                'popularity': artist['popularity'],
                'uri': artist['uri']
            }

        related_artist_list_copy = related_artist_list.copy()
        for artist in related_artist_list_copy:
            more_related_artist_response = requests.get(related_artist_endpoint.format(artist), headers=headers)
            more_related_artist_data = more_related_artist_response.json()

            for more_related_artist in more_related_artist_data['artists']:
                if related_artist_dic.get(more_related_artist['id']) == None:
                    related_artist_dic[more_related_artist['id']] = {
                        'name': more_related_artist['name'],
                        'images': more_related_artist['images'],
                        'popularity': more_related_artist['popularity'],
                        'uri': more_related_artist['uri']
                    }
                    related_artist_list.append(more_related_artist['id'])

        list_min = 0
        follow_artist_ids = related_artist_list[list_min:list_min + 50]
        while follow_artist_ids:
            comma_seperate_ids = ','.join(follow_artist_ids)
            follow_artist_response = requests.get(follow_artist_endpoint, headers=headers, params={'ids': comma_seperate_ids, 'type': 'artist'})
            follow_artist_data = follow_artist_response.json()
            for idx, val in enumerate(follow_artist_data):
                related_artist_dic[follow_artist_ids[idx]]['follow'] = val
            list_min += 50 
            follow_artist_ids = related_artist_list[list_min:list_min + 50]

        return flask.make_response(flask.jsonify({'related_artist_dic': related_artist_dic, 'related_artist_list': related_artist_list}), 200)


    return flask.make_response(flask.jsonify({}), 405) 





