#!/bin/bash

celery multi kill worker1@%h worker2@%h worker3@%h worker4@%h --pidfile=pids/%n.pid --logfile=logs/%n.log
rm -rf pids
rm -rf logs

