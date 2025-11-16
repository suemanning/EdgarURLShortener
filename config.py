"""
Configuration file for URL Shortener
"""

# Server Configuration
HOST = '0.0.0.0'
PORT = 5001
DEBUG = True

# URL Configuration
BASE_URL = 'http://localhost:5001'  # Change this to your production domain
SHORT_CODE_LENGTH = 6  # Length of generated short codes

# Storage Configuration
DATA_FILE = 'urls.json'  # File to store URL mappings

# For production, you might want to use environment variables:
# import os
# BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5001')
# PORT = int(os.environ.get('PORT', 5001))
