#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    S3 Instance class, manage connection to s3
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import boto


def read_keys():
    """ read aws credentials from file, then stick into global variables... """
    with open('%s/.aws/credentials' % os.getenv('HOME'), 'rt') as infile:
        for line in infile:
            if 'aws_access_key_id' in line:
                aws_access_key_id = line.split('=')[-1].strip()
            if 'aws_secret_access_key' in line:
                aws_secret_access_key = line.split('=')[-1].strip()
    return aws_access_key_id, aws_secret_access_key


AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = read_keys()


class S3Instance(object):
    """ S3Instance class to interact with S3 via Boto """

    def __init__(self):
        self.s3_ = boto.connect_s3(
            aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    def get_list_of_buckets(self):
        """ get list of buckets """
        _temp = []
        BLACKLIST = ['py2deb-repo']
        for bucket in self.s3_.get_all_buckets():
            if bucket in BLACKLIST:
                continue
            _temp.append(bucket.name)
        return _temp

    def delete_bucket(self, bucket_name=None):
        """ delete s3 bucket """
        if bucket_name:
            for bucket in self.s3_.get_all_buckets():
                if bucket.name == bucket_name:
                    bucket.delete()
                    return

    def create_bucket(self, bucket_name=None):
        """ create s3 bucket """
        return self.s3_.create_bucket(bucket_name=bucket_name)

    def upload(self, bucket_name, key_name, fname):
        """ upload to s3 bucket """
        bucket = self.s3_.get_bucket(bucket_name)
        key = boto.s3.key.Key(bucket)
        with open(fname, 'rb') as infile:
            key.key = key_name
            return key.set_contents_from_file(infile)

    def download(self, bucket_name, key_name, fname):
        """ download from s3 bucket """
        dname = os.path.dirname(fname)
        if dname and not os.path.exists(dname):
            os.makedirs(dname)
        bucket = self.s3_.get_bucket(bucket_name)
        key = bucket.get_key(key_name)
        return key.get_contents_to_filename(fname)

    def delete_key(self, bucket_name, key_name):
        """ delete key from s3 bucket """
        bucket = self.s3_.get_bucket(bucket_name)
        key = bucket.get_key(key_name)
        return key.delete()

    def get_list_of_keys(self, bucket_name=None, callback_fn=None):
        """ get list of keys """
        list_of_keys = []
        if not callback_fn:
            callback_fn = lambda x: print(x.key)
        if bucket_name:
            buckets = [self.s3_.get_bucket(bucket_name)]
        else:
            buckets = self.s3_.get_all_buckets()
        for bucket in buckets:
            for key in bucket.list():
                callback_fn(key)
                list_of_keys.append(key)
        return list_of_keys
