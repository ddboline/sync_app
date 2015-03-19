#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    extract FileInfo object for local files
'''

import os

from sync_app.sync_utils import get_md5

from sync_app.file_list import FileInfo, FileList

class FileInfoLocal(FileInfo):
    def __init__(self, fn='', md5='', fs=None):
        absfn = os.path.abspath(fn)
        if not os.path.exists(absfn):
            print 'ERROR'
            return False
        _url = 'file://%s' % absfn
        FileInfo.__init__(self, fn=absfn, url=_url, md5=md5, fs=fs)

    def get_md5(self):
        if os.path.exists(self.filename):
            return get_md5(self.filename)
        else:
            return None
    
    def get_stat(self):
        if os.path.exists(self.filename):
            return os.stat(self.filename)
        else:
            return None


class FileListLocal(FileList):
    def __init__(self, filelist=None, directory=None, cache_file_list=None, do_debug=False):
        FileList.__init__(self, filelist=filelist, basedir=directory, filelist_type='local')
        self.cache_file_list = cache_file_list
        self.do_debug = do_debug

    def fill_file_list_local(self, directory):
        def parse_dir(arg, path, filelist):
            for fn in filelist:
                finfo = None
                fullfn = os.path.abspath('%s/%s' % (path, fn)).replace('//', '/')
                if os.path.isfile(fullfn):
                    fs = os.stat(fullfn)
                    if fn in self.filelist_name_dict:
                        for ffn in self.filelist_name_dict[fn]:
                            if fullfn == ffn.filename:
                                if fs.st_mtime > ffn.filestat.st_mtime:
                                    finfo = FileInfoLocal(fn=fullfn)
                                    if self.do_debug:
                                        print finfo
                                else:
                                    finfo = ffn
                    if not finfo:
                        finfo = FileInfoLocal(fn=fullfn)
                        if self.do_debug:
                            print finfo
                        self.append(finfo)

        if type(directory) == str:
            if os.path.isdir(directory):
                os.path.walk(directory, parse_dir, None)
        if type(directory) == list:
            for d in directory:
                if os.path.isdir(d):
                    os.path.walk(d, parse_dir, None)
