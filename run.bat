@echo off
echo Starting Kannada Movie Recommendation Server...
echo ================================================

set TF_ENABLE_ONEDNN_OPTS=0
set TF_CPP_MIN_LOG_LEVEL=2

echo Server URLs:
echo - Main App: http://127.0.0.1:8000/emotion/emotion_page/
echo - API Test: http://127.0.0.1:8000/emotion/api/recommendations/?emotion=HAPPY
echo - Movie Test: http://127.0.0.1:8000/emotion/tmdb_test/
echo.
echo Press Ctrl+C to stop the server
echo ================================================

python manage.py runserver 8000

pause