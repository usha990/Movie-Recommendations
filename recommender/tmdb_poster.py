import requests
import re

def get_movie_poster_url(title):
    """Fetch movie poster from TMDB API"""
    api_key = '937bdb1c447a5f3d54df1951ba92f033'
    
    # Clean title and extract year
    clean_title = re.sub(r'\s*\(\d{4}\)', '', title).strip()
    year_match = re.search(r'\((\d{4})\)', title)
    year = year_match.group(1) if year_match else None
    
    try:
        params = {
            'api_key': api_key,
            'query': clean_title
        }
        if year:
            params['year'] = year
            
        response = requests.get(
            'https://api.themoviedb.org/3/search/movie',
            params=params,
            timeout=5
        )
        
        data = response.json()
        if data.get('results'):
            poster_path = data['results'][0].get('poster_path')
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except:
        pass
    
    return f"https://via.placeholder.com/300x450/333/fff?text={title.replace(' ', '+')}"