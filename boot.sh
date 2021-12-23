#!/bin/sh
poetry run flask db upgrade
exec gunicorn -b :5000 --access-logfile - --error-logfile - schengen_calculator:app