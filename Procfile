# Flask app lives in api_server.py (app = Flask(__name__)) → api_server:app. Bind to Railway's PORT.
web: gunicorn api_server:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120 --log-level debug
