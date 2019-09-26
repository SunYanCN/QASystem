#!/bin/bash

# start workers
celery -A query worker --loglevel=INFO --concurrency=1 -n worker1@%h &
celery -A query worker --loglevel=INFO --concurrency=1 -n worker2@%h &
celery -A query worker --loglevel=INFO --concurrency=1 -n worker3@%h &
celery -A query worker --loglevel=INFO --concurrency=1 -n worker4@%h &
# checkout worker status
celery -A query status
