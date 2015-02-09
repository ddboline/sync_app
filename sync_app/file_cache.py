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

    def get_cache_file_list(self, directory):
        _temp = self.read_pickle_object_in_file()
        if _temp:
            self.cache_file_list_dict = _temp
        
        def parse_dir(arg, path, filelist):
            for fn in filelist:
                fullfn = ('%s/%s' % (path, fn)).replace('//', '/')
                if os.path.isfile(fullfn):
                    stobj = os.stat(fullfn)
                    if fullfn in arg and arg[fullfn].filestat.st_size == stobj.st_size:
                        continue
                    finfo = FileInfo(fn=fullfn, hn=hostname, fs=stobj)
                    print(finfo)
                    arg[fullfn] = finfo

        if type(directory) == str:
            if os.path.isdir(directory):
                os.path.walk(directory, parse_dir, self.cache_file_list_dict)
            elif os.path.isfile(directory):
                add_file(directory)
        if type(directory) == list:
            for d in directory:
                if os.path.isdir(d):
                    os.path.walk(d, parse_dir, self.cache_file_list_dict)
                elif os.path.isfile(d):
                    add_file(d)
        return FileList(filelist=self.cache_file_list_dict.values())
