#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Unit tests for sync_app
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import hashlib
import unittest

CURDIR = os.path.abspath(os.curdir)
os.sys.path.append(CURDIR)

#from sync_app.sync_utils import get_md5
from sync_app.file_cache import FileListCache
from sync_app.file_info_local import FileInfoLocal
from sync_app.file_list_local import FileListLocal

TEST_FILE = 'tests/test_dir/hello_world.txt'
TEST_DIR = 'tests/test_dir'
TEST_GDR = 'Amazon-Gift-Card.pdf'

class TestSyncAppLocal(unittest.TestCase):
    """ SyncApp Unit Tests """

    def tearDown(self):
        """ remove temporary pickle file """
        if os.path.exists('.tmp_file_list_cache.pkl.gz'):
            os.remove('.tmp_file_list_cache.pkl.gz')
        pass

    def test_file_info_local(self):
        """ Test FileInfoLocal class """
        finfo = FileInfoLocal(fn=TEST_FILE)
        output = '%s %s %s %d' % (finfo.filename, finfo.urlname, finfo.md5sum,
                                  finfo.filestat.st_size)
        output = output.replace(CURDIR, '')
#        print('finfo', output)
        m = hashlib.md5()
        if hasattr(output, 'encode'):
            output = output.encode()
        m.update(output)
        self.assertEqual(m.hexdigest(), '1bfc429c2f36ef5c541742be8aaf934b')

    def test_file_list_local(self):
        """ Test FileListLocal class """
        flist = FileListLocal()
        flist.fill_file_list_local(directory=TEST_DIR)
        output = []
        for fl in flist:
            temp_ = '%s %s %s %d' % (fl.filename, fl.urlname, fl.md5sum,
                                     fl.filestat.st_size)
            output.append(temp_.replace(CURDIR, ''))
        output = sorted(output)
#        print('file_list', '\n'.join(output))
        m = hashlib.md5()
        for out in sorted(output):
            if hasattr(out, 'encode'):
                out = out.encode()
            m.update(out)
        self.assertEqual(m.hexdigest(), 'cd3bf7a0a388d94ef5626fb9d5ca1632')

    def test_file_list_cache(self):
        """ Test FileListCache class """
        flist = FileListLocal()
        flist.fill_file_list_local(directory=TEST_DIR)
        fcache = FileListCache(pickle_file='.tmp_file_list_cache.pkl.gz')
        fcache.write_cache_file_list(flist)
        del flist, fcache

        fcache = FileListCache(pickle_file='.tmp_file_list_cache.pkl.gz')
        flist = fcache.get_cache_file_list()
        output = []
        for fl in flist:
            temp_ = '%s %s %s %d' % (fl.filename, fl.urlname, fl.md5sum,
                                     fl.filestat.st_size)
            output.append(temp_.replace(CURDIR, ''))
        output = sorted(output)
#        print('file_cache', '\n'.join(output))
        m = hashlib.md5()
        for out in sorted(output):
            if hasattr(out, 'encode'):
                out = out.encode()
            m.update(out)
        self.assertEqual(m.hexdigest(), 'cd3bf7a0a388d94ef5626fb9d5ca1632')

#    def test_global_file_cache(self):
#        flist = []
#        with gzip.open('/home/ddboline/.local_file_list_cache.pkl.gz', 'rb') as pklfile:
#            flist = pickle.load(pklfile)
#        for fl_ in flist:
#            if 'Ch5.csv' in fl_[0]:
#                print(fl_)

if __name__ == '__main__':
    unittest.main()
