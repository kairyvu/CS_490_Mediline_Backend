#!/usr/bin/env bash

make upgrade_models

gunicorn --preload --threads 8 -b 0.0.0.0:8080 'flaskr:create_app()' 
