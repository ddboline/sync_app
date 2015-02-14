#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    FileCache class, cache objects to pickle file
'''

import os, hashlib
import gzip
try:
    import cPickle as pickle
except ImportError:
    import pickle

from sync_app.file_list import FileInfo, FileList
from sync_app.util import run_command

class FileListCache(object):
    ''' class to manage caching objects '''
    def __init__(self, pickle_file=''):
        self.pickle_file = pickle_file
        self.cache_file_list_dict = {}
        self.pickle_file_is_modified = False
        self.do_update = False
    
    def read_pickle_object_in_file(self):
        ''' read python object from gzipped pickle file '''
        outobj = None
        if os.path.exists(self.pickle_file):
            with gzip.open(self.pickle_file, 'rb') as pkl_file:
                outobj = pickle.load(pkl_file)
        return outobj
        
    def write_pickle_object_to_file(self, inpobj):
        ''' write python object to gzipped pickle file '''
        with gzip.open('%s.tmp' % self.pickle_file, 'wb') as pkl_file:
            pickle.dump(inpobj, pkl_file, pickle.HIGHEST_PROTOCOL)
        run_command('mv %s.tmp %s' % (self.pickle_file, self.pickle_file))
        return True

    def get_cache_file_list(self, file_list_obj=None):
        if not file_list_obj:
            file_list_obj = FileList()
        _temp = self.read_pickle_object_in_file()
        if _temp:
            self.cache_file_list_dict = _temp
        for finfo in self.cache_file_list_dict.values():
            file_list_obj.append(finfo)
        return file_list_obj

    def write_cache_file_list(self, file_list=None):
        if not file_list:
            return False
        for fileinfo in file_list:
            fn = fileinfo.filename
            if fn not in self.cache_file_list_dict:
                self.cache_file_list_dict[fn] = fileinfo
        return self.write_pickle_object_to_file(self.cache_file_list_dict)
