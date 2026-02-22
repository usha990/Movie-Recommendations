#!/usr/bin/env python3
"""
Setup script to configure TMDB API integration.
Run this script to add your TMDB API key.
"""

import os

def setup_tmdb_api():
    print("🎬 TMDB API Setup")
    print("=" * 50)
    print("1. Go to https://www.themoviedb.org/settings/api")
    print("2. Create an account and request an API key")
    print("3. Copy your API key and paste it below")
    print()
    
    api_key = input("Enter your TMDB API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Exiting.")
        return
    
    # Update the tmdb_utils.py file
    tmdb_file = "emotion_recognition/tmdb_utils.py"
    
    try:
        with open(tmdb_file, 'r') as f:
            content = f.read()
        
        # Replace the placeholder API key
        updated_content = content.replace(
            'TMDB_API_KEY = "YOUR_API_KEY_HERE"',
            f'TMDB_API_KEY = "{api_key}"'
        )
        
        with open(tmdb_file, 'w') as f:
            f.write(updated_content)
        
        print(f"✅ API key saved to {tmdb_file}")
        print("🎉 TMDB integration is now ready!")
        print("\nYour movie recommendations will now show real poster images.")
        
    except FileNotFoundError:
        print(f"❌ Could not find {tmdb_file}")
    except Exception as e:
        print(f"❌ Error updating file: {e}")

if __name__ == "__main__":
    setup_tmdb_api()