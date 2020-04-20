#!/bin/bash
source ./env/bin/activate
supervisord -c ./supervisord.conf
rq-dashboard
python ./report-DFMS/src/watcher.py
