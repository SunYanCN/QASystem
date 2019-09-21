#!/bin/bash

celery -A worker worker --loglevel=INFO --concurrency=1 -n worker1@%h &
celery -A worker worker --loglevel=INFO --concurrency=1 -n worker2@%h &
celery -A worker worker --loglevel=INFO --concurrency=1 -n worker3@%h &
celery -A worker worker --loglevel=INFO --concurrency=1 -n worker4@%h &
