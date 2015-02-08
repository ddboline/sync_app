#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

class FileInfo(object):
    ''' file info class '''
    __slots__ = ['filename', 'pathname', 'hostname', 'urlname', 'md5sum', 'filestat']

    stat_attrs = ('st_atime', 'st_blksize', 'st_blocks', 'st_ctime', 'st_dev', 'st_gid', 'st_ino', 'st_mode', 'st_mtime', 'st_nlink', 'st_rdev', 'st_size', 'st_uid')

    def __init__(self, fn='', pn='', hn='localhost', url='', md5='', fs=None):
        self.filename = fn
        self.pathname = pn
        self.hostname = hn
        self.urlname = url
        self.md5sum = md5
        self.filestat = fs
        if hn == 'localhost' and os.path.exists('%s/%s' % (self.pathname, self.filename)):
            _md5 = get_md5_full('%s/%s' % (self.pathname, self.filename))
            self.md5sum = _md5
            _fstat = os.stat(self.fullfilename)
            self.filestat = {attr: getattr(_fstat, attr) for attr in self.stat_attrs}

    def __repr__(self):
        return '<FileInfo(fn=%s, hs=%s, md5=%s, size=%s>' % (self.fullfilename,
                                                             self.hostname, self.md5sum, self.filestat.st_size)

class FileList(object):
    ''' file list class '''
    def __init__(self, basepath='', subdirectories=[]):
        if basepath:
            self.basepath = basepath
        else:
            self.basepath = '.'
        if subdirectories:
            self.subdirs = ['%s/%s' % (self.basepath, subdirectories)]
        else:
            self.subdirs = [self.basepath]
        self.filelist_dict = {}
