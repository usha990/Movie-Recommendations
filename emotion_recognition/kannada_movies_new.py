"""
Enhanced emotion-based movie recommendations using movies.csv
"""
import pandas as pd
import requests
from django.core.cache import cache
import hashlib
import random

# Emotion to genre mapping - MAIN FOCUS genres
EMOTION_GENRE_MAP = {
    'HAPPY': ['Comedy', 'Animation', 'Family'],  # Main focus: Comedy + Animation + Family
    'SAD': ['Drama', 'Romance'],  # Main focus: Drama + Romance
    'ANGRY': ['Action', 'Thriller'],  # Main focus: Action + Thriller
    'FEAR': ['Horror', 'Mystery'],  # Main focus: Horror + Mystery
    'NEUTRAL': ['Drama', 'Adventure', 'Documentary']  # Main focus: Drama + Adventure + Documentary
}

def fetch_tmdb_poster(title, year=None):
    """Fetch real poster from TMDB API"""
    cache_key = f'tmdb_{hashlib.md5(f"{title}_{year}".encode()).hexdigest()}'
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    api_key = '937bdb1c447a5f3d54df1951ba92f033'
    
    try:
        params = {'api_key': api_key, 'query': title}
        if year:
            params['year'] = year
        
        response = requests.get(
            'https://api.themoviedb.org/3/search/movie',
            params=params,
            timeout=3
        )
        data = response.json()
        
        if data.get('results') and data['results'][0].get('poster_path'):
            poster_url = f"https://image.tmdb.org/t/p/w500{data['results'][0]['poster_path']}"
            cache.set(cache_key, poster_url, 86400)
            return poster_url
    except:
        pass
    
    return 'https://via.placeholder.com/500x750/333/fff?text=No+Poster'

def get_kannada_movies_by_emotion(emotion, limit=20):
    """Get movies from CSV based on emotion-genre mapping"""
    try:
        # Load movies.csv
        df = pd.read_csv('movies.csv')
        
        # Get genres for this emotion
        target_genres = EMOTION_GENRE_MAP.get(emotion.upper(), EMOTION_GENRE_MAP['NEUTRAL'])
        
        # Filter movies by genre
        def matches_emotion(genres_str):
            if pd.isna(genres_str):
                return False
            genres = genres_str.lower()
            return any(genre.lower() in genres for genre in target_genres)
        
        filtered = df[df['genres'].apply(matches_emotion)]
        
        # If not enough results, get random movies
        if len(filtered) < limit:
            filtered = df.sample(min(limit, len(df)))
        else:
            filtered = filtered.sample(min(limit, len(filtered)))
        
        # Build result
        results = []
        for _, movie in filtered.iterrows():
            # Extract year from title if present
            title = movie['title']
            year = None
            if '(' in title and ')' in title:
                try:
                    year = title[title.rfind('(')+1:title.rfind(')')]
                except:
                    pass
            
            # Get poster from CSV or fetch from TMDB
            poster_url = movie.get('poster_url', '')
            if not poster_url or pd.isna(poster_url) or poster_url == '':
                poster_url = fetch_tmdb_poster(title, year)
            
            results.append({
                'id': int(movie['movieId']),
                'title': title,
                'year': year or 'N/A',
                'genre_names': movie['genres'],
                'score': round(random.uniform(7.0, 9.0), 1),
                'overview': f"A {movie['genres']} movie that matches your {emotion.lower()} mood.",
                'poster_url': poster_url
            })
        
        return results
        
    except Exception as e:
        print(f"Error loading movies: {e}")
        return []
