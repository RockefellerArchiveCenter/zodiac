#!/bin/bash

# Apply database migrations
../wait-for-it.sh db:5432 -- echo "Apply database migrations"
python manage.py migrate

  if [ ! -f zodiac/config.py ]; then
      echo "Creating config file"
      cp zodiac/config.py.example zodiac/config.py
  fi

#Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8001
