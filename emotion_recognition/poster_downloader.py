import os
import requests
import hashlib
from django.conf import settings
from django.core.cache import cache

POSTER_DIR = os.path.join(settings.BASE_DIR, 'static', 'posters')
os.makedirs(POSTER_DIR, exist_ok=True)

def download_poster(poster_url):
    """Download poster image and return local path"""
    if not poster_url or 'image.tmdb.org' not in poster_url:
        return '/static/no_poster.png'
    
    # Generate filename from URL hash
    filename = hashlib.md5(poster_url.encode()).hexdigest() + '.jpg'
    filepath = os.path.join(POSTER_DIR, filename)
    local_url = f'/static/posters/{filename}'
    
    # Return if already downloaded
    if os.path.exists(filepath):
        return local_url
    
    # Check cache
    cached = cache.get(f'poster_{filename}')
    if cached:
        return cached
    
    try:
        response = requests.get(poster_url, timeout=10, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)
        
        cache.set(f'poster_{filename}', local_url, 86400)
        return local_url
    
    except:
        return '/static/no_poster.png'
