#!/usr/bin/env bash

rm -rf migrations/
./create_db.sh
make schema
