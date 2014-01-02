# Copyright 2013-2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.

# Licensed under the Apache License, Version 2.0 (the "License"). You may not 
# use this file except in compliance with the License. A copy of the License 
# is located at

#     http://aws.amazon.com/apache2.0/

# or in the "license" file accompanying this file. This file is distributed on 
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express 
# or implied. See the License for the specific language governing permissions 
# and limitations under the License.

#!/bin/bash

nohup python poster.py my-first-stream --shard_count 10 --poster_count 50 --poster_time 345600 --partition_key Kinesis02 --quiet &
