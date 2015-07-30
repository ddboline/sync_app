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

from .sync_utils import get_md5

from .file_info import FileInfo

class FileInfoLocal(FileInfo):
    """ File Info Local """

    def __init__(self, fn='', md5='', fs=None, in_tuple=None):
        """ Init function """
        absfn = os.path.abspath(fn)
        if not os.path.exists(absfn):
            print('ERROR')
            return False
        _url = 'file://%s' % absfn
        FileInfo.__init__(self, fn=absfn, url=_url, md5=md5, fs=fs,
                          in_tuple=in_tuple)

    def get_md5(self):
        """ Wrapper around sync_utils.get_md5 """
        if os.path.exists(self.filename):
            return get_md5(self.filename)
        else:
            return FileInfo.get_md5(self)

    def get_stat(self):
        """ Wrapper around os.stat """
        if os.path.exists(self.filename):
            return os.stat(self.filename)
        else:
            return FileInfo.get_stat(self)
