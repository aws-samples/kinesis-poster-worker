import sys
# until Kinesis Python SDK is released the absolute path 
# to the Kinesis SDK must be included
sys.path.insert(0, 
	'/Users/brettf/dev/AWSSA-collab/examples/python/kinesis-poster-worker/boto-2.9.8')
import boto
import argparse
import json
import threading
import datetime
import time

from argparse import RawTextHelpFormatter
from boto.canal.exceptions import ResourceNotFoundException
from random import choice
from string import lowercase

print boto.__file__

kinesis = boto.connect_canal()

make_string = lambda(x): "".join(choice(lowercase) for i in range(x))

def get_or_create_stream(stream_name, shard_count):
	stream = None
	try:
		stream = kinesis.describe_stream(stream_name)
		print json.dumps(stream, sort_keys=True, indent=2, 
			separators=(',', ': '))
	except ResourceNotFoundException as rnfe:
		while (stream is None) or (stream['StreamStatus'] is not 'ACTIVE'):
			stream = kinesis.create_stream(stream_name, shard_count)
			time.sleep(0.5)

	return stream

def sum_posts(kinesis_actors):
	total_records = 0
	for actor in kinesis_actors:
		total_records += actor.total_records
	return total_records

class KinesisPoster(threading.Thread):
	"""docstring for KinesisPoster"""
	def __init__(self, stream_name, shard_count, partition_key, 
				 poster_time=30, quiet=False,
				 name=None, group=None, args=(), kwargs={}):
		super(KinesisPoster, self).__init__(name=name, group=group, 
										  args=args, kwargs=kwargs)
		self._pending_records = []
		self.stream_name = stream_name
		self.partition_key = partition_key
		self.quiet = quiet
		self.default_records = [ 
			make_string(100), make_string(1000), make_string(500),
			make_string(5000), make_string(10), make_string(750),
			make_string(10), make_string(2000), make_string(500)
		]
		self.poster_time = poster_time
		self.total_records = 0

	def add_records(self, records):
		self._pending_records.extend(records)

	def put_all_records(self):
		precs = self._pending_records
		self._pending_records = []
		self.put_records(precs)
		self.total_records += len(precs)
		return len(precs)

	def put_records(self, records):
		for record in records:
			response = kinesis.put_record(
				stream_name=self.stream_name, 
				data=record, partition_key=self.partition_key)
			if self.quiet is False:
				print "-= put seqNum:", response['SequenceNumber']

	def run(self):
		start = datetime.datetime.now()
		finish = start + datetime.timedelta(seconds=self.poster_time)
		while finish > datetime.datetime.now():
			self.add_records(self.default_records)
			records_put = self.put_all_records()
			if self.quiet is False:
				print('Records Put:', records_put)
				print(' Total Records Put:', self.total_records)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description='Create or attach to a Kinesis stream and put records in the stream', 
		formatter_class=RawTextHelpFormatter)
	parser.add_argument('stream_name', 
		help='''the name of the Kinesis stream to either create or connect''')
	parser.add_argument('shard_count', type=int, 
		help='''the number of shards in the Kinesis stream''')
	parser.add_argument('--partition_key', default='PyKinesisExample', 
		help='''the partition_key to use when communicating records to the Kinesis stream''')
	parser.add_argument('--poster_count', type=int, default=1, 
		help='''the number of poster threads''')
	parser.add_argument('--poster_time', type=int, default=30, 
		help='''how long the poster threads should put records into the stream''')
	parser.add_argument('--quiet', action='store_true', default=False, 
		help='''reduce console output to just initialization info''')
	parser.add_argument('--delete_stream', action='store_true', default=False, 
		help='''delete the Kinesis stream matching the given stream_name''')
	parser.add_argument('--describe_only', action='store_true', default=False, 
		help='''only describe the Kinesis stream matching the given stream_name''')

	args = parser.parse_args()
	if (args.delete_stream):
		kinesis.delete_stream(stream_name=args.stream_name)
	else:
		start_time = datetime.datetime.now()

		if args.describe_only is True:
			stream = kinesis.describe_stream(args.stream_name)
			print json.dumps(stream, sort_keys=True, indent=2, 
				separators=(',', ': '))
		else:
			stream = get_or_create_stream(args.stream_name, args.shard_count)
			threads = []
			for pid in xrange(args.poster_count):
				poster_name = 'shard_poster:'+str(pid)
				poster = KinesisPoster(
					stream_name=args.stream_name, 
					shard_count=args.shard_count,
					partition_key=args.partition_key, 
					poster_time=args.poster_time,
					name=poster_name,
					quiet=args.quiet)
				poster.daemon = True
				threads.append(poster)
				print 'starting: ', poster_name
				poster.start()

			# Wait for all threads to complete
			for t in threads:
			    t.join()

		finish_time = datetime.datetime.now()
		duration = (finish_time - start_time).total_seconds()
		total_records = sum_posts(threads)
		print "-=> Exiting Poster Main <=-"
		print "  Total Records:", total_records
		print "     Total Time:", duration
		print "  Records / sec:", total_records / duration
