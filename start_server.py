#!/usr/bin/env python
"""
Simple script to start the Django server with proper error handling
"""

import os
import sys
import subprocess

def start_server():
    print("Starting Kannada Movie Recommendation Server...")
    print("=" * 50)
    
    try:
        # Set environment variable to avoid TensorFlow warnings
        os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        
        # Start Django server
        print("Server starting at: http://127.0.0.1:8000")
        print("Available URLs:")
        print("- Netflix-Style Interface: http://127.0.0.1:8000/recommender/netflix/")
        print("- Emotion Detection: http://127.0.0.1:8000/emotion/emotion_page/")
        print("- Hybrid API: http://127.0.0.1:8000/recommender/api/recommend/1/")
        print("- Kannada Movies API: http://127.0.0.1:8000/emotion/api/recommendations/?emotion=HAPPY")
        print("- Test Page: http://127.0.0.1:8000/emotion/tmdb_test/")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 50)
        
        subprocess.run([sys.executable, 'manage.py', 'runserver', '8000'], check=True)
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    start_server()