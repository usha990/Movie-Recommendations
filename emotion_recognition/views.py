from django.shortcuts import render
from django.http import JsonResponse
import cv2
import numpy as np
from fer.fer import FER
from .tmdb_service import TMDBService
from .kannada_movies_new import get_kannada_movies_by_emotion

detector = FER(mtcnn=True)


def emotion_page(request):
    """Render the emotion detection page."""
    return render(request, 'emotion.html')


def detect_emotion(request):
    """Receive a frame from frontend and detect emotion."""
    if request.method == 'POST' and request.FILES.get('frame'):
        file = request.FILES['frame']
        img_array = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        # Detect emotion
        result = detector.detect_emotions(frame)
        if result:
            dominant_emotion = max(result[0]['emotions'], key=result[0]['emotions'].get)
            return JsonResponse({'emotion': dominant_emotion.upper()})
        else:
            return JsonResponse({'emotion': None})
    return JsonResponse({'error': 'Invalid request'})


def recommend_by_emotion(request, emotion):
    """Display movies based on detected emotion."""
    emotion = emotion.upper()
    recommended_movies = get_kannada_movies_by_emotion(emotion)

    return render(request, 'emotion_recommendation.html', {
        'emotion': emotion,
        'movies': recommended_movies
    })


def api_recommendations(request):
    """API endpoint for TMDB-based recommendations"""
    emotion = request.GET.get('emotion', 'NEUTRAL').upper()
    
    if emotion not in ['NEUTRAL', 'HAPPY', 'SAD', 'ANGRY', 'FEAR']:
        return JsonResponse({'error': 'Invalid emotion'}, status=400)
    
    try:
        recommendations = get_kannada_movies_by_emotion(emotion)
        return JsonResponse({'recommendations': recommendations})
    except Exception as e:
        return JsonResponse({'error': 'Service unavailable'}, status=503)


def tmdb_test(request):
    """Test page for TMDB integration"""
    return render(request, 'tmdb_test.html')
