from django.shortcuts import render
from django.http import JsonResponse
import cv2
import numpy as np
from fer.fer import FER
from accounts.recommendation import get_emotion_based_movies  # ✅ use your accounts app

# Initialize emotion detector
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
    emotion = emotion.lower()
    recommended_movies = get_emotion_based_movies(emotion)

    return render(request, 'emotion_recommendation.html', {
        'emotion': emotion.capitalize(),
        'movies': recommended_movies
    })
