# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is a Flask-based URL shortener API designed for internal use by the Edgar project. It consists of:

- **app.py**: Main Flask API server with 5 endpoints - shorten URLs, redirect, get stats, list URLs, and delete URLs
- **client.py**: Python client library providing a clean interface for the Edgar project to interact with the API
- **config.py**: Centralized configuration (host, port, BASE_URL, short code length, data file path)
- **test_api.py**: Comprehensive test suite for all API functionality

The application uses JSON file storage (urls.json) for persistence. The architecture separates internal API endpoints (/api/*) from external redirect endpoints (/<short_code>).

## Common Development Commands

### Running the Application
```bash
# Start the development server
python app.py

# Change port if 5000 is in use - edit config.py PORT value first
python app.py
```

### Testing
```bash
# Run the test suite (requires server to be running)
python test_api.py

# Test the client library directly
python client.py
```

### Dependencies
```bash
# Install requirements
pip install -r requirements.txt
```

### Production Deployment
```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Using uWSGI
pip install uwsgi
uwsgi --http :5000 --wsgi-file app.py --callable app --processes 4
```

## Configuration

All configuration is centralized in config.py:
- Change BASE_URL for different environments
- Adjust PORT if 5000 conflicts
- Modify SHORT_CODE_LENGTH for different code lengths
- Update DATA_FILE path for different storage locations

For production, use environment variables as shown in the commented section of config.py.

## Data Flow

1. **URL Shortening**: POST /api/shorten checks for existing URLs before generating new short codes
2. **Redirection**: GET /<short_code> increments click counter and redirects
3. **Storage**: All data persists to urls.json with atomic writes
4. **Client Library**: Provides typed interface with error handling for Edgar project integration

The system prevents duplicate short codes through existence checking and reuses existing codes for the same original URL.