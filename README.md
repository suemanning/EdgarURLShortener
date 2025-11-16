# URL Shortener - Edgar Project

A simple, lightweight URL shortener API designed for internal use by the Edgar project. The shortened links can be shared externally and will redirect to the original URLs.

## Features

- **API-Only**: No web interface, designed for programmatic access
- **Simple Integration**: Python client library included
- **Persistent Storage**: URLs stored in JSON file
- **Click Tracking**: Track how many times each shortened URL is accessed
- **Duplicate Detection**: Reuses existing short codes for the same URL
- **Easy Deployment**: Single Flask application

## Project Structure

```
url_shortener/
├── app.py              # Main Flask API server
├── client.py           # Python client library for Edgar project
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── urls.json           # URL storage (created automatically)
└── README.md           # This file
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure the Application

Edit `config.py` to set your domain:

```python
BASE_URL = 'https://yourdomain.com'  # Your production domain
```

### 3. Run the Server

```bash
python app.py
```

The server will start on `http://localhost:5000` by default.

## API Endpoints

### Shorten a URL (Internal)

**POST** `/api/shorten`

Request:
```json
{
  "url": "https://example.com/very/long/url"
}
```

Response:
```json
{
  "short_url": "http://localhost:5000/abc123",
  "short_code": "abc123",
  "original_url": "https://example.com/very/long/url",
  "existing": false
}
```

### Redirect to Original URL (External)

**GET** `/<short_code>`

Redirects to the original URL and increments click counter.

### Get Statistics (Internal)

**GET** `/api/stats/<short_code>`

Response:
```json
{
  "original_url": "https://example.com/very/long/url",
  "created_at": "2025-01-15T10:30:00.000000",
  "clicks": 42
}
```

### List All URLs (Internal)

**GET** `/api/list`

Response:
```json
[
  {
    "short_code": "abc123",
    "short_url": "http://localhost:5000/abc123",
    "original_url": "https://example.com/very/long/url",
    "created_at": "2025-01-15T10:30:00.000000",
    "clicks": 42
  }
]
```

### Delete a URL (Internal)

**DELETE** `/api/delete/<short_code>`

Response:
```json
{
  "message": "URL deleted successfully"
}
```

## Using the Python Client

The `client.py` module provides a simple interface for your Edgar project:

### Basic Usage

```python
from client import URLShortenerClient

# Initialize the client
client = URLShortenerClient(base_url="http://localhost:5000")

# Shorten a URL
result = client.shorten("https://example.com/long/url")
print(result['short_url'])  # http://localhost:5000/abc123

# Or get just the short URL string
short_url = client.get_short_url("https://example.com/long/url")
```

### Integration Example

```python
from client import URLShortenerClient

class EdgarProject:
    def __init__(self):
        self.url_shortener = URLShortenerClient(base_url="http://localhost:5000")
    
    def send_email_with_link(self, recipient, original_url):
        # Shorten the URL before sending
        short_url = self.url_shortener.get_short_url(original_url)
        
        # Send email with shortened URL
        email_body = f"Click here: {short_url}"
        self.send_email(recipient, email_body)
    
    def get_link_analytics(self, short_code):
        # Get statistics for a shortened URL
        stats = self.url_shortener.get_stats(short_code)
        return {
            'url': stats['original_url'],
            'clicks': stats['clicks'],
            'created': stats['created_at']
        }
```

### Error Handling

```python
from client import URLShortenerClient
import requests

client = URLShortenerClient()

try:
    result = client.shorten("https://example.com")
except requests.exceptions.RequestException as e:
    print(f"Error shortening URL: {e}")
```

## Deployment

### Development

```bash
python app.py
```

### Production

For production, use a production WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Or use uWSGI:

```bash
pip install uwsgi
uwsgi --http :5000 --wsgi-file app.py --callable app --processes 4
```

### Docker (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:

```bash
docker build -t url-shortener .
docker run -p 5000:5000 -v $(pwd)/urls.json:/app/urls.json url-shortener
```

## Configuration Options

Edit `config.py`:

- `BASE_URL`: Your domain (e.g., 'https://yourdomain.com')
- `SHORT_CODE_LENGTH`: Length of generated codes (default: 6)
- `PORT`: Server port (default: 5000)
- `DATA_FILE`: Path to JSON storage file (default: 'urls.json')

## Security Considerations

Since this is for internal URL creation only:

1. **Authentication**: Consider adding API key authentication to the `/api/shorten`, `/api/list`, `/api/stats`, and `/api/delete` endpoints
2. **Rate Limiting**: Add rate limiting to prevent abuse
3. **HTTPS**: Use HTTPS in production for secure communication
4. **Firewall**: Restrict access to internal API endpoints to your Edgar project only

Example with API key:

```python
from flask import request

API_KEY = "your-secret-api-key"

def require_api_key(f):
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-API-Key') != API_KEY:
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/shorten', methods=['POST'])
@require_api_key
def shorten_url():
    # ... existing code
```

## Troubleshoads

- **Port already in use**: Change `PORT` in `config.py`
- **URLs not persisting**: Check write permissions for `urls.json`
- **Import errors**: Ensure Flask and requests are installed

## License

Internal use for Edgar project.
