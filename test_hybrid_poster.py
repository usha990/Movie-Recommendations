import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_project.settings')
django.setup()

from accounts.recommendation import hybrid_recommend

print("Testing Hybrid Recommendation Poster Fetching...")
print("=" * 50)

recommendations = hybrid_recommend(user_id=1, top_n=3)

for movie in recommendations:
    print(f"Title: {movie['title']}")
    print(f"Poster: {movie.get('poster_url', 'None')}")
    print("-" * 50)
