#!/usr/bin/env bash
export FLASK_APP=wsgi.py
export FLASK_DEBUG=1
export APP_CONFIG_FILE=config.py
export SECRET_KEY=<SECRET_KEY>

#flask run --host=0.0.0.0
gunicorn -b 0.0.0.0:5000 wsgi:app --threads 12
