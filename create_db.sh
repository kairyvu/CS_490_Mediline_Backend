#!/usr/bin/env bash
## Script to create database in mysql
## Should be in project root and uses .env
set -ex
. .env

cat <<-EOF > tmp_create.sql
DROP SCHEMA IF EXISTS ${MYSQL_DATABASE};
CREATE SCHEMA ${MYSQL_DATABASE} DEFAULT CHARACTER SET utf8mb4;
EOF

mysql -u "${MYSQL_USER}" -p"${MYSQL_PASSWORD}" -h "${MYSQL_HOST}" < tmp_create.sql
mysql -u "${MYSQL_USER}" -p"${MYSQL_PASSWORD}" -h "${MYSQL_HOST}" -e "SHOW SCHEMAS;" | grep "${MYSQL_DATABASE}"

rm tmp_create.sql

