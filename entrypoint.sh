#!/bin/bash

# Apply database migrations
./wait-for-it.sh db:5432 --

if [ ! -f zodiac/config.py ]; then
    echo "Creating config file"
    cp zodiac/config.py.example zodiac/config.py
fi

echo "Apply database migrations"
python manage.py migrate

# Create initial organizations and users
echo "Setting up applications and services"
python manage.py setup_services

echo "Starting celery using supervisor"
supervisord -c /etc/supervisord.conf

#Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:${APPLICATION_PORT}
