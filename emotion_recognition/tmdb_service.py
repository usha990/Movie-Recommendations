import os
import requests
from django.conf import settings
try:
    from django.core.cache import cache
except:
    cache = None
from .kannada_movies import get_kannada_movies_by_emotion

class TMDBService:
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
    
    EMOTION_GENRE_MAP = {
        'NEUTRAL': [18, 10751],  # Drama, Family
        'HAPPY': [35, 16, 10402],  # Comedy, Animation, Music
        'SAD': [18, 10749],  # Drama, Romance
        'ANGRY': [28, 53],  # Action, Thriller
        'FEAR': [27, 9648],  # Horror, Mystery
    }
    
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        if not self.api_key:
            raise ValueError("TMDB_API_KEY not found in settings")
        self.genres_cache = {}
    
    def get_genres(self):
        """Get and cache TMDB genres"""
        if cache:
            genres = cache.get('tmdb_genres')
            if genres:
                return genres
        
        if hasattr(self, 'genres_cache') and self.genres_cache:
            return self.genres_cache
            
        try:
            response = requests.get(
                f"{self.BASE_URL}/genre/movie/list",
                params={'api_key': self.api_key},
                timeout=10
            )
            response.raise_for_status()
            genres = {g['id']: g['name'] for g in response.json()['genres']}
            
            if cache:
                cache.set('tmdb_genres', genres, 86400)
            self.genres_cache = genres
            return genres
        except requests.RequestException:
            return {}
    
    def get_recommendations(self, emotion):
        """Get cached movie recommendations by emotion"""
        if cache:
            cache_key = f'tmdb_recommendations_{emotion}'
            recommendations = cache.get(cache_key)
            if recommendations:
                return recommendations
        
        recommendations = self._fetch_recommendations(emotion)
        
        if cache:
            cache.set(cache_key, recommendations, 300)
        
        return recommendations
    
    def _fetch_recommendations(self, emotion):
        """Fetch Kannada movie recommendations from TMDB API"""
        genre_ids = self.EMOTION_GENRE_MAP.get(emotion.upper(), [18])
        genres_dict = self.get_genres()
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/discover/movie",
                params={
                    'api_key': self.api_key,
                    'with_genres': '|'.join(map(str, genre_ids)),
                    'with_original_language': 'kn',  # Kannada language code
                    'vote_count.gte': 10,  # Lower threshold for regional movies
                    'sort_by': 'vote_average.desc',
                    'page': 1
                },
                timeout=10
            )
            response.raise_for_status()
            movies = response.json()['results'][:20]
            
            # If TMDB has Kannada movies, format them
            if movies:
                return [
                    {
                        'id': movie['id'],
                        'title': movie['title'],
                        'year': movie['release_date'][:4] if movie.get('release_date') else 'N/A',
                        'genre_names': ', '.join([genres_dict.get(gid, '') for gid in movie['genre_ids']]),
                        'score': round(movie['vote_average'], 1),
                        'poster_url': f"{self.IMAGE_BASE_URL}{movie['poster_path']}" if movie.get('poster_path') else None,
                        'overview': movie.get('overview', '')[:200] + '...' if len(movie.get('overview', '')) > 200 else movie.get('overview', '')
                    }
                    for movie in movies
                ]
            
        except requests.RequestException:
            pass
        
        # Fallback to local Kannada movie database
        return get_kannada_movies_by_emotion(emotion)