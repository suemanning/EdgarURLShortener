"""
URL Shortener Client
Python client library for Edgar project to interact with the URL shortener API
"""

import requests
from typing import Optional, Dict, List
from datetime import datetime


class URLShortenerClient:
    """Client for interacting with the URL Shortener API"""
    
    def __init__(self, base_url: str = "http://localhost:5001"):
        """
        Initialize the URL shortener client
        
        Args:
            base_url: Base URL of the URL shortener service
        """
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api"
    
    def shorten(self, url: str) -> Dict:
        """
        Shorten a URL
        
        Args:
            url: The original URL to shorten
            
        Returns:
            Dict containing:
                - short_url: The full shortened URL
                - short_code: Just the short code
                - original_url: The original URL
                - existing: Whether this URL was already shortened
                
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.post(
            f"{self.api_base}/shorten",
            json={'url': url},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def get_stats(self, short_code: str) -> Dict:
        """
        Get statistics for a shortened URL
        
        Args:
            short_code: The short code to get stats for
            
        Returns:
            Dict containing:
                - original_url: The original URL
                - created_at: ISO format timestamp
                - clicks: Number of times the link was clicked
                
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.get(
            f"{self.api_base}/stats/{short_code}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def list_urls(self) -> List[Dict]:
        """
        List all shortened URLs
        
        Returns:
            List of dicts, each containing:
                - short_code: The short code
                - short_url: The full shortened URL
                - original_url: The original URL
                - created_at: ISO format timestamp
                - clicks: Number of clicks
                
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.get(
            f"{self.api_base}/list",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def delete(self, short_code: str) -> Dict:
        """
        Delete a shortened URL
        
        Args:
            short_code: The short code to delete
            
        Returns:
            Dict with success message
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = requests.delete(
            f"{self.api_base}/delete/{short_code}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def get_short_url(self, url: str) -> str:
        """
        Convenience method to get just the shortened URL string
        
        Args:
            url: The original URL to shorten
            
        Returns:
            The shortened URL as a string
        """
        result = self.shorten(url)
        return result['short_url']


# Example usage
if __name__ == "__main__":
    # Initialize the client
    client = URLShortenerClient()
    
    # Shorten a URL
    result = client.shorten("https://example.com/very/long/url/that/needs/shortening")
    print(f"Original: {result['original_url']}")
    print(f"Shortened: {result['short_url']}")
    print(f"Existing: {result['existing']}")
    print()
    
    # Get just the short URL
    short_url = client.get_short_url("https://github.com/anthropics/anthropic-sdk-python")
    print(f"Short URL: {short_url}")
    print()
    
    # Get statistics
    short_code = result['short_code']
    stats = client.get_stats(short_code)
    print(f"Stats for {short_code}:")
    print(f"  Clicks: {stats['clicks']}")
    print(f"  Created: {stats['created_at']}")
    print()
    
    # List all URLs
    all_urls = client.list_urls()
    print(f"Total shortened URLs: {len(all_urls)}")
    for url_info in all_urls[:3]:  # Show first 3
        print(f"  {url_info['short_url']} -> {url_info['original_url'][:50]}...")
