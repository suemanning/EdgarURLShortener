"""
Test script for URL Shortener API
Run this after starting the server to verify everything works
"""

from client import URLShortenerClient
import time


def test_url_shortener():
    """Test all URL shortener functionality"""
    print("=" * 60)
    print("URL Shortener API Test")
    print("=" * 60)
    print()
    
    # Initialize client
    client = URLShortenerClient("https://edgarurlshortener.onrender.com")
    
    # Test 1: Shorten a URL
    print("Test 1: Shortening a URL")
    print("-" * 60)
    test_url = "https://github.com/anthropics/anthropic-sdk-python"
    try:
        result = client.shorten(test_url)
        print(f"✓ Original URL: {result['original_url']}")
        print(f"✓ Short URL: {result['short_url']}")
        print(f"✓ Short Code: {result['short_code']}")
        print(f"✓ Was Existing: {result['existing']}")
        short_code = result['short_code']
        short_url = result['short_url']
        print("PASSED ✓")
    except Exception as e:
        print(f"FAILED ✗ - {e}")
        return
    print()
    
    # Test 2: Shorten the same URL again (should return existing)
    print("Test 2: Shortening duplicate URL")
    print("-" * 60)
    try:
        result2 = client.shorten(test_url)
        if result2['existing'] and result2['short_code'] == short_code:
            print(f"✓ Correctly returned existing short code: {result2['short_code']}")
            print("PASSED ✓")
        else:
            print("FAILED ✗ - Did not reuse existing short code")
    except Exception as e:
        print(f"FAILED ✗ - {e}")
    print()
    
    # Test 3: Get statistics
    print("Test 3: Getting URL statistics")
    print("-" * 60)
    try:
        stats = client.get_stats(short_code)
        print(f"✓ Original URL: {stats['original_url']}")
        print(f"✓ Created At: {stats['created_at']}")
        print(f"✓ Clicks: {stats['clicks']}")
        print("PASSED ✓")
    except Exception as e:
        print(f"FAILED ✗ - {e}")
    print()
    
    # Test 4: List all URLs
    print("Test 4: Listing all URLs")
    print("-" * 60)
    try:
        all_urls = client.list_urls()
        print(f"✓ Found {len(all_urls)} shortened URL(s)")
        for url_info in all_urls[:3]:
            print(f"  - {url_info['short_url']} -> {url_info['original_url'][:50]}...")
        print("PASSED ✓")
    except Exception as e:
        print(f"FAILED ✗ - {e}")
    print()
    
    # Test 5: Convenience method
    print("Test 5: Using convenience method")
    print("-" * 60)
    try:
        another_url = "https://www.python.org/doc/"
        quick_short = client.get_short_url(another_url)
        print(f"✓ Shortened {another_url}")
        print(f"✓ Result: {quick_short}")
        print("PASSED ✓")
    except Exception as e:
        print(f"FAILED ✗ - {e}")
    print()
    
    # Test 6: Test redirect (informational only)
    print("Test 6: Testing redirect (manual verification)")
    print("-" * 60)
    print(f"Visit {short_url} in your browser")
    print(f"It should redirect to: {test_url}")
    print("MANUAL TEST")
    print()
    
    print("=" * 60)
    print("All automated tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    print("\nTesting the deployed URL shortener at https://edgarurlshortener.onrender.com\n")
    time.sleep(1)
    
    try:
        test_url_shortener()
    except Exception as e:
        print(f"\nTest suite failed with error: {e}")
        print("Check if https://edgarurlshortener.onrender.com is accessible")
