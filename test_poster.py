import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_project.settings')
django.setup()

from accounts.tmdb_helper import get_tmdb_poster

# Test poster fetching
test_movies = ['KGF Chapter 1', 'Kirik Party', 'Toy Story']

print("Testing TMDB Poster Fetching...")
print("=" * 50)

for movie in test_movies:
    poster = get_tmdb_poster(movie)
    print(f"{movie}: {poster}")
    
print("=" * 50)
