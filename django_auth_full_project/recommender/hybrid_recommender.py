# recommender/hybrid_recommender.py

from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

CANDIDATE_PATHS = [
    BASE_DIR / "movies.csv",
    BASE_DIR / "data" / "movies.csv",
    PROJECT_ROOT / "movies.csv",
    PROJECT_ROOT / "data" / "movies.csv",
]

CANDIDATE_RATINGS_PATHS = [
    BASE_DIR / "ratings.csv",
    BASE_DIR / "data" / "ratings.csv",
    PROJECT_ROOT / "ratings.csv",
    PROJECT_ROOT / "data" / "ratings.csv",
]


# 🧠 Helper functions
def find_existing(path_list):
    for p in path_list:
        if p.exists():
            return p
    return None


def normalize_scores(score_dict):
    if not score_dict:
        return {}
    vals = np.array(list(score_dict.values()), dtype=float)
    minv, maxv = vals.min(), vals.max()
    out = {}
    if maxv - minv <= 1e-9:
        for k in score_dict:
            out[k] = 0.0
        return out
    for k, v in score_dict.items():
        out[k] = float((v - minv) / (maxv - minv))
    return out


# 🎬 Main Recommender Class
class HybridRecommender:
    def __init__(self):
        self.movies, self.ratings = self.load_data()
        self.content_mat, self.tfidf = self.build_content_matrix(self.movies)
        self.sim_df, self.pivot = self.compute_item_similarity_from_ratings(self.ratings)

    def load_data(self):
        movies_path = find_existing(CANDIDATE_PATHS)
        ratings_path = find_existing(CANDIDATE_RATINGS_PATHS)
        if movies_path is None or ratings_path is None:
            raise FileNotFoundError(
                f"movies.csv or ratings.csv not found. Searched:\nmovies: {CANDIDATE_PATHS}\nratings: {CANDIDATE_RATINGS_PATHS}"
            )

        movies = pd.read_csv(movies_path)
        ratings = pd.read_csv(ratings_path)

        movies = movies.rename(columns={c: c.strip() for c in movies.columns})
        ratings = ratings.rename(columns={c: c.strip() for c in ratings.columns})

        if 'movieId' in movies.columns and 'movie_id' not in movies.columns:
            movies = movies.rename(columns={'movieId': 'movie_id'})
        if 'movieId' in ratings.columns and 'movie_id' not in ratings.columns:
            ratings = ratings.rename(columns={'movieId': 'movie_id'})
        if 'userId' in ratings.columns and 'user_id' not in ratings.columns:
            ratings = ratings.rename(columns={'userId': 'user_id'})

        if 'movie_id' not in movies.columns or 'title' not in movies.columns:
            raise ValueError("movies.csv must contain columns: movie_id (or movieId) and title")
        if 'movie_id' not in ratings.columns or 'user_id' not in ratings.columns or 'rating' not in ratings.columns:
            raise ValueError("ratings.csv must contain columns: user_id (or userId), movie_id (or movieId), rating")

        movies['movie_id'] = movies['movie_id'].astype(int)
        ratings['movie_id'] = ratings['movie_id'].astype(int)
        ratings['user_id'] = ratings['user_id'].astype(int)

        return movies, ratings

    def build_content_matrix(self, movies):
        text = movies['title'].fillna('') + " " + movies.get('genres', pd.Series(['']*len(movies))).fillna('')
        tf = TfidfVectorizer(stop_words='english', max_features=5000)
        mat = tf.fit_transform(text.astype(str))
        return mat, tf

    def compute_item_similarity_from_ratings(self, ratings):
        pivot = ratings.pivot_table(index='user_id', columns='movie_id', values='rating').fillna(0)
        if pivot.shape[1] == 0:
            sim_df = pd.DataFrame()
            return sim_df, pivot
        item_matrix = pivot.T.values
        sim = cosine_similarity(item_matrix)
        movie_ids = pivot.columns.astype(int)
        sim_df = pd.DataFrame(sim, index=movie_ids, columns=movie_ids)
        return sim_df, pivot

    def predict_cf_scores_for_user(self, user_id):
        if self.pivot.empty or user_id not in self.pivot.index:
            return {}
        user_ratings = self.pivot.loc[user_id]
        rated = user_ratings[user_ratings > 0]
        unrated = user_ratings[user_ratings == 0]
        scores = {}
        for movie_id in unrated.index:
            if movie_id not in self.sim_df.index:
                scores[movie_id] = 0.0
                continue
            sim_to_rated = self.sim_df.loc[movie_id, rated.index]
            denom = sim_to_rated.abs().sum()
            if denom == 0:
                scores[movie_id] = 0.0
            else:
                scores[movie_id] = float((sim_to_rated * rated).sum() / denom)
        return scores

    def compute_content_scores_for_user(self, user_id):
        user_ratings = self.ratings[self.ratings['user_id'] == user_id]
        liked = user_ratings[user_ratings['rating'] >= 4]['movie_id'].unique().astype(int)
        all_ids = self.movies['movie_id'].astype(int).values
        idx_map = {mid: i for i, mid in enumerate(all_ids)}
        scores = {int(mid): 0.0 for mid in all_ids}
        if len(liked) == 0:
            return scores
        liked_idxs = [idx_map[mid] for mid in liked if mid in idx_map]
        if not liked_idxs:
            return scores
        liked_vecs = self.content_mat[liked_idxs]
        sim = cosine_similarity(liked_vecs, self.content_mat)
        max_sim = sim.max(axis=0)
        for i, mid in enumerate(all_ids):
            scores[int(mid)] = float(max_sim[i])
        return scores

    def recommend_for_user(self, user_id, top_n=10, alpha=0.6):
        cf_scores = self.predict_cf_scores_for_user(user_id)
        content_scores = self.compute_content_scores_for_user(user_id)

        cf_norm = normalize_scores(cf_scores)
        content_norm = normalize_scores(content_scores)

        user_rated = set(self.ratings[self.ratings['user_id'] == user_id]['movie_id'].astype(int).tolist())
        combined = {}
        for mid in self.movies['movie_id'].astype(int).values:
            if mid in user_rated:
                continue
            cf = cf_norm.get(mid, 0.0)
            cont = content_norm.get(mid, 0.0)
            combined[mid] = float(alpha * cf + (1 - alpha) * cont)

        if not combined:
            pop = self.ratings.groupby('movie_id')['rating'].mean().sort_values(ascending=False).head(top_n)
            res = []
            for mid, sc in pop.items():
                title = self.movies[self.movies['movie_id'] == mid]['title'].values[0]
                res.append({'movie_id': int(mid), 'title': title, 'score': float(sc)})
            return res

        ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:top_n]
        results = []
        for mid, sc in ranked:
            row = self.movies[self.movies['movie_id'] == mid]
            title = row.iloc[0]['title'] if not row.empty else str(mid)
            results.append({'movie_id': int(mid), 'title': title, 'score': float(sc)})
        return results

    def get_top_movies_by_genres(self, genres, top_n=10):
        """Return top movies for given genres (for emotion-based filtering)."""
        if self.movies.empty:
            print("⚠️ Movies CSV not loaded properly.")
            return []

        self.movies['genres'] = self.movies['genres'].fillna('')
        mask = self.movies['genres'].apply(lambda g: any(genre.lower() in g.lower() for genre in genres))
        filtered = self.movies[mask]

        if filtered.empty:
            print("⚠️ No movies matched the given genres, returning fallback set.")
            return self.movies.sample(min(10, len(self.movies))).to_dict(orient='records')

        return filtered.head(top_n).to_dict(orient='records')
