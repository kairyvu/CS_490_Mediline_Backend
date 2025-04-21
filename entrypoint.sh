#!/usr/bin/env bash

#rm -rf migrations
#./create_db.sh

#make schema
make upgrade_models
#make fake

gunicorn --workers=2 'flaskr:create_app()' -b 0.0.0.0:8080
