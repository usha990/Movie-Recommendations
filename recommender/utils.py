# recommender/utils.py
import pandas as pd
import numpy as np
from pathlib import Path
import os
import re
import logging
import urllib.parse
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
try:
    from emotion_recognition.tmdb_utils import get_movie_poster_url
except ImportError:
    def get_movie_poster_url(title):
        return f"https://via.placeholder.com/300x450/333/fff?text={title.replace(' ', '+')}"

BASE = Path(__file__).resolve().parent.parent
MOVIES_CSV = BASE / 'movies.csv'
RATINGS_CSV = BASE / 'ratings.csv'

# Optional: lightweight TMDB poster fetcher with caching
try:
    from django.conf import settings
    from django.core.cache import cache
except Exception:
    # When running outside Django (scripts/tests) provide no-op stubs
    settings = None
    cache = None


def _clean_title(title):
    """Remove trailing year like 'Title (1995)' for better TMDB matches."""
    if not title:
        return ''
    return re.sub(r"\s*\(\d{4}\)", '', str(title)).strip()


def fetch_tmdb_poster(title: str) -> str:
    """Fetch poster URL for a movie title from TMDB with caching.

    Returns full image URL or a placeholder.
    """
    fallback = 'https://via.placeholder.com/500x750/333/fff?text=No+Poster'

    if not title:
        return fallback

    key = '937bdb1c447a5f3d54df1951ba92f033'

    cache_key = f"tmdb_poster:{urllib.parse.quote_plus(title.lower())}"
    try:
        if cache is not None:
            cached = cache.get(cache_key)
            if cached:
                return cached
    except Exception:
        pass

    search_url = 'https://api.themoviedb.org/3/search/movie'
    params = {'api_key': key, 'query': _clean_title(title)}
    try:
        resp = requests.get(search_url, params=params, timeout=6)
        resp.raise_for_status()
        data = resp.json()
        results = data.get('results') or []
        if results:
            poster_path = results[0].get('poster_path')
            if poster_path:
                full = f'https://image.tmdb.org/t/p/w500{poster_path}'
                try:
                    if cache is not None:
                        cache.set(cache_key, full, 24 * 3600)
                except Exception:
                    pass
                return full
    except Exception as e:
        logging.error(f'TMDB error for {title}: {e}')

    try:
        if cache is not None:
            cache.set(cache_key, fallback, 24 * 3600)
    except Exception:
        pass
    return fallback


def load_data():
    """
    Loads movies and ratings CSVs from project root (same folder as manage.py).
    Expected columns:
      movies.csv -> movie_id,title,genres
      ratings.csv -> user_id,movie_id,rating
    """
    movies = pd.read_csv(MOVIES_CSV)
    ratings = pd.read_csv(RATINGS_CSV)

    # Normalize column names
    movies = movies.rename(columns={c.strip(): c.strip() for c in movies.columns})
    ratings = ratings.rename(columns={c.strip(): c.strip() for c in ratings.columns})

    # Handle alternate column names
    if 'movieId' in movies.columns and 'movie_id' not in movies.columns:
        movies = movies.rename(columns={'movieId': 'movie_id'})
    if 'movieId' in ratings.columns and 'movie_id' not in ratings.columns:
        ratings = ratings.rename(columns={'movieId': 'movie_id'})
    if 'userId' in ratings.columns and 'user_id' not in ratings.columns:
        ratings = ratings.rename(columns={'userId': 'user_id'})

    movies['movie_id'] = movies['movie_id'].astype(int)
    ratings['movie_id'] = ratings['movie_id'].astype(int)
    ratings['user_id'] = ratings['user_id'].astype(int)

    return movies, ratings


def build_content_matrix(movies):
    """
    Build TF-IDF matrix from movie title + genres.
    """
    content = (movies['title'].fillna('') + " " +
               movies.get('genres', pd.Series([''] * len(movies))).fillna('')).astype(str)
    tf = TfidfVectorizer(stop_words='english', max_features=5000)
    mat = tf.fit_transform(content)
    return mat, tf


def compute_item_similarity(ratings):
    """
    Compute item-item similarity using item vectors formed from user ratings (item-based CF).
    """
    pivot = ratings.pivot_table(index='user_id', columns='movie_id', values='rating').fillna(0)
    if pivot.shape[1] == 0:
        return pd.DataFrame(), pivot

    sim = cosine_similarity(pivot.T)
    movie_ids = pivot.columns.astype(int)
    sim_df = pd.DataFrame(sim, index=movie_ids, columns=movie_ids)
    return sim_df, pivot


