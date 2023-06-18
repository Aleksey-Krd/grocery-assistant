#!/bin/sh
python manage.py makemigrations;
python manage.py migrate;
python manage.py collectstatic;
cp -r /app/collected_static/. /app/static/
gunicorn -b 0:8000 foodgram_backend.wsgi;
