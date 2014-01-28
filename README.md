kinesis-poster-worker
=====================

A simple Python-based Kinesis Poster and Worker example (aka _The Egg Finder_)

_Poster_ is a multi-threaded client that creates ```--poster_count``` poster 
threads to: 
 1. generate random characters, and then
 2. put the generated random characters into the stream as records

_Worker_ is a thread-per-shard client that:  
 1. gets batches of records, and then
 2. seeks through the records for the word '```egg```'

Multiple Poster or Worker clients can be run simultaneously to generate 
multi-threaded load on a Kinesis stream. 
* * *
Getting Started
---------------
To get this example working with Python 2.7+, first install boto 2.23+ using: 
````
$ pip install boto
````
and follow the instructions [here](http://docs.pythonboto.org/en/latest/getting_started.html#configuring-boto-credentials) to get your credentials setup for use. The credentials you use should permit at least these Kinesis actions: ``` CreateStream, DescribeStream, GetRecords, GetShardIterator, ListStreams & 
PutRecord```. Both the ```MergeShards``` and ```SplitShard``` actions are 
unused in this example.

Once boto is configured with your credentials run: 
````
$ python poster.py my-first-stream
```` 
and the Poster will attempt to create the Kinesis stream named 
```my-first-stream```. In a matter of a few minutes the stream will have been 
created and you can again run: 
````
$ python poster.py my-first-stream
````
again. The Poster will then use multiple threads to pump records into the stream.

Once the Poster is pumping records into the stream, then run: 
````
$ python worker.py my-first-stream
```` 
which will start the Worker. The Worker will then begin reading records from 
the ```my-first-stream``` Kinesis stream.

For detailed help and configuration options:
```python poster.py --help``` ..or  ```python worker.py --help```, respectively.

Related Resources
-----------------
* [Amazon Kinesis Developer Guide](http://docs.aws.amazon.com/kinesis/latest/dev/introduction.html)  
* [Amazon Kinesis API Reference](http://docs.aws.amazon.com/kinesis/latest/APIReference/Welcome.html)
* [AWS SDK for Python](http://aws.amazon.com/sdkforpython)
