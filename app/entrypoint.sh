#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then 
    echo "Waiting for postgress..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
        sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py flush --no-input
python manage.py migrate --no-input

exec "$@"