def predict_cf_scores_for_user(user_id, ratings, sim_df, pivot):
    """Predict collaborative scores using weighted item-based CF."""
    if user_id not in pivot.index:
        return {}
    user_ratings = pivot.loc[user_id]
    rated = user_ratings[user_ratings > 0]
    unrated = user_ratings[user_ratings == 0]
    scores = {}
    for movie_id in unrated.index:
        if movie_id not in sim_df.index:
            scores[movie_id] = 0.0
            continue
        sim_to_rated = sim_df.loc[movie_id, rated.index]
        denom = sim_to_rated.abs().sum()
        if denom == 0:
            scores[movie_id] = 0.0
        else:
            scores[movie_id] = float((sim_to_rated * rated).sum() / denom)
    return scores


def compute_content_scores_for_user(user_id, movies, ratings, content_mat):
    """Compute content similarity scores for a user’s liked movies."""
    user_ratings = ratings[ratings['user_id'] == user_id]
    liked = user_ratings[user_ratings['rating'] >= 4]['movie_id'].unique().astype(int)
    all_ids = movies['movie_id'].astype(int).values
    idx_map = {mid: i for i, mid in enumerate(all_ids)}
    scores = {int(mid): 0.0 for mid in all_ids}

    if len(liked) == 0:
        return scores

    liked_idxs = [idx_map[mid] for mid in liked if mid in idx_map]
    if not liked_idxs:
        return scores

    liked_vecs = content_mat[liked_idxs]
    sim = cosine_similarity(liked_vecs, content_mat)
    max_sim = sim.max(axis=0)

    for i, mid in enumerate(all_ids):
        scores[int(mid)] = float(max_sim[i])
    return scores


def normalize_scores(score_dict):
    """Min-max normalize dictionary values."""
    if not score_dict:
        return {}
    vals = np.array(list(score_dict.values()), dtype=float)
    minv, maxv = vals.min(), vals.max()
    if maxv - minv <= 1e-9:
        return {k: 0.0 for k in score_dict}
    return {k: float((v - minv) / (maxv - minv)) for k, v in score_dict.items()}


def recommend_for_user(user_id, top_n=10, alpha=0.6):
    """Hybrid recommendation combining CF + Content-based."""
    movies, ratings = load_data()
    content_mat, _ = build_content_matrix(movies)
    sim_df, pivot = compute_item_similarity(ratings)
    cf_scores = predict_cf_scores_for_user(user_id, ratings, sim_df, pivot)
    content_scores = compute_content_scores_for_user(user_id, movies, ratings, content_mat)

    cf_norm = normalize_scores(cf_scores)
    content_norm = normalize_scores(content_scores)

    user_rated = set(ratings[ratings['user_id'] == user_id]['movie_id'].astype(int).tolist())
    combined = {}
    for mid in movies['movie_id'].astype(int).values:
        if mid in user_rated:
            continue
        cf = cf_norm.get(mid, 0.0)
        cont = content_norm.get(mid, 0.0)
        combined[mid] = float(alpha * cf + (1 - alpha) * cont)

    if not combined:
        pop = ratings.groupby('movie_id')['rating'].mean().sort_values(ascending=False).head(top_n)
        return [{'movie_id': int(mid),
                 'title': movies.loc[movies['movie_id'] == mid, 'title'].values[0],
                 'score': float(sc)} for mid, sc in pop.items()]

    ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:top_n]
    results = []
    for mid, sc in ranked:
        title = movies.loc[movies['movie_id'] == mid, 'title'].values[0]
        genres = movies.loc[movies['movie_id'] == mid, 'genres'].values[0] if 'genres' in movies.columns else 'N/A'
        results.append({
            'movie_id': int(mid),
            'title': title,
            'genres': genres,
            'score': float(sc),
            'poster_url': get_movie_poster_url(title),
            'rating': round(np.random.uniform(3.5, 5.0), 1)
        })
    return results


def search_and_recommend(query, top_n=10, similarity_threshold=0.15):
    """Hybrid movie search using enhanced content filtering + TMDB ratings."""
    from .hybrid_recommender import recommender
    return recommender.recommend(query, top_n)
