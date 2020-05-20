#Auto Feat API
import flask
import json
import featurfy
import requests
from featurfy.model import get_db, makeRequestEndpointHeaders, check_valid_access_tokens

SPOTIFY_API_URL = 'https://api.spotify.com/v1'


@featurfy.app.route('/api/v1/createbpmplaylist/', methods=['POST','GET'])
def audio_feat_playlist():
    '''
    Audio Feat playlist route:
    GET: Retrives all users saved songs and audio features of each track 
    POST: Create playlist of given tracks 
    '''
    if 'username' not in flask.session:
        # Session expired redirect to index page
        return flask.make_response(flask.jsonify({}), 401) 

    # GET: Retrives all users saved songs and audio features of each track 
    if flask.request.method == 'GET':
        genre_dic = {}
        genre_list = []
        saved_tracks_dic = {}
        saved_tracks_list = []
        saved_artist_dic = {}
        saved_artist_no_duplicates = []
        audio_features_endpoint = SPOTIFY_API_URL + '/audio-features'
        saved_tracks_endpoint = SPOTIFY_API_URL + '/me/tracks?limit=50'
        artists_endpoint = SPOTIFY_API_URL + '/artists'

        # Implement function to check if the access token is expired. If the access token is expired here we need to update it and use the new one
        check_valid_access_tokens(flask.session['username'])
        query = get_db().cursor().execute('SELECT access_token FROM users WHERE username=?',[flask.session['username']]).fetchall()
        headers = makeRequestEndpointHeaders(query[0]['access_token'])

        artist_ids_dic = {'ids': ''}
        artist_ids_count = 0
        saved_tracks_ids = {'ids': ''}
        saved_tracks_ids_count = 0

        while(True):
            saved_tracks_response = requests.get(saved_tracks_endpoint, headers=headers)
            saved_tracks_data = saved_tracks_response.json()
            
            if 'error' in saved_tracks_data:
                print(saved_tracks_data)
                return flask.make_response(flask.jsonify({}), 500)

            for track_obj in saved_tracks_data['items']:
                saved_tracks_list.append(track_obj['track']['id'])
                saved_tracks_ids['ids'] = saved_tracks_ids['ids'] + track_obj['track']['id'] + ','
                artist_id = track_obj['track']['artists'][0]['id']
                # Get all artist's names for a single track 
                track_artists = []
                for artist_obj in track_obj['track']['artists']:
                    track_artists.append(artist_obj['name'])
                # Create map of track ids to genre/bpm/valence/danceability/energy/track name/track artists
                saved_tracks_dic[track_obj['track']['id']] = {
                    'name': track_obj['track']['name'], 
                    'artists': track_artists,
                    'genres': [], 
                    'bpm': 0, 
                    'valence': 0, 
                    'danceability': 0, 
                    'energy': 0
                }
                # Create map of artists to list of tracks and list of unique artist id strings with 50 ids that are used in a query string later
                if saved_artist_dic.get(artist_id) == None:
                    saved_artist_dic[artist_id] = []
                    # Add artist id strings once we have a string of 50 unique ids
                    if artist_ids_count == 50:
                        saved_artist_no_duplicates.append(artist_ids_dic)
                        artist_ids_dic = {'ids': ''}
                        artist_ids_count = 0
                    artist_ids_count += 1
                    artist_ids_dic['ids'] = artist_ids_dic['ids'] + artist_id + ','
                saved_artist_dic[artist_id].append(track_obj['track']['id'])

                saved_tracks_ids_count += 1
            # Add remaing unique artist id strings
            if artist_ids_count > 0:
                saved_artist_no_duplicates.append(artist_ids_dic)
                artist_ids_dic = {'ids': ''}
                artist_ids_count = 0

            if saved_tracks_ids_count == 100: 
                # Trim ending comma
                saved_tracks_ids['ids'] = saved_tracks_ids['ids'][:-1]
               
                audio_response = requests.get(audio_features_endpoint, headers=headers, params=saved_tracks_ids)
                audio_response_data = audio_response.json()

                if 'error' in audio_response_data:
                    print(audio_response_data)
                    return flask.make_response(flask.jsonify({}), 500)
                
                # Add BPM to tracks
                for track in audio_response_data['audio_features']:
                    # Handle if no audio features for a track. This usually occues if the song was recently released and Spotify hasn't gathered audio data yet
                    # Fixes TypeError: 'NoneType' object is not subscriptable: Was getting this because Drakes new album I saved didn't have audio data yet 
                    if track == None:
                        continue
                    saved_tracks_dic[track['id']]['bpm'] = track['tempo']
                    saved_tracks_dic[track['id']]['valence'] = track['valence']
                    saved_tracks_dic[track['id']]['danceability'] = track['danceability']
                    saved_tracks_dic[track['id']]['energy'] = track['energy']
                saved_tracks_ids = {'ids': ''}
                saved_tracks_ids_count = 0
        
            if saved_tracks_data['next'] == None:
                break
                
            saved_tracks_endpoint = saved_tracks_data['next']
      
        if saved_tracks_ids_count > 0:
            # Trim ending comma
            saved_tracks_ids['ids'] = saved_tracks_ids['ids'][:-1]
            audio_response = requests.get(audio_features_endpoint, headers=headers, params=saved_tracks_ids)
            audio_response_data = audio_response.json()

            if 'error' in audio_response_data:
                print(audio_response_data)
                return flask.make_response(flask.jsonify({}), 500)
            # Add BPM to reamaining tracks 
            for track in audio_response_data['audio_features']:
                # Handle if no audio features for a track. This usually occues if the song was recently released and Spotify hasn't gathered audio data yet
                if track == None:
                    continue

                saved_tracks_dic[track['id']]['bpm'] = track['tempo']
                saved_tracks_dic[track['id']]['valence'] = track['valence']
                saved_tracks_dic[track['id']]['danceability'] = track['danceability']
                saved_tracks_dic[track['id']]['energy'] = track['energy']
            saved_tracks_ids = {'ids': ''}
            saved_tracks_ids_count = 0

        # Get list of genres of users saved songs 
        for obj in saved_artist_no_duplicates:
            # Trim ending comma
            obj['ids'] = obj['ids'][:-1]
            artists_response = requests.get(artists_endpoint, headers=headers, params=obj)
            artists_response_data = artists_response.json()

            if 'error' in artists_response_data:
                print(artists_response_data)
                return flask.make_response(flask.jsonify({}), 500)

            for artist in artists_response_data['artists']:
                for track in saved_artist_dic[artist['id']]:
                    saved_tracks_dic[track]['genres'] = artist['genres']
                    for genre in artist['genres']:
                        if genre_dic.get(genre) == None:
                            genre_dic[genre] = True
                            genre_list.append(genre)


        genre_list.sort()
        return flask.make_response(flask.jsonify({'saved_tracks_dic': saved_tracks_dic , 'saved_tracks_list': saved_tracks_list, 'genre_list': genre_list, 'genre_dic': genre_dic}), 200)

    # POST: Create playlist of given tracks 
    elif flask.request.method == 'POST':
        content = flask.request.json

        # Implement function to check if the access token is expired. If the access token is expired here we need to update it and use the new one
        check_valid_access_tokens(flask.session['username'])
        query = get_db().cursor().execute('SELECT access_token FROM users WHERE username=?',[flask.session['username']]).fetchall()
        headers = makeRequestEndpointHeaders(query[0]['access_token'])

        response = requests.get(SPOTIFY_API_URL + '/me', headers=headers)
        data = response.json()

        body = {'name': content['name']}
        headers['Content-type'] = 'application/json'
        response = requests.post(SPOTIFY_API_URL + '/users/{}/playlists'.format(data['id']), headers=headers, data=json.dumps(body))
        data = response.json()

        if 'error' in data:
            print(data)
            return flask.make_response(flask.jsonify({}), 500)

        created_playlist_id = data['id']
        body = []
        for track_id in content['tracks']:
            if len(body) == 100:
                response = requests.post(SPOTIFY_API_URL + '/playlists/{}/tracks'.format(created_playlist_id), headers=headers, data=json.dumps(body))
                body = []
            body.append('spotify:track:' + track_id)

        if len(body) > 0:
            response = requests.post(SPOTIFY_API_URL + '/playlists/{}/tracks'.format(created_playlist_id), headers=headers, data=json.dumps(body))
            body = []

        return flask.make_response(flask.jsonify({}), 201)

    return flask.make_response(flask.jsonify({}), 405) 


