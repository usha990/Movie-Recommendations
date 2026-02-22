import requests
from django.conf import settings
from django.core.cache import cache

def fetch_tmdb_poster(movie_title, year=None):
    """
    Fetch movie poster URL from TMDB API by title.
    
    Args:
        movie_title (str): Movie title to search
        year (int, optional): Release year for better matching
    
    Returns:
        str: Full poster URL or None if not found
    """
    if not movie_title:
        return None
    
    # Check cache first
    cache_key = f'poster_{movie_title}_{year}'
    cached_url = cache.get(cache_key)
    if cached_url:
        return cached_url
    
    api_key = getattr(settings, 'TMDB_API_KEY', None)
    if not api_key:
        print(f"[ERROR] TMDB_API_KEY not found in settings")
        return None
    
    try:
        # Search for movie
        response = requests.get(
            'https://api.themoviedb.org/3/search/movie',
            params={
                'api_key': api_key,
                'query': movie_title,
                'year': year
            },
            timeout=5
        )
        response.raise_for_status()
        results = response.json().get('results', [])
        
        if results:
            poster_path = results[0].get('poster_path')
            if poster_path:
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                cache.set(cache_key, poster_url, 86400)
                print(f"[OK] Fetched poster for '{movie_title}': {poster_url}")
                return poster_url
        
        print(f"[WARN] No poster found for '{movie_title}'")
    
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch poster for '{movie_title}': {e}")
    
    return None
