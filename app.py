"""
URL Shortener API
Flask API for shortening URLs internally and resolving them externally
No UI - API only for programmatic access
"""

from flask import Flask, request, redirect, jsonify
import string
import random
import json
import os
from datetime import datetime
import config

app = Flask(__name__)

# Load configuration
DATA_FILE = config.DATA_FILE
BASE_URL = config.BASE_URL
SHORT_CODE_LENGTH = config.SHORT_CODE_LENGTH

# Initialize or load URL database
def load_urls():
    """Load URL mappings from file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_urls(url_map):
    """Save URL mappings to file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(url_map, f, indent=2)

url_database = load_urls()

def generate_short_code():
    """Generate a unique short code for URL"""
    characters = string.ascii_letters + string.digits
    while True:
        short_code = ''.join(random.choices(characters, k=SHORT_CODE_LENGTH))
        if short_code not in url_database:
            return short_code

@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    """API endpoint to shorten a URL - internal use only"""
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    original_url = data['url']
    
    # Validate URL format
    if not original_url.startswith(('http://', 'https://')):
        original_url = 'https://' + original_url
    
    # Check if URL already exists
    for code, info in url_database.items():
        if info['original_url'] == original_url:
            return jsonify({
                'short_url': f"{BASE_URL}/{code}",
                'short_code': code,
                'original_url': original_url,
                'existing': True
            })
    
    # Generate new short code
    short_code = generate_short_code()
    
    # Store URL mapping
    url_database[short_code] = {
        'original_url': original_url,
        'created_at': datetime.now().isoformat(),
        'clicks': 0
    }
    
    save_urls(url_database)
    
    return jsonify({
        'short_url': f"{BASE_URL}/{short_code}",
        'short_code': short_code,
        'original_url': original_url,
        'existing': False
    }), 201

@app.route('/<short_code>')
def redirect_to_url(short_code):
    """Redirect short URL to original URL - external access"""
    if short_code in url_database:
        # Increment click counter
        url_database[short_code]['clicks'] += 1
        save_urls(url_database)
        
        original_url = url_database[short_code]['original_url']
        return redirect(original_url)
    
    return jsonify({'error': 'Short code not found'}), 404

@app.route('/api/stats/<short_code>')
def get_stats(short_code):
    """Get statistics for a shortened URL - internal use"""
    if short_code in url_database:
        return jsonify(url_database[short_code])
    
    return jsonify({'error': 'Short code not found'}), 404

@app.route('/api/list')
def list_urls():
    """List all shortened URLs - internal use"""
    urls = []
    for code, info in url_database.items():
        urls.append({
            'short_code': code,
            'short_url': f"{BASE_URL}/{code}",
            'original_url': info['original_url'],
            'created_at': info['created_at'],
            'clicks': info['clicks']
        })
    
    # Sort by creation date (newest first)
    urls.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify(urls)

@app.route('/api/bulk-shorten', methods=['POST'])
def bulk_shorten_urls():
    """API endpoint to shorten multiple URLs at once - internal use only"""
    data = request.get_json()
    
    if not data or 'urls' not in data:
        return jsonify({'error': 'URLs list is required'}), 400
    
    if not isinstance(data['urls'], list):
        return jsonify({'error': 'URLs must be a list'}), 400
    
    if len(data['urls']) == 0:
        return jsonify({'error': 'URLs list cannot be empty'}), 400
    
    if len(data['urls']) > 100:  # Limit to prevent abuse
        return jsonify({'error': 'Maximum 100 URLs allowed per request'}), 400
    
    results = []
    
    for original_url in data['urls']:
        if not isinstance(original_url, str):
            results.append({
                'original_url': original_url,
                'error': 'URL must be a string'
            })
            continue
        
        # Validate URL format
        if not original_url.startswith(('http://', 'https://')):
            original_url = 'https://' + original_url
        
        # Check if URL already exists
        existing_code = None
        for code, info in url_database.items():
            if info['original_url'] == original_url:
                existing_code = code
                break
        
        if existing_code:
            results.append({
                'short_url': f"{BASE_URL}/{existing_code}",
                'short_code': existing_code,
                'original_url': original_url,
                'existing': True
            })
        else:
            # Generate new short code
            short_code = generate_short_code()
            
            # Store URL mapping
            url_database[short_code] = {
                'original_url': original_url,
                'created_at': datetime.now().isoformat(),
                'clicks': 0
            }
            
            results.append({
                'short_url': f"{BASE_URL}/{short_code}",
                'short_code': short_code,
                'original_url': original_url,
                'existing': False
            })
    
    # Save all changes at once
    save_urls(url_database)
    
    return jsonify({
        'results': results,
        'total_processed': len(results),
        'new_urls': len([r for r in results if not r.get('existing', False) and 'error' not in r]),
        'existing_urls': len([r for r in results if r.get('existing', False)]),
        'errors': len([r for r in results if 'error' in r])
    }), 201

@app.route('/api/delete/<short_code>', methods=['DELETE'])
def delete_url(short_code):
    """Delete a shortened URL - internal use"""
    if short_code in url_database:
        del url_database[short_code]
        save_urls(url_database)
        return jsonify({'message': 'URL deleted successfully'})
    
    return jsonify({'error': 'Short code not found'}), 404

if __name__ == '__main__':
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
