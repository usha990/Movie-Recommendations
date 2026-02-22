"""
Batch script to fetch and save poster URLs to CSV
Run: python update_posters.py
"""
import pandas as pd
import requests
import time
import re
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

TMDB_API_KEY = '937bdb1c447a5f3d54df1951ba92f033'

def clean_title(title):
    return re.sub(r'\s*\(\d{4}\)\s*$', '', str(title)).strip()

def create_session():
    """Create session with retry logic"""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

session = create_session()

def fetch_poster(title, retries=3):
    for attempt in range(retries):
        try:
            response = session.get(
                'https://api.themoviedb.org/3/search/movie',
                params={'api_key': TMDB_API_KEY, 'query': clean_title(title)},
                timeout=5
            )
            data = response.json()
            if data.get('results'):
                poster_path = data['results'][0].get('poster_path')
                if poster_path:
                    return f"https://image.tmdb.org/t/p/w500{poster_path}"
            return ''  # No results found
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)  # Wait before retry
                continue
            return ''  # Failed after retries
    return ''

print("Loading movies.csv...")
df = pd.read_csv('movies.csv')

# Add poster_url column if not exists
if 'poster_url' not in df.columns:
    df['poster_url'] = ''
    print("Added poster_url column")

# Update only missing posters
missing_mask = (df['poster_url'] == '') | (df['poster_url'].isna())
missing = df[missing_mask]
print(f"\nFound {len(missing)} movies without posters")
print(f"Fetching from TMDB API...\n")

save_interval = 50  # Save every 50 movies
count = 0

for idx, row in missing.iterrows():
    poster = fetch_poster(row['title'])
    df.at[idx, 'poster_url'] = poster
    status = "✓" if poster else "✗"
    print(f"[{idx+1}/{len(df)}] {status} {row['title']}")
    
    count += 1
    if count % save_interval == 0:
        df.to_csv('movies.csv', index=False)
        print(f"  💾 Progress saved ({count} processed)")
    
    time.sleep(0.3)  # Rate limit: ~3 requests/second

# Final save
df.to_csv('movies.csv', index=False)
print(f"\n✅ Done! Updated {len(missing)} posters in movies.csv")
