#!/bin/sh
#source venv/bin/activate
# exec gunicorn -b :5000 --access-logfile - --error-logfile - api-server:app
exec gunicorn -b :5000 --access-logfile - --error-logfile - api-server:app -k gevent --worker-connections 500