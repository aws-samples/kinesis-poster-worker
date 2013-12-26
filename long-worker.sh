#!/bin/bash

nohup python worker.py my-first-stream --sleep_interval 0.1 --worker_time 345600 --partition_key Kinesis01 > 01worker.out 2> 01worker.err < /dev/null &
