#!/bin/bash
# Production-ready startup script using Gunicorn

# Install gunicorn if needed
pip install gunicorn -q

# Start with gunicorn (4 workers for better performance)
gunicorn -w 4 -b 127.0.0.1:5000 --access-logfile - --error-logfile - app:app
