#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    Unit tests for sync_app
'''
import os
import re
import hashlib
import unittest

CURDIR = os.path.abspath(os.curdir)
os.sys.path.append(CURDIR)

from sync_app.file_cache import FileListCache
from sync_app.file_list_local import FileInfoLocal, FileListLocal

TEST_FILE = 'tests/test_dir/hello_world.txt'

class TestGarminApp(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        if os.path.exists('.tmp_file_list_cache.pkl.gz'):
            os.remove('.tmp_file_list_cache.pkl.gz')
        pass

    def test_file_info_local(self):
        finfo = FileInfoLocal(fn=TEST_FILE)
        output = ('%s' % finfo).replace(CURDIR, '')
        #print output
        m = hashlib.md5()
        m.update(output)
        self.assertEqual(m.hexdigest(), '41c5f9381ea74a6dbc00047e425054a1')

    def test_file_list_local(self):
        flist = FileListLocal()
        flist.fill_cache_file_list_local(directory='tests/test_dir')
        output = []
        for fl in flist.filelist:
            output.append(('%s' % fl).replace(CURDIR, ''))
        output = sorted(output)
        print '\n'.join(output)
        m = hashlib.md5()
        for out in sorted(output):
            m.update(out)
        self.assertEqual(m.hexdigest(), '73f22ce2c1f4b894fadff79d8574e360')

    def test_file_list_cache(self):
        flist = FileListLocal()
        flist.fill_cache_file_list_local(directory='tests/test_dir')
        fcache = FileListCache(pickle_file='.tmp_file_list_cache.pkl.gz')
        fcache.write_cache_file_list(flist.filelist)
        del flist
        flist = fcache.get_cache_file_list()
        output = []
        for fl in flist.filelist:
            output.append(('%s' % fl).replace(CURDIR, ''))
        output = sorted(output)
        #print '\n'.join(output)
        m = hashlib.md5()
        for out in sorted(output):
            m.update(out)
        self.assertEqual(m.hexdigest(), '73f22ce2c1f4b894fadff79d8574e360')

if __name__ == '__main__':
    unittest.main()
