#!/usr/bin/env python
"""Test script to verify TMDB API integration"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_project.settings')
django.setup()

from emotion_recognition.tmdb_service import TMDBService

def test_tmdb():
    print("Testing TMDB API integration...")
    
    try:
        tmdb = TMDBService()
        print(f"[OK] TMDB Service initialized with API key: {tmdb.api_key[:10]}...")
        
        # Test genres
        genres = tmdb.get_genres()
        print(f"[OK] Fetched {len(genres)} genres")
        
        # Test recommendations
        recommendations = tmdb.get_recommendations('HAPPY')
        print(f"[OK] Fetched {len(recommendations)} recommendations for HAPPY emotion")
        
        if recommendations:
            movie = recommendations[0]
            print(f"Sample movie: {movie['title']} ({movie['year']})")
            print(f"Poster URL: {movie['poster_url']}")
        
        print("[SUCCESS] TMDB integration working correctly!")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tmdb()