kinesis-poster-worker
=====================

Kinesis Poster and Worker example.  

Poster is a multi-threaded client that:  
1. generates random characters
2. posts those random characters as records

Worker is a thread-per-shard client that:  
1. retrieves batches of records
2. seeks through the records for the word 'egg'

Multiple clients can be run simultaneously to generate more load on the Kinesis stream.  

Detailed help: ```python poster.py --help``` ..or  ```python worker.py --help```, respectively.  

keywords: kinesis poster worker put get