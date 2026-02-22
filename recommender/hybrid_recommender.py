import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
from django.core.cache import cache
import re
import os

TMDB_API_KEY = '937bdb1c447a5f3d54df1951ba92f033'

class HybridRecommender:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if HybridRecommender._initialized:
            return
        self.movies = None
        self.vectorizer = None
        self.tfidf_matrix = None
        self.similarity_matrix = None
        HybridRecommender._initialized = True
        # Don't load on init - load on first request
    
    def _ensure_loaded(self):
        if self.movies is None:
            self._load_data()
    
    def _clean_title(self, title):
        return re.sub(r'\s*\(\d{4}\)\s*$', '', str(title)).strip()
    
    def _fetch_tmdb_metadata(self, title):
        cache_key = f'tmdb_meta_{title.lower()}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            response = requests.get(
                'https://api.themoviedb.org/3/search/movie',
                params={'api_key': TMDB_API_KEY, 'query': self._clean_title(title)},
                timeout=2  # Reduced from 5 to 2 seconds
            )
            data = response.json()
            if data.get('results'):
                result = data['results'][0]
                metadata = {
                    'overview': result.get('overview', ''),
                    'vote_average': result.get('vote_average', 5.0),
                    'vote_count': result.get('vote_count', 0),
                    'poster_path': result.get('poster_path', '')
                }
                cache.set(cache_key, metadata, 86400)
                return metadata
        except Exception as e:
            pass  # Fail silently for speed
        
        return {'overview': '', 'vote_average': 5.0, 'vote_count': 0, 'poster_path': ''}
    
    def _load_data(self):
        print("[INFO] Loading movie data...")
        self.movies = pd.read_csv('movies.csv')
        self.movies['genres'] = self.movies['genres'].fillna('')
        
        # Check if poster_url column exists, if not add it
        if 'poster_url' not in self.movies.columns:
            self.movies['poster_url'] = ''
        
        # Simple genre processing - NO TMDB fetching during load
        self.movies['processed_genres'] = self.movies['genres'].apply(
            lambda x: ' '.join(x.replace('|', ' ').lower().split())
        )
        
        # Build TF-IDF
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2),
            min_df=1
        )
        
        self.tfidf_matrix = self.vectorizer.fit_transform(self.movies['processed_genres'])
        self.similarity_matrix = cosine_similarity(self.tfidf_matrix)
        
        print(f"[INFO] Loaded {len(self.movies)} movies successfully")
    
    def recommend(self, movie_title, top_n=10):
        self._ensure_loaded()
        
        matches = self.movies[self.movies['title'].str.contains(movie_title, case=False, na=False)]
        
        if matches.empty:
            print(f"[WARN] No matches found for: {movie_title}")
            return []
        
        idx = matches.index[0]
        movie_name = self.movies.iloc[idx]['title']
        
        print(f"[INFO] Recommending for: {movie_name}")
        
        # Get similarity scores
        sim_row = self.similarity_matrix[idx]
        sim_scores = list(enumerate(sim_row))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:30]
        
        # Extract indices and values
        movie_indices = [i[0] for i in sim_scores]
        similarity_values = [i[1] for i in sim_scores]
        
        # Get candidates
        candidates = self.movies.iloc[movie_indices].copy()
        candidates['similarity'] = similarity_values
        
        # Filter by threshold
        candidates = candidates[candidates['similarity'] > 0.1]
        
        # Build results
        results = []
        for _, movie in candidates.head(top_n).iterrows():
            # Use CSV poster_url if available, otherwise fetch from TMDB
            if 'poster_url' in movie and movie['poster_url'] and str(movie['poster_url']) != 'nan':
                poster_url = movie['poster_url']
                meta = {'vote_average': 5.0, 'vote_count': 0}  # Default values
            else:
                meta = self._fetch_tmdb_metadata(movie['title'])
                poster_url = f"https://image.tmdb.org/t/p/w500{meta['poster_path']}" if meta['poster_path'] else 'https://via.placeholder.com/500x750/333/fff?text=No+Poster'
            
            actual_similarity = float(movie['similarity'])
            normalized_rating = meta['vote_average'] / 10.0
            final_score = 0.7 * actual_similarity + 0.3 * normalized_rating
            
            results.append({
                'movie_id': int(movie['movieId']),
                'title': movie['title'],
                'genres': movie['genres'],
                'similarity_score': round(actual_similarity, 3),
                'vote_average': round(float(meta['vote_average']), 1),
                'vote_count': int(meta.get('vote_count', 0)),
                'final_score': round(float(final_score), 3),
                'poster_url': poster_url
            })
        
        results = sorted(results, key=lambda x: x['final_score'], reverse=True)
        print(f"[INFO] Returning {len(results)} recommendations")
        return results

# Singleton instance
recommender = HybridRecommender()
