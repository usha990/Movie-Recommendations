"""
Kannada movie database for emotion-based recommendations
"""
import requests
from django.conf import settings
from django.core.cache import cache
import hashlib

KANNADA_MOVIES = {
    'HAPPY': [
        {'title': 'Kirik Party', 'year': '2016', 'genre_names': 'Comedy, Drama', 'score': 8.2, 'overview': 'A fun-filled college drama about friendship and love.'},
        {'title': 'Ulidavaru Kandanthe', 'year': '2014', 'genre_names': 'Comedy, Drama', 'score': 8.5, 'overview': 'Multiple perspectives of the same incident in a coastal town.'},
        {'title': 'Lucia', 'year': '2013', 'genre_names': 'Drama, Thriller', 'score': 8.3, 'overview': 'A psychological thriller about dreams and reality.'},
        {'title': 'Godhi Banna Sadharana Mykattu', 'year': '2016', 'genre_names': 'Comedy, Drama', 'score': 8.0, 'overview': 'A heartwarming story about Alzheimer\'s and family bonds.'},
        {'title': 'Dia', 'year': '2020', 'genre_names': 'Romance, Drama', 'score': 7.8, 'overview': 'A beautiful love story spanning different time periods.'}
    ],
    'SAD': [
        {'title': 'Thithi', 'year': '2015', 'genre_names': 'Drama, Comedy', 'score': 8.1, 'overview': 'A rural drama about three generations dealing with death.'},
        {'title': 'Ondu Motteya Kathe', 'year': '2017', 'genre_names': 'Drama, Romance', 'score': 7.9, 'overview': 'A touching story about self-acceptance and love.'},
        {'title': 'Nathicharami', 'year': '2018', 'genre_names': 'Drama', 'score': 7.7, 'overview': 'A bold exploration of a woman\'s desires and relationships.'},
        {'title': 'Aa Karaala Ratri', 'year': '2018', 'genre_names': 'Drama, Thriller', 'score': 7.5, 'overview': 'A dark night that changes everything for the characters.'},
        {'title': 'Kanoora Heggadati', 'year': '1999', 'genre_names': 'Drama', 'score': 8.0, 'overview': 'A classic tale of love and sacrifice in rural Karnataka.'}
    ],
    'ANGRY': [
        {'title': 'KGF Chapter 1', 'year': '2018', 'genre_names': 'Action, Drama', 'score': 8.2, 'overview': 'The rise of Rocky in the gold mines of Kolar.'},
        {'title': 'KGF Chapter 2', 'year': '2022', 'genre_names': 'Action, Drama', 'score': 8.4, 'overview': 'Rocky\'s empire faces new challenges and enemies.'},
        {'title': 'Tagaru', 'year': '2018', 'genre_names': 'Action, Crime', 'score': 7.6, 'overview': 'A violent tale of revenge and justice.'},
        {'title': 'Avane Srimannarayana', 'year': '2019', 'genre_names': 'Action, Comedy', 'score': 7.8, 'overview': 'A quirky action-comedy set in a fictional town.'},
        {'title': 'Roberrt', 'year': '2021', 'genre_names': 'Action, Drama', 'score': 7.2, 'overview': 'A mass entertainer with high-octane action sequences.'}
    ],
    'FEAR': [
        {'title': 'Kavaludaari', 'year': '2019', 'genre_names': 'Mystery, Thriller', 'score': 7.9, 'overview': 'A gripping mystery about skeletal remains found in Bangalore.'},
        {'title': 'U Turn', 'year': '2016', 'genre_names': 'Mystery, Thriller', 'score': 7.7, 'overview': 'A supernatural thriller about a flyover and mysterious deaths.'},
        {'title': 'Gultoo', 'year': '2018', 'genre_names': 'Thriller, Drama', 'score': 7.4, 'overview': 'A cyber-thriller about data theft and corruption.'},
        {'title': 'Rathnan Prapancha', 'year': '2021', 'genre_names': 'Mystery, Drama', 'score': 7.3, 'overview': 'A mysterious tale involving a book and its consequences.'},
        {'title': 'Shivaji Surathkal', 'year': '2020', 'genre_names': 'Mystery, Crime', 'score': 7.5, 'overview': 'A detective story with twists and turns.'}
    ],
    'NEUTRAL': [
        {'title': 'Sarkari Hi. Pra. Shale Kasaragodu', 'year': '2018', 'genre_names': 'Drama, Comedy', 'score': 8.1, 'overview': 'A heartwarming story about a government school.'},
        {'title': 'Humble Politician Nograj', 'year': '2018', 'genre_names': 'Comedy, Satire', 'score': 7.6, 'overview': 'A political satire about a corrupt politician.'},
        {'title': 'French Biriyani', 'year': '2020', 'genre_names': 'Comedy, Drama', 'score': 7.4, 'overview': 'A comedy about an auto driver and his adventures.'},
        {'title': 'Mayabazar 2016', 'year': '2020', 'genre_names': 'Comedy, Fantasy', 'score': 7.2, 'overview': 'A modern take on the classic Mayabazar story.'},
        {'title': 'Panchatantra', 'year': '2019', 'genre_names': 'Drama, Thriller', 'score': 7.8, 'overview': 'Five interconnected stories exploring human nature.'}
    ]
}

def fetch_tmdb_poster(title, year=None):
    """Fetch real poster from TMDB API - NO placeholders"""
    cache_key = f'tmdb_{hashlib.md5(f"{title}_{year}".encode()).hexdigest()}'
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    api_key = settings.TMDB_API_KEY
    if not api_key:
        return None
    
    try:
        params = {'api_key': api_key, 'query': title}
        if year:
            params['year'] = year
        
        response = requests.get(
            'https://api.themoviedb.org/3/search/movie',
            params=params,
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get('results') and data['results'][0].get('poster_path'):
            poster_url = f"https://image.tmdb.org/t/p/w500{data['results'][0]['poster_path']}"
            cache.set(cache_key, poster_url, 86400)
            return poster_url
    except:
        pass
    
    return None

def get_kannada_movies_by_emotion(emotion):
    """Get Kannada movies with real TMDB posters"""
    movies = KANNADA_MOVIES.get(emotion.upper(), KANNADA_MOVIES['NEUTRAL'])
    
    result = []
    for movie in movies:
        movie_copy = movie.copy()
        movie_copy['id'] = hash(movie['title']) % 10000
        movie_copy['poster_url'] = fetch_tmdb_poster(movie['title'], movie['year'])
        result.append(movie_copy)
    
    return result