#!/bin/bash

rm -rf logs && mkdir logs
rm -rf pids && mkdir pids
# start workers
celery -A query worker --loglevel=INFO --concurrency=1 -n worker1@%h --logfile=logs/%n.log --pidfile=pids/%n.pid &
celery -A query worker --loglevel=INFO --concurrency=1 -n worker2@%h --logfile=logs/%n.log --pidfile=pids/%n.pid &
celery -A query worker --loglevel=INFO --concurrency=1 -n worker3@%h --logfile=logs/%n.log --pidfile=pids/%n.pid &
celery -A query worker --loglevel=INFO --concurrency=1 -n worker4@%h --logfile=logs/%n.log --pidfile=pids/%n.pid &
# checkout worker status
celery -A query status

