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

from sync_app.sync_utils import get_md5
from sync_app.file_cache import FileListCache
from sync_app.file_list_local import FileInfoLocal, FileListLocal

TEST_FILE = 'tests/test_dir/hello_world.txt'
TEST_DIR = 'tests/test_dir'
TEST_GDR = 'Amazon-Gift-Card.pdf'

class TestSyncApp(unittest.TestCase):
    """ SyncApp Unit Tests """

    def tearDown(self):
        """ remove temporary pickle file """
        if os.path.exists('.tmp_file_list_cache.pkl.gz'):
            os.remove('.tmp_file_list_cache.pkl.gz')
        pass

    def test_file_info_local(self):
        """ Test FileInfoLocal class """
        finfo = FileInfoLocal(fn=TEST_FILE)
        output = ('%s' % finfo).replace(CURDIR, '')
#        print('finfo', output)
        m = hashlib.md5()
        m.update(output)
        self.assertEqual(m.hexdigest(), 'bb0681fe01c42429d0a7b0994f0d9265')

    def test_file_list_local(self):
        """ Test FileListLocal class """
        flist = FileListLocal()
        flist.fill_file_list_local(directory=TEST_DIR)
        output = []
        for fl in flist.filelist:
            output.append(('%s' % fl).replace(CURDIR, ''))
        output = sorted(output)
#        print('file_list', '\n'.join(output))
        m = hashlib.md5()
        for out in sorted(output):
            m.update(out)
        self.assertEqual(m.hexdigest(), '30eceb5a3d7b9c761651f8b1df5e53b5')

    def test_file_list_cache(self):
        """ Test FileListCache class """
        flist = FileListLocal()
        flist.fill_file_list_local(directory=TEST_DIR)
        fcache = FileListCache(pickle_file='.tmp_file_list_cache.pkl.gz')
        fcache.write_cache_file_list(flist.filelist)
        del flist
        flist = fcache.get_cache_file_list()
        output = []
        for fl in flist.filelist:
            output.append(('%s' % fl).replace(CURDIR, ''))
        output = sorted(output)
#        print('file_cache', '\n'.join(output))
        m = hashlib.md5()
        for out in sorted(output):
            m.update(out)
        self.assertEqual(m.hexdigest(), '30eceb5a3d7b9c761651f8b1df5e53b5')

if __name__ == '__main__':
    unittest.main()
