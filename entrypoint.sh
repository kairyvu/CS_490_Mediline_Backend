#!/usr/bin/env bash

make upgrade_models

gunicorn --threads 4 -b 0.0.0.0:8080 'flaskr:create_app()' 
