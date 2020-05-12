# Featurfy

## Overview
Featurfy is a web app that allows Spotify users to explore a variety of features built using Spotify's Web API. This is an ongoing project that will have new features released monthly!
<br />
<br />
Visit here: [Featurfy](http://www.featurfy.org/)
## Features
### Audio Feature Playlist
This feature allows users to filter their Spotify liked songs by genre, bpm, valence, energy, and danceability. This feature also allows users to create a playlist as they explore the different filters. 
## Run Locally
```
git clone https://github.com/smithjosh115/featurfy
cd featurfy
'''
Set your CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, and SECRET_KEY in '''config.py'''
To create a SECRET_KEY run '''python3 -c 'import os; print(os.urandom(24))''''
'''
python3 -m venv env
source env/bin/activate
pip install -e .
./bin/featurfydb create
./bin/featurfyrun
```
