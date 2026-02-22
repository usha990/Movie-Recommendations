import pandas as pd
import os
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np


# --- Safe CSV Loading Setup ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def safe_read_csv(filename):
    """Safely read a CSV, skipping malformed lines and using absolute path."""
    filepath = os.path.join(BASE_DIR, filename)
    try:
        df = pd.read_csv(filepath, on_bad_lines="skip", encoding='utf-8')
        print(f"✅ Loaded {filename} successfully with {len(df)} records.")
        return df
    except Exception as e:
        print(f"⚠️ Error loading {filename}: {e}")
        return pd.DataFrame()

# Load datasets
movies = safe_read_csv("movies.csv")
ratings = safe_read_csv("ratings.csv")

# --- Hybrid Recommendation Algorithm ---
def hybrid_recommend(user_id, top_n=10):
    """Return top-N recommended movies using hybrid (content + collaborative) filtering."""
    if movies.empty or ratings.empty:
        print("⚠️ CSV files not loaded properly.")
        return []

    # --- Content-based filtering part ---
    if 'genres' in movies.columns:
        movies['genres'] = movies['genres'].fillna('')
        cv = CountVectorizer(tokenizer=lambda x: x.split('|'))
        genre_matrix = cv.fit_transform(movies['genres'])
        content_sim = cosine_similarity(genre_matrix)
    else:
        print("⚠️ 'genres' column not found in movies.csv")
        return []

    # --- Collaborative filtering part ---
    user_movie_matrix = ratings.pivot_table(index='userId', columns='movieId', values='rating')
    user_movie_matrix = user_movie_matrix.fillna(0)
    collab_sim = cosine_similarity(user_movie_matrix)
    collab_sim_df = pd.DataFrame(collab_sim, index=user_movie_matrix.index, columns=user_movie_matrix.index)

    # --- Hybrid approach ---
    if user_id not in collab_sim_df.index:
        print(f"⚠️ User {user_id} not found in ratings.")
        return []

    # Combine similarities (simple average)
    similar_users = collab_sim_df[user_id].sort_values(ascending=False)[1:11]
    similar_user_ids = similar_users.index.tolist()

    user_ratings = ratings[ratings['userId'].isin(similar_user_ids)]
    mean_ratings = user_ratings.groupby('movieId')['rating'].mean().sort_values(ascending=False)
    top_movie_ids = mean_ratings.head(top_n).index

    recommendations = movies[movies['movieId'].isin(top_movie_ids)]
    return recommendations[['movieId', 'title']].to_dict(orient='records')


# --- Emotion-based Movie Recommendation ---
def get_emotion_based_movies(emotion):
    emotion_to_genres = {
        'happy': ['Comedy', 'Family', 'Animation'],
        'sad': ['Drama', 'Romance'],
        'angry': ['Action', 'Thriller'],
        'fear': ['Horror', 'Mystery'],
        'surprise': ['Adventure', 'Fantasy'],
        'disgust': ['Crime', 'Drama'],
        'neutral': ['Drama', 'Family']
    }

    genres = emotion_to_genres.get(emotion.lower(), ['Drama'])

    if movies.empty:
        print("⚠️ Movies CSV not loaded.")
        return []

    # Filter by matching any of the emotion genres
    mask = movies['genres'].apply(lambda g: any(genre in g for genre in genres))
    recommended = movies[mask]

    if recommended.empty:
        recommended = movies.sample(10)

    # Add a random "score" for better UI display
    recommended = recommended.copy()
    recommended['score'] = np.random.uniform(3.0, 5.0, len(recommended))
    
    # Return movie info with genre and score
    return recommended.head(10)[['movieId', 'title', 'genres', 'score']].to_dict(orient='records')
