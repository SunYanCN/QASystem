#!/bin/bash

rm -rf logs && mkdir logs
rm -rf pids && mkdir pids

celery -A query multi start worker1@%h worker2@%h worker3@%h worker4@%h --concurrency=1 --pidfile=pids/%n.pid --logfile=logs/%n.log

