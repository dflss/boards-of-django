#!/bin/sh

pip install -r requirements.txt

bash /usr/src/wait-for-it.sh $POSTGRES_HOST:$POSTGRES_PORT -- echo "PostgreSQL is up"

python manage.py collectstatic --no-input

exec "$@"
