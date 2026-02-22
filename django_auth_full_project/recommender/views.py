# recommender/views.py
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_GET
from . import hybrid_recommender as hr
import pandas as pd

# === UI VIEW ===
def ui_view(request):
    """
    Renders the main web interface with a language dropdown.
    """
    movies_df = pd.read_csv("movies.csv")
    languages = sorted(movies_df["language"].dropna().unique().tolist())
    languages.insert(0, "All")

    selected_language = request.GET.get("language", "All")
    if selected_language != "All":
        movies_df = movies_df[movies_df["language"] == selected_language]

    sample_movies = movies_df.head(30).to_dict(orient="records")

    return render(request, 'recommender/index.html', {
        "movies": sample_movies,
        "languages": languages,
        "selected_language": selected_language
    })


# === RECOMMENDATION API ===
@require_GET
def recommend_api(request, user_id):
    """
    Returns hybrid recommendations for a user, optionally filtered by language.
    """
    try:
        uid = int(user_id)
    except Exception:
        return HttpResponseBadRequest('user_id must be integer')

    try:
        alpha = float(request.GET.get('alpha', 0.6))
    except:
        alpha = 0.6

    # Optional language filter (default All)
    selected_language = request.GET.get("language", "All")

    try:
        recs = hr.recommend_for_user(uid, top_n=20, alpha=alpha)

        # If language filter applied, filter recommendations
        if selected_language != "All":
            movies_df = pd.read_csv("movies.csv")
            rec_movie_ids = [r['movieId'] for r in recs]
            filtered_ids = movies_df[movies_df["language"] == selected_language]["movieId"].tolist()
            recs = [r for r in recs if r['movieId'] in filtered_ids]

        return JsonResponse({
            'user_id': uid,
            'alpha': alpha,
            'language': selected_language,
            'recommendations': recs
        })
    except Exception as e:
        # Return the error message to the browser for debugging (dev only)
        return JsonResponse({'error': str(e)}, status=500)


# === SEARCH API ===
@require_GET
def search_api(request):
    """
    Searches movies and returns recommendations based on the search term,
    with optional language filtering.
    """
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'error': 'q parameter required'}, status=400)

    selected_language = request.GET.get("language", "All")

    try:
        res = hr.search_and_recommend(q, top_n=20)

        # Filter by language if requested
        if selected_language != "All":
            movies_df = pd.read_csv("movies.csv")
            filtered_ids = movies_df[movies_df["language"] == selected_language]["movieId"].tolist()
            res = [r for r in res if r['movieId'] in filtered_ids]

        return JsonResponse({
            'query': q,
            'language': selected_language,
            'results': res
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
def recommend_by_emotion(request, emotion):
    emotion_map = {
        'happy': ['Comedy', 'Adventure'],
        'sad': ['Romance', 'Comedy'],
        'angry': ['Action', 'Thriller'],
        'fear': ['Drama', 'Animation'],
        'surprise': ['Mystery', 'Fantasy'],
        'neutral': ['Documentary', 'Drama']
    }

    genres = emotion_map.get(emotion.lower(), ['Drama'])
    movies = Movie.objects.filter(genre__in=genres)[:10]
    return render(request, 'recommender/recommendations.html', {'movies': movies, 'emotion': emotion})
