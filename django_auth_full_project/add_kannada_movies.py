import pandas as pd
import random
from datetime import datetime

# === CONFIGURATION ===
movies_path = "movies.csv"     # Adjust if your CSVs are in a subfolder
ratings_path = "ratings.csv"

# === LOAD EXISTING DATA ===
movies_df = pd.read_csv(movies_path)
ratings_df = pd.read_csv(ratings_path)

# === Detect columns ===
movieid_col = "movieId"
title_col = "title"
genres_col = "genres"

# Add 'language' column if not already present
if "language" not in movies_df.columns:
    movies_df["language"] = "English"   # assume existing movies are English

# === Generate 2000 Kannada movies ===
start_id = int(movies_df[movieid_col].max()) + 1

k_words = ["Amma","Nanna","Prema","Hridaya","Mane","Beladingala","Hosa","Jeevana","Prerana","Veera",
           "Kshama","Sneha","Bhakti","Shanti","Dhwani","Baduku","Nodi","Kannada","Katha","Mana",
           "Mouna","Muhurtha","Chethana","Yuvajana","Taranga","Hrudaya","Saakshi","Sanchaya",
           "Namma","Sogadu","Aashirvada"]

suffixes = [" - The Story", " (Kannada)", " - A Tale", ": The Journey", " - An Emotion", " : Amma's Love"]

titles, genres, languages = [], [], []
for i in range(2000):
    title = f"{random.choice(k_words)} {random.choice(k_words)}{random.choice(suffixes)} ({random.randint(1980,2025)})"
    titles.append(title)
    genres.append(random.choice(["Drama|Family", "Drama|Inspirational", "Family|Drama", "Drama|Romance"]))
    languages.append("Kannada")

new_movies = pd.DataFrame({
    movieid_col: range(start_id, start_id + 2000),
    title_col: titles,
    genres_col: genres,
    "language": languages
})

# === Append new Kannada movies ===
movies_df = pd.concat([movies_df, new_movies], ignore_index=True)

# === Generate random ratings for new movies ===
user_ids = list(range(1001, 3001))
new_ratings = []
for u in user_ids:
    rated_movies = random.sample(list(new_movies[movieid_col]), k=20)
    for m in rated_movies:
        rating = round(random.uniform(2.5, 5.0), 1)
        timestamp = int(datetime.now().timestamp())
        new_ratings.append([u, m, rating, timestamp])

new_ratings_df = pd.DataFrame(new_ratings, columns=["userId", "movieId", "rating", "timestamp"])

# === Append to ratings ===
ratings_df = pd.concat([ratings_df, new_ratings_df], ignore_index=True)

# === Save Updated CSVs ===
movies_df.to_csv(movies_path, index=False)
ratings_df.to_csv(ratings_path, index=False)

print("✅ Added 2000 Kannada movies and", len(new_ratings_df), "ratings successfully!")
print("✅ 'language' column added with Kannada tag for new movies.")
