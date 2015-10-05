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

from .util import get_md5

from .file_info import FileInfo


class FileInfoLocal(FileInfo):
    """ File Info Local """

    def __init__(self, fn='', md5='', fs=None, in_tuple=None):
        """ Init function """
        absfn = ''
        _url = ''
        if fn:
            absfn = os.path.abspath(fn)
            if not os.path.isfile(absfn):
                print('ERROR')
                raise TypeError
            _url = 'file://%s' % absfn
        FileInfo.__init__(self, fn=absfn, url=_url, md5=md5, fs=fs,
                          in_tuple=in_tuple)

    def get_md5(self):
        """ Wrapper around sync_utils.get_md5 """
        if os.path.exists(self.filename):
            return get_md5(self.filename)
        else:
            return self.md5sum

    def get_stat(self):
        """ Wrapper around os.stat """
        if os.path.exists(self.filename):
            return os.stat(self.filename)
        else:
            return self.filestat

def test_file_info_local():
    """ Test FileInfoLocal """
    from nose.tools import raises
    @raises(TypeError)
    def test_tmp():
        """ ... """
        FileInfoLocal(fn='apsodfij')
    test_tmp()

    from .file_info import StatTuple
    test_dict = {'st_mtime': 1234567, 'st_size': 7654321}
    fs_ = StatTuple(**test_dict)
    fn_ = 'tests/test_dir/hello_world.txt'
    tmp = '%s' % FileInfoLocal(fn=fn_, md5='8ddd8be4b179a529afa5f2ffae4b9858',
                               fs=fs_)
    test = '<FileInfo(fn=/home/ddboline/setup_files/build/sync_app/tests/' + \
           'test_dir/hello_world.txt, url=file:///home/ddboline/' + \
           'setup_files/build/sync_app/tests/test_dir/hello_world.txt, ' + \
           'md5=8ddd8be4b179a529afa5f2ffae4b9858, size=7654321, ' + \
           'st_mtime=1234567)>'

    assert tmp == test
