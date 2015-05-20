#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    S3 Instance class, manage connection to s3
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import boto

def read_keys():
    """ read aws credentials from file, then stick into global variables... """
    with open('%s/.aws/credentials' % os.getenv('HOME'), 'r') as f:
        for line in f:
            if 'aws_access_key_id' in line:
                aws_access_key_id = line.split('=')[-1].strip()
            if 'aws_secret_access_key' in line:
                aws_secret_access_key = line.split('=')[-1].strip()
    return aws_access_key_id, aws_secret_access_key

AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = read_keys()

class S3Instance(object):
    """ S3Instance class to interact with S3 via Boto """
    def __init__(self):
        self.s3 = boto.connect_s3(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    def get_list_of_buckets(self):
        """ get list of buckets """
        _temp = []
        for bucket in self.s3.get_all_buckets():
            _temp.append(bucket.name)
        return _temp

    def get_list_of_keys(self, bucket_name=None, callback_fn=None):
        """ get list of keys """
        if not callback_fn:
            def _temp_fn(x):
                print(x.key)
            callback_fn = _temp_fn
        if bucket_name:
            buckets = [self.s3.get_bucket(bucket_name)]
        else:
            buckets = self.s3.get_all_buckets()
        for bucket in buckets:
            for key in bucket.list():
                callback_fn(key)
        return
