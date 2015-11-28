#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    extract FileList object for files in AWS S3
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os

from .file_list import FileList
from .file_info_s3 import FileInfoS3

BASE_DIR = '%s/S3' % os.getenv('HOME')


class FileListS3(FileList):
    """ File list for S3 """

    def __init__(self, filelist=None, bucket=None, s3=None):
        """ Init function """
        FileList.__init__(self, filelist=filelist, basedir=bucket,
                          filelist_type='s3')
        self.s3_ = s3
        self.filelist_key_dict = {}

    def __getitem__(self, key):
        if key in self.filelist_key_dict:
            return self.filelist_key_dict[key]
        else:
            return FileList.__getitem__(self, key)

    def append_item(self, item):
        """ append S3 item to filelist """
        finfo = FileInfoS3(item=item)
        if finfo.filename in self:
            for ffn in self.filelist_name_dict[finfo.filename]:
                if ffn.md5sum == finfo.md5sum:
                    return self.filelist_name_dict[finfo.filename]
        self.append(finfo)
        self.filelist_key_dict[finfo.filename] = finfo
        return finfo

    def fill_file_list(self, bucket=None):
        """ fill s3 filelist  """
        self.s3_.get_list_of_keys(bucket_name=bucket,
                                  callback_fn=self.append_item)
        self.fill_hash_dicts()
