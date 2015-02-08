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

class FileListCache(object):
    ''' class to manage caching objects '''
    def __init__(self, pickle_file=''):
        self.pickle_file = pickle_file
        self.cache_file_list = []
        self.cache_file_md5_dict = {}
        self.cache_file_name_dict = {}
        self.pickle_file_is_modified = False
        self.do_update = False
    
    def read_pickle_object_in_file(self, pickle_file=''):
        ''' read python object from gzipped pickle file '''
        if not pickle_file:
            if not self.pickle_file:
                return None
            else:
                pickle_file = self.pickle_file
        outobj = None
        if os.path.exists(pickle_file):
            with gzip.open(pickle_file, 'rb') as pkl_file:
                outobj = pickle.load(pkl_file)
        return outobj
        
    def write_pickle_object_to_file(self, inpobj, pickle_file=''):
        ''' write python object to gzipped pickle file '''
        if not pickle_file:
            if not self.pickle_file:
                return False
            else:
                pickle_file = self.pickle_file
        with gzip.open('%s.tmp' % pickle_file, 'wb') as pkl_file:
            pickle.dump(inpobj, pkl_file, pickle.HIGHEST_PROTOCOL)
        run_command('mv %s.tmp %s' % (pickle_file, pickle_file))
        return True
