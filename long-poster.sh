#!/bin/bash

nohup python poster.py my-first-stream --shard_count 10 --poster_count 50 --poster_time 345600 --partition_key Kinesis02 --quiet &
