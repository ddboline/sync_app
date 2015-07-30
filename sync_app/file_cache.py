#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    FileCache class, cache objects to pickle file
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import gzip
try:
    import cPickle as pickle
except ImportError:
    import pickle

from .file_info import FileInfo
from .file_list import FileList
from .util import run_command

class FileListCache(object):
    """ class to manage caching objects """
    def __init__(self, pickle_file=''):
        self.pickle_file = pickle_file
        self.cache_file_list_dict = {}

    @property
    def cache_file_list_dict(self):
        return self.__cache_file_list_dict

    @cache_file_list_dict.setter
    def cache_file_list_dict(self, dict_):
        """
            check that we have a dict-like object
            which can be set to FileInfo object
        """
        dict_['DUMMYKEY'] = FileInfo()
        dict_.pop('DUMMYKEY')
        self.__cache_file_list_dict = dict_

    def read_pickle_object_in_file(self):
        """ read python object from gzipped pickle file """
        outobj = None
        if os.path.exists(self.pickle_file):
            with gzip.open(self.pickle_file, 'rb') as pkl_file:
                outobj = pickle.load(pkl_file)
        return outobj

    def write_pickle_object_to_file(self, inpobj):
        """ write python object to gzipped pickle file """
        with gzip.open('%s.tmp' % self.pickle_file, 'wb') as pkl_file:
            pickle.dump(inpobj, pkl_file, pickle.HIGHEST_PROTOCOL)
        run_command('mv %s.tmp %s' % (self.pickle_file, self.pickle_file))
        return True

    def get_cache_file_list(self, file_list_obj=None,
                            file_info_class=FileInfo,
                            file_list_class=FileList):
        """ read list from cache file """
        if not file_list_obj:
            file_list_obj = file_list_class()
        temp_ = self.read_pickle_object_in_file()
        if temp_:
            for tup_ in temp_:
                finf_ = file_info_class(in_tuple=tup_)
                fn_ = finf_.filename
                self.cache_file_list_dict[fn_] = finf_
                file_list_obj.append(finf_)
        return file_list_obj

    def add_filelist_to_cache(self, file_list=None):
        if not file_list:
            return False
        for fileinfo in file_list:
            fn = fileinfo.filename
            self.cache_file_list_dict[fn] = fileinfo

    def write_cache_file_list(self, file_list=None):
        if file_list:
            self.add_filelist_to_cache(file_list)
        cache_list = []
        for finfo in self.cache_file_list_dict.values():
            cache_list.append(finfo.output_cache_tuple())
        return self.write_pickle_object_to_file(tuple(cache_list))
