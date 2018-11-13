#!/bin/bash

# Apply database migrations
../wait-for-it.sh db:5432 -- echo "Apply database migrations"
python manage.py makemigrations && python manage.py migrate

  if [ ! -f zodiac/config.py ]; then
      echo "Creating config file"
      cp zodiac/config.py.example zodiac/config.py
  fi

# Create initial organizations and users
echo "Setting up applications and services"
python manage.py shell < ../setup_services.py

echo "Starting celery"
/etc/init.d/celeryd start
/etc/init.d/celerybeat start

#Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8001
