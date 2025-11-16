"""
URL Shortener API
Flask API for shortening URLs internally and resolving them externally
No UI - API only for programmatic access
"""

from flask import Flask, request, redirect, jsonify
import string
import random
import sqlite3
import os
from datetime import datetime
import config

app = Flask(__name__)

# Load configuration
DATABASE_PATH = config.DATABASE_PATH
BASE_URL = config.BASE_URL
SHORT_CODE_LENGTH = config.SHORT_CODE_LENGTH

# Database initialization
def init_database():
    """Initialize SQLite database with schema"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            short_code TEXT PRIMARY KEY,
            original_url TEXT NOT NULL,
            created_at TEXT NOT NULL,
            clicks INTEGER DEFAULT 0
        )
    ''')
    
    # Create index for fast lookup by original URL
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_original_url ON urls(original_url)
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    return conn

# Initialize database on startup
init_database()

def generate_short_code():
    """Generate a unique short code for URL"""
    characters = string.ascii_letters + string.digits
    conn = get_db_connection()
    
    while True:
        short_code = ''.join(random.choices(characters, k=SHORT_CODE_LENGTH))
        cursor = conn.cursor()
        cursor.execute('SELECT short_code FROM urls WHERE short_code = ?', (short_code,))
        if cursor.fetchone() is None:
            conn.close()
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
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if URL already exists
    cursor.execute('SELECT short_code FROM urls WHERE original_url = ?', (original_url,))
    existing = cursor.fetchone()
    
    if existing:
        conn.close()
        return jsonify({
            'short_url': f"{BASE_URL}/{existing['short_code']}",
            'short_code': existing['short_code'],
            'original_url': original_url,
            'existing': True
        })
    
    # Generate new short code
    short_code = generate_short_code()
    
    # Store URL mapping
    cursor.execute('''
        INSERT INTO urls (short_code, original_url, created_at, clicks)
        VALUES (?, ?, ?, 0)
    ''', (short_code, original_url, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'short_url': f"{BASE_URL}/{short_code}",
        'short_code': short_code,
        'original_url': original_url,
        'existing': False
    }), 201

@app.route('/<short_code>')
def redirect_to_url(short_code):
    """Redirect short URL to original URL - external access"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT original_url FROM urls WHERE short_code = ?', (short_code,))
    result = cursor.fetchone()
    
    if result:
        # Increment click counter
        cursor.execute('UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?', (short_code,))
        conn.commit()
        conn.close()
        
        return redirect(result['original_url'])
    
    conn.close()
    return jsonify({'error': 'Short code not found'}), 404

@app.route('/api/stats/<short_code>')
def get_stats(short_code):
    """Get statistics for a shortened URL - internal use"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT original_url, created_at, clicks FROM urls WHERE short_code = ?', (short_code,))
    result = cursor.fetchone()
    
    if result:
        stats = {
            'original_url': result['original_url'],
            'created_at': result['created_at'],
            'clicks': result['clicks']
        }
        conn.close()
        return jsonify(stats)
    
    conn.close()
    return jsonify({'error': 'Short code not found'}), 404

@app.route('/api/list')
def list_urls():
    """List all shortened URLs - internal use"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM urls ORDER BY created_at DESC')
    rows = cursor.fetchall()
    
    urls = []
    for row in rows:
        urls.append({
            'short_code': row['short_code'],
            'short_url': f"{BASE_URL}/{row['short_code']}",
            'original_url': row['original_url'],
            'created_at': row['created_at'],
            'clicks': row['clicks']
        })
    
    conn.close()
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
    
    conn = get_db_connection()
    cursor = conn.cursor()
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
        cursor.execute('SELECT short_code FROM urls WHERE original_url = ?', (original_url,))
        existing = cursor.fetchone()
        
        if existing:
            results.append({
                'short_url': f"{BASE_URL}/{existing['short_code']}",
                'short_code': existing['short_code'],
                'original_url': original_url,
                'existing': True
            })
        else:
            # Generate new short code
            short_code = generate_short_code()
            
            # Store URL mapping
            cursor.execute('''
                INSERT INTO urls (short_code, original_url, created_at, clicks)
                VALUES (?, ?, ?, 0)
            ''', (short_code, original_url, datetime.now().isoformat()))
            
            results.append({
                'short_url': f"{BASE_URL}/{short_code}",
                'short_code': short_code,
                'original_url': original_url,
                'existing': False
            })
    
    # Commit all changes at once
    conn.commit()
    conn.close()
    
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM urls WHERE short_code = ?', (short_code,))
    
    if cursor.rowcount > 0:
        conn.commit()
        conn.close()
        return jsonify({'message': 'URL deleted successfully'})
    
    conn.close()
    return jsonify({'error': 'Short code not found'}), 404

if __name__ == '__main__':
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
