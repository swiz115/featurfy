# Featurfy

## Overview
Featurfy is a web app that allows Spotify users to explore a variety of small applications built using Spotify's Web API. Each feature isn't big enough to be an independent application, so I decided to create a platform for them. This is an ongoing project that will have new features released periodically!
<br />
<br />
Visit here: [Featurfy](http://www.featurfy.org/)
## Features
### Audio Feature Playlist
This feature allows users to filter their Spotify liked songs by genre, bpm, valence, energy, and danceability. This feature also allows users to create a playlist as they explore the different filters. 
### Unpopular Artist Finder
This feature allows users to discover unpopular artists to follow that are related to their favorite artists. 
## Run Locally
```
git clone https://github.com/smithjosh115/featurfy
cd featurfy
```
Set your CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, and SECRET_KEY in ```config.py```.
To create a SECRET_KEY run ```python3 -c 'import os; print(os.urandom(24))'```
```
python3 -m venv env
source env/bin/activate
pip install -e .
mkdir var
./bin/featurfydb create
./bin/featurfyrun
```
