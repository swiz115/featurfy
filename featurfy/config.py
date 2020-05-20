"""Development configuration."""

import os

# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = '/'

# Secret key for encrypting cookies
SECRET_KEY = ''

SESSION_COOKIE_NAME = 'login'

# Client Keys
CLIENT_ID = ''
CLIENT_SECRET = ''
SCOPE = 'user-read-private user-read-email user-library-read playlist-modify-public playlist-modify-public user-follow-read'
REDIRECT_URI = 'http://localhost:8000/callback/'

# File Upload to var/uploads/
UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    'var', 'uploads'
)
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Database file is var/featurfy.sqlite3
DATABASE_FILENAME = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    'var', 'featurfy.sqlite3'
)
