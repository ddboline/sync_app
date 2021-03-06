#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    module containing FileList class.
    FileList:
        container for list of FileInfo object
        dicts to efficiently search within filelist
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
from collections import defaultdict

FILE_LIST_TYPES = ('local', 'remote', 'gdrive', 's3', 'onedrive', 'box')


class FileList(object):
    """ file list class """

    def __init__(self, filelist=None, filelist_type=None, basedir=None):
        self.filelist = filelist if filelist else {}
        self.filelist_name_dict = defaultdict(list)
        self.filelist_md5_dict = defaultdict(list)
        self.filelist_sha1_dict = defaultdict(list)
        self.filelist_type = filelist_type if filelist_type else 'local'

        self.basedir = basedir if basedir else os.getenv('HOME')
        self.baseurl = 'local://'
        self.fill_dicts()

    @property
    def filelist(self):
        """ filelist getter """
        return self.__filelist

    @filelist.setter
    def filelist(self, val):
        """ make a copy of list, element by element """
        self.__filelist = {}
        for k__, v__ in val.items():
            if k__ not in self.__filelist:
                self.__filelist[k__] = v__

    @property
    def filelist_type(self):
        """ filelist_type getter """
        return self.__filelist_type

    @filelist_type.setter
    def filelist_type(self, val):
        """ throw error if we get unexpected value """
        if val in FILE_LIST_TYPES:
            self.__filelist_type = val
        else:
            raise ValueError

    def __getitem__(self, key):
        """ try to simplify calling a bit... """
        if key in self.filelist_md5_dict:
            return self.filelist_md5_dict.__getitem__(key)
        elif key in self.filelist_sha1_dict:
            return self.filelist_sha1_dict.__getitem__(key)
        elif key in self.filelist_name_dict:
            return self.filelist_name_dict.__getitem__(key)
        else:
            return self.filelist.__getitem__(key)

    def __iter__(self):
        if hasattr(self.filelist, 'itervalues'):
            return self.filelist.itervalues()
        else:
            return iter(self.filelist.values())

    def append(self, file_info_obj):
        """ append to list, fill dicts """
        if not all(
                hasattr(file_info_obj, at) for at in ('filename', 'urlname', 'md5sum', 'filestat')):
            raise ValueError('this object won\'t work')
        ffn_ = file_info_obj.filename
        if ffn_ in self.filelist:
            self.filelist[ffn_] = file_info_obj
            return
        fn_ = os.path.basename(ffn_)
        self.filelist[ffn_] = file_info_obj
        self.filelist_name_dict[fn_].append(file_info_obj)

    def fill_hash_dicts(self):
        for key in self.filelist:
            finfo = self.filelist[key]
            if hasattr(finfo.md5sum, 'result'):
                finfo.md5sum = finfo.md5sum.result()
            if hasattr(finfo.sha1sum, 'result'):
                finfo.sha1sum = finfo.sha1sum.result()
            md5 = finfo.md5sum
            sha1 = finfo.sha1sum
            if md5:
                self.filelist_md5_dict[md5].append(finfo)
            if sha1:
                self.filelist_sha1_dict[sha1].append(finfo)

    def append_item(self, item):
        raise NotImplementedError

    def fill_file_list(self):
        raise NotImplementedError

    def fill_dicts(self):
        """ fill dicts """
        for f__ in self.filelist:
            self.append(f__)


def test_file_list():
    """ test FileList """
    from nose.tools import raises
    tmp = FileList()

    @raises(AttributeError)
    def test_tmp():
        """ ... """
        tmp.filelist = 1

    test_tmp()

    @raises(ValueError)
    def test_tmp1():
        """ ... """
        tmp.append(1)

    test_tmp1()


def test_file_list_add():
    tmp = FileList()
    new_filelist = {'key0': 'val0', 'key1': 'val1'}
    tmp.filelist = new_filelist
