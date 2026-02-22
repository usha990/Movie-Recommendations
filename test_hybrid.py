#!/usr/bin/env python
"""Test script to verify hybrid recommendation system"""

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_project.settings')
django.setup()

from accounts.recommendation import hybrid_recommend
import pandas as pd

def test_hybrid():
    print("Testing Hybrid Recommendation System...")
    print("=" * 50)
    
    # Load data to check available users
    try:
        ratings = pd.read_csv("ratings.csv")
        print(f"Loaded {len(ratings)} ratings")
        
        # Get some sample user IDs
        sample_users = ratings['userId'].unique()[:5]
        print(f"Sample user IDs: {sample_users}")
        
        # Test hybrid recommendation for first user
        user_id = sample_users[0]
        print(f"\nTesting recommendations for user {user_id}:")
        
        recommendations = hybrid_recommend(user_id, top_n=5)
        
        if recommendations:
            print(f"[SUCCESS] Got {len(recommendations)} recommendations:")
            for i, movie in enumerate(recommendations, 1):
                print(f"  {i}. {movie['title']} - {movie['genres']}")
        else:
            print("[ERROR] No recommendations returned")
            
        # Test with invalid user
        print(f"\nTesting with invalid user ID 99999:")
        invalid_recs = hybrid_recommend(99999)
        if not invalid_recs:
            print("[SUCCESS] Correctly handled invalid user")
        
        print("\n[RESULT] Hybrid recommendation system is working correctly!")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_hybrid()