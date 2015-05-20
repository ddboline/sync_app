#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    extract FileInfo object for local files
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

from sync_app.sync_utils import get_md5

from sync_app.file_list import FileInfo, FileList, StatTuple

class FileInfoLocal(FileInfo):
    """ File Info Local """

    def __init__(self, fn='', md5='', fs=None):
        """ Init function """
        absfn = os.path.abspath(fn)
        if not os.path.exists(absfn):
            print('ERROR')
            return False
        _url = 'file://%s' % absfn
        FileInfo.__init__(self, fn=absfn, url=_url, md5=md5, fs=fs)

    def get_md5(self):
        """ Wrapper around sync_utils.get_md5 """
        if os.path.exists(self.filename):
            return get_md5(self.filename)
        else:
            return ''

    def get_stat(self):
        """ Wrapper around os.stat """
        if os.path.exists(self.filename):
            return os.stat(self.filename)
        else:
            return StatTuple()


class FileListLocal(FileList):
    """ File Info Local"""

    def __init__(self, filelist=None, directory=None, cache_file_list=None,
                 do_debug=False):
        """ Init Function """
        FileList.__init__(self, filelist=filelist, basedir=directory,
                          filelist_type='local')
        self.cache_file_list = cache_file_list
        self.do_debug = do_debug

    def fill_file_list_local(self, directory):
        """ Fill local file list """
        def parse_dir(arg, path, filelist):
            """ Parse directory, fill FileInfo object """
            for fn in filelist:
                finfo = None
                fullfn = os.path.abspath('%s/%s' % (path, fn))
                fullfn = fullfn.replace('//', '/')
                if os.path.isfile(fullfn):
                    fs = os.stat(fullfn)
                    
                    if fn in self.cache_file_list.filelist_name_dict:
                        flist_ = self.cache_file_list.filelist_name_dict
                        finf_ = flist_[fn][0]
                        if fn not in self.filelist_name_dict:
                            self.append(finf_)
                    
                    if fn in self.filelist_name_dict:
                        for ffn in self.filelist_name_dict[fn]:
                            if fullfn == ffn.filename:
                                if fs.st_mtime > ffn.filestat.st_mtime:
                                    finfo = FileInfoLocal(fn=fullfn)
                                    if self.do_debug:
                                        print(finfo)
                                else:
                                    finfo = ffn
                    if not finfo:
                        finfo = FileInfoLocal(fn=fullfn)
                        if self.do_debug:
                            print(finfo)
                        self.append(finfo)

        if type(directory) in (str, unicode):
            if os.path.isdir(directory):
                os.path.walk(directory, parse_dir, None)
        if type(directory) == list:
            for d in directory:
                if os.path.isdir(d):
                    os.path.walk(d, parse_dir, None)
