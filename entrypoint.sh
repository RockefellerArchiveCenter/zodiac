#!/bin/bash

# Apply database migrations
echo "Apply database migrations"
../wait-for-it.sh db:5432 -- python manage.py migrate

  if [ ! -f projectelectronapigateway/config.py ]; then
      echo "Creating config file"
      cp projectelectronapigateway/config.py.example projectelectronapigateway/config.py
  fi

#Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000
