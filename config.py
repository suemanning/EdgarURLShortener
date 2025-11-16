"""
Configuration file for URL Shortener
"""

import os

# Server Configuration
HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', 5001))
DEBUG = os.environ.get('FLASK_ENV') != 'production'

# URL Configuration - uses environment variable for production
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5001')
SHORT_CODE_LENGTH = 6  # Length of generated short codes

# Storage Configuration
DATABASE_PATH = 'urls.db'  # SQLite database file
