# Copyright 2013-2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not
# use this file except in compliance with the License. A copy of the License
# is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "LICENSE.txt" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

from __future__ import print_function

import boto
import argparse
import json
import threading
import time
import datetime

from argparse import RawTextHelpFormatter
from random import choice
from string import lowercase
from boto.kinesis.exceptions import ResourceNotFoundException

# To preclude inclusion of aws keys into this code, you may temporarily add
# your AWS credentials to the file:
#     ~/.boto
# as follows:
#     [Credentials]
#     aws_access_key_id = <your access key>
#     aws_secret_access_key = <your secret key>

make_string = lambda x: "".join(choice(lowercase) for i in range(x))

def get_or_create_stream(stream_name, shard_count):
    stream = None
    try:
        stream = kinesis.describe_stream(stream_name)
        print (json.dumps(stream, sort_keys=True, indent=2,
            separators=(',', ': ')))
    except ResourceNotFoundException as rnfe:
        while (stream is None) or ('ACTIVE' not in stream['StreamDescription']['StreamStatus']):
            if stream is None:
                print ('Could not find ACTIVE stream:{0} trying to create.'.format(
                    stream_name))
                kinesis.create_stream(stream_name, shard_count)
            else:
                print ("Stream status: %s" % stream['StreamDescription']['StreamStatus'])
            time.sleep(1)
            stream = kinesis.describe_stream(stream_name)

    return stream


def sum_posts(kinesis_actors):
    """Sum all posts across an array of KinesisPosters
    """
    total_records = 0
    for actor in kinesis_actors:
        total_records += actor.total_records
    return total_records


class KinesisPoster(threading.Thread):
    """The Poster thread that repeatedly posts records to shards in a given
    Kinesis stream.
    """
    def __init__(self, stream_name, partition_key, poster_time=30, quiet=False,
                 name=None, group=None, filename=None, args=(), kwargs={}):
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
        self.file_contents = None
        if filename is not None:
            print('~> opening file:{0}'.format(filename))
            with open(filename, 'r') as content_file:
                self.file_contents = content_file.read(40000)

    def add_records(self, records):
        """ Add given records to the Poster's pending records list.
        """
        print('~> adding records:{0}'.format(records))
        if len(records) is 1:
            self._pending_records.extend(records[0])
        else:
            self._pending_records.extend(records)

    def put_all_records(self):
        """Put all pending records in the Kinesis stream."""
        precs = self._pending_records
        self._pending_records = []
        self.put_records(precs)
        self.total_records += len(precs)
        return len(precs)

    def put_file_contents(self):
        if self.file_contents:
            response = kinesis.put_record(
                stream_name=self.stream_name,
                data=self.file_contents, partition_key=self.partition_key)
            self.total_records += 1
            if self.quiet is False:
                print ("-= put seqNum:", response['SequenceNumber'])

    def put_records(self, records):
        """Put the given records in the Kinesis stream."""
        for record in records:
            response = kinesis.put_record(
                stream_name=self.stream_name,
                data=record, partition_key=self.partition_key)
            if self.quiet is False:
                print ("-= put seqNum:", response['SequenceNumber'])

    def run(self):
        start = datetime.datetime.now()
        finish = start + datetime.timedelta(seconds=self.poster_time)
        while finish > datetime.datetime.now():
            if self.file_contents:
                self.put_file_contents()
            else:
                self.add_records(self.default_records)
            records_put = self.put_all_records()
            if self.quiet is False:
                print(' Total Records Put:', self.total_records)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='''Create or attach to a Kinesis stream and put records in the stream''',
        formatter_class=RawTextHelpFormatter)
    parser.add_argument('stream_name',
        help='''the name of the Kinesis stream to either connect with or create''')
    parser.add_argument('--region', type=str, default='us-east-1',
        help='''the name of the Kinesis region to connect with [default: us-east-1]''')
    parser.add_argument('--shard_count', type=int, default=1,
        help='''the number of shards to create in the stream, if creating [default: 1]''')
    parser.add_argument('--partition_key', default='PyKinesisExample',
        help='''the partition key to use when communicating records to the
stream [default: 'PyKinesisExample-##']''')
    parser.add_argument('--poster_count', type=int, default=2,
        help='''the number of poster threads [default: 10]''')
    parser.add_argument('--poster_time', type=int, default=30,
        help='''how many seconds the poster threads should put records into
the stream [default: 30]''')
    parser.add_argument('--record_file', type=str, default=None,
        help='''the file whose contents to use as a record''')
    parser.add_argument('--quiet', action='store_true', default=False,
        help='''reduce console output to just initialization info''')
    parser.add_argument('--delete_stream', action='store_true', default=False,
        help='''delete the Kinesis stream matching the given stream_name''')
    parser.add_argument('--describe_only', action='store_true', default=False,
        help='''only describe the Kinesis stream matching the given stream_name''')

    threads = []
    args = parser.parse_args()
    kinesis = boto.kinesis.connect_to_region(region_name = args.region)
    if (args.delete_stream):
        # delete the given Kinesis stream name
        kinesis.delete_stream(stream_name=args.stream_name)
    else:
        start_time = datetime.datetime.now()

        if args.describe_only is True:
            # describe the given Kinesis stream name
            stream = kinesis.describe_stream(args.stream_name)
            print (json.dumps(stream, sort_keys=True, indent=2,
                separators=(',', ': ')))
        else:
            stream = get_or_create_stream(args.stream_name, args.shard_count)
            # Create a KinesisPoster thread up to the poster_count value
            for pid in xrange(args.poster_count):
                # create poster name per poster thread
                poster_name = 'shard_poster:%s' % pid
                # create partition key per poster thread
                part_key = args.partition_key + '-' + str(pid)
                poster = KinesisPoster(
                    stream_name=args.stream_name,
                    partition_key=part_key,  # poster's partition key
                    poster_time=args.poster_time,
                    name=poster_name,  # thread name
                    filename=args.record_file,
                    quiet=args.quiet)
                poster.daemon = True
                threads.append(poster)
                print ('starting: ', poster_name)
                poster.start()

            # Wait for all threads to complete
            for t in threads:
                t.join()

        finish_time = datetime.datetime.now()
        duration = (finish_time - start_time).total_seconds()
        total_records = sum_posts(threads)
        print ("-=> Exiting Poster Main <=-")
        print ("  Total Records:", total_records)
        print ("     Total Time:", duration)
        print ("  Records / sec:", total_records / duration)
