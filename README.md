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
multi-threaded load on a Kinesis stream. 

To get this example working with Python 2.7:
````
pip install boto
````
Follow the instructions [here](http://http://docs.pythonboto.org/en/latest/getting_started.html#configuring-boto-credentials) to get your credentials setup for use by boto.

Then for the first run ```python poster.py my-first-stream``` the Poster will 
attempt to create the Kinesis stream named ```my-first-stream```. In a matter 
of minutes you can run ```python poster.py my-first-stream``` again and Poster
will use multiple threads to pump records into the newly created stream.

Once the Poster is pumping records in you will want to run 
```python worker.py my-first-stream``` which will start reading records from 
the Kinesis stream.

For detailed help and configuration options:
```python poster.py --help``` ..or  ```python worker.py --help```, respectively.  

keywords: aws kinesis poster worker put get boto