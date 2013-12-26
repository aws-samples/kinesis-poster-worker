kinesis-poster-worker
=====================

Kinesis Poster and Worker example.  

Poster is a multi-threaded client that creates ```--poster_count``` poster 
threads to: 
 1. generate random characters, and then
 2. put the generated random characters into the stream as records

Worker is a thread-per-shard client that:  
 1. gets batches of records, and then
 2. seeks through the records for the word '```egg```'

Multiple Poster or Worker clients can be run simultaneously to generate 
multi-threaded load on the Kinesis stream. 

Detailed help: ```python poster.py --help``` ..or  ```python worker.py --help```, respectively.  

keywords: kinesis poster worker put get