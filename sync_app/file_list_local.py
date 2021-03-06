#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    extract FileInfo object for local files
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os

from sync_app.util import walk_wrapper
from sync_app.file_list import FileList
from sync_app.file_info_local import FileInfoLocal


class FileListLocal(FileList):
    """ File Info Local"""

    def __init__(self, filelist=None, directory=None, cache_file_list=None, do_debug=False):
        """ Init Function """
        FileList.__init__(self, filelist=filelist, basedir=directory, filelist_type='local')
        self.cache_file_list = cache_file_list
        self.do_debug = do_debug

    def fill_file_list(self, directory):
        """ Fill local file list """

        def parse_dir(_, path, filelist):
            """ Parse directory, fill FileInfo object """
            for fn_ in filelist:
                finfo = None
                fullfn = os.path.abspath('%s/%s' % (path, fn_))
                fullfn = fullfn.replace('//', '/')
                if os.path.isfile(fullfn):
                    fs_ = os.stat(fullfn)

                    if self.cache_file_list and \
                            fn_ in self.cache_file_list.filelist_name_dict:
                        flist_ = self.cache_file_list.filelist_name_dict
                        for finf_ in flist_[fn_]:
                            if finf_.filename == fullfn:
                                self.append(finf_)

                    if fn_ in self.filelist_name_dict:
                        for ffn in self.filelist_name_dict[fn_]:
                            if finfo:
                                continue
                            if fullfn == ffn.filename:
                                mt0 = int(fs_.st_mtime)
                                mt1 = int(ffn.filestat.st_mtime)
                                if mt0 > mt1:
                                    finfo = FileInfoLocal(fn=fullfn)
                                else:
                                    finfo = ffn
                    if not finfo:
                        finfo = FileInfoLocal(fn=fullfn)
                    self.append(finfo)

        if type(directory) == list:
            for d__ in directory:
                if os.path.isdir(d__):
                    walk_wrapper(d__, parse_dir, None)
        else:
            if os.path.isdir(directory):
                walk_wrapper(directory, parse_dir, None)

        self.fill_hash_dicts()
