# TMDB Movie Recommendations Setup

## 1. Install Dependencies
```bash
pip install -r requirements.txt
```

## 2. Get TMDB API Key
1. Go to https://www.themoviedb.org/settings/api
2. Create account and request API key
3. Copy your API key

## 3. Set Environment Variable
Create `.env` file in project root:
```
TMDB_API_KEY=your_actual_api_key_here
```

## 4. Load Environment Variables
Add to your `settings.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

## 5. Test the API
Visit: `http://localhost:8000/emotion/api/recommendations/?emotion=NEUTRAL`

## 6. Use the Template
Visit: `http://localhost:8000/emotion/recommend_by_emotion/neutral/`

## Emotion Options
- NEUTRAL, HAPPY, SAD, ANGRY, FEAR, CALM

## API Response Format
```json
{
  "recommendations": [
    {
      "id": 123,
      "title": "Movie Title",
      "year": "2023",
      "genre_names": "Action, Drama",
      "score": 8.5,
      "poster_url": "https://image.tmdb.org/t/p/w500/poster.jpg",
      "overview": "Movie description..."
    }
  ]
}
```