#!/usr/bin/env bash

gunicorn --threads=2 'flaskr:create_app()' -b 0.0.0.0:8080
