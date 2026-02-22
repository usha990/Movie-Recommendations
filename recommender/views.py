# recommender/views.py
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_GET
import pandas as pd
import numpy as np
import traceback
from . import utils as hr  # ✅ use the working utils.py

# === MAIN UI ===
def ui_view(request):
    """Main CineMatch web interface."""
    try:
        movies_df = pd.read_csv("movies.csv")
        sample_movies = movies_df.head(30).to_dict(orient="records")
    except Exception as e:
        sample_movies = []
        print("⚠️ Error loading movies.csv:", e)
    return render(request, 'recommender/index.html', {"movies": sample_movies})


# === HYBRID RECOMMENDER API ===
@require_GET
def recommend_api(request, user_id):
    try:
        uid = int(user_id)
        alpha = float(request.GET.get('alpha', 0.6))
        recs = hr.recommend_for_user(uid, top_n=20, alpha=alpha)
        return JsonResponse({'user_id': uid, 'alpha': alpha, 'recommendations': recs})
    except Exception as e:
        return JsonResponse({'error': str(e), 'trace': traceback.format_exc()}, status=500)


# === SEARCH API ===
@require_GET
def search_api(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'error': 'q parameter required'}, status=400)
    try:
        res = hr.search_and_recommend(q, top_n=10)
        return JsonResponse({'query': q, 'count': len(res), 'results': res})
    except Exception as e:
        return JsonResponse({'error': str(e), 'trace': traceback.format_exc()}, status=500)


# === EMOTION-BASED ===
def recommend_by_emotion(request, emotion):
    """Return movies matching emotion-mapped genres and attach TMDB poster URLs."""
    # use the module-level utils alias (imported as `hr` above)
    emotion_map = {
        'happy': ['Comedy', 'drama'],
        'sad': ['drama', 'Romance'],
        'angry': ['Action', 'Thriller'],
        'fear': ['horror', 'thriller'],
        'surprise': ['Mystery', 'Fantasy'],
        'neutral': ['Documentary', 'Drama']
    }
    genres = emotion_map.get(emotion.lower(), ['Drama'])
    try:
        movies = hr.load_data()[0]
        mask = movies['genres'].apply(lambda g: any(genre.lower() in g.lower() for genre in genres))
        limit = 20  # return up to 20 items for emotion-based lists
        results = movies[mask].head(limit).to_dict(orient='records')
        # Ensure every result has a poster_url (cached lookup)
        for movie in results:
            title = movie.get('title') or movie.get('name') or ''
            try:
                movie['poster_url'] = hr.fetch_tmdb_poster(title)
            except Exception:
                # On failure, fall back to a static placeholder
                movie['poster_url'] = '/static/no_poster.png'
    except Exception:
        results = []
    return render(request, 'recommender/recommendations.html', {'movies': results, 'emotion': emotion.capitalize()})


def netflix_style(request):
    """Netflix-style interface for hybrid recommendations"""
    return render(request, 'recommender/netflix_style.html')
