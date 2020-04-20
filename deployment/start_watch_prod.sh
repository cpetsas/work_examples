#!/bin/bash
export PROD=0

# REDIS
export REDIS_ENDPOINT_DEV=localhost
export REDIS_PORT_DEV=6379
export REDIS_ENDPOINT_PROD=localhost
export REDIS_PORT_PROD=6379
# CATALOG
export CATALOG_ENDPOINT_DEV=
export CATALOG_ENDPOINT_PROD=

# MAP AND STATISTICAL
export MS_ENDPOINT_DEV=
export MS_ENDPOINT_PROD=

## IMAGE SIZE
export MAP_W=400
export MAP_H=400

# TEMPLATE
export DEFAULT_TEMPLATE=/home/ubuntu/report-dfms/templates/default/template.json

# EMAIL CREDENTIALS
export USER=
export PASS=

# DB
export DBNAME=
export DBUSER=
export DBPASS=
export DBHOST=.eu-west-2.rds.amazonaws.com
export DBPORT=

# RUN CODE
/home/ubuntu/report-dfms/env/bin/python /home/ubuntu/report-dfms/src/watcher.py
