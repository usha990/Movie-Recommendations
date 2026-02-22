import requests
from django.core.cache import cache
import hashlib
import re

def get_tmdb_poster(movie_title):
    """Fetch real poster URL from TMDB API"""
    if not movie_title:
        return 'https://via.placeholder.com/500x750/333/fff?text=No+Poster'
    
    clean_title = re.sub(r'\s*\(\d{4}\)\s*$', '', movie_title).strip()
    
    cache_key = f'tmdb_poster_{hashlib.md5(clean_title.encode()).hexdigest()}'
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    api_key = '937bdb1c447a5f3d54df1951ba92f033'
    
    try:
        response = requests.get(
            'https://api.themoviedb.org/3/search/movie',
            params={'api_key': api_key, 'query': clean_title},
            timeout=5
        )
        data = response.json()
        
        if data.get('results'):
            poster_path = data['results'][0].get('poster_path')
            if poster_path:
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                cache.set(cache_key, poster_url, 86400)
                return poster_url
    except Exception as e:
        print(f"[ERROR] TMDB API error for '{clean_title}': {e}")
    
    fallback = 'https://via.placeholder.com/500x750/333/fff?text=No+Poster'
    cache.set(cache_key, fallback, 86400)
    return fallback
