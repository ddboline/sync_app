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
from sync_app.file_list_gdrive import FileInfoGdrive, FileListGdrive
from sync_app.gdrive_instance import GdriveInstance

TEST_FILE = 'tests/test_dir/hello_world.txt'

class TestSyncApp(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        if os.path.exists('.tmp_file_list_cache.pkl.gz'):
            os.remove('.tmp_file_list_cache.pkl.gz')
        pass

    def test_file_info_local(self):
        finfo = FileInfoLocal(fn=TEST_FILE)
        output = ('%s' % finfo).replace(CURDIR, '')
        #print 'finfo', output
        m = hashlib.md5()
        m.update(output)
        self.assertEqual(m.hexdigest(), '216c600e877f238202dec92c9a235648')

    def test_file_list_local(self):
        flist = FileListLocal()
        flist.fill_file_list_local(directory='tests/test_dir')
        output = []
        for fl in flist.filelist:
            output.append(('%s' % fl).replace(CURDIR, ''))
        output = sorted(output)
        #print 'file_list', '\n'.join(output)
        m = hashlib.md5()
        for out in sorted(output):
            m.update(out)
        self.assertEqual(m.hexdigest(), '51e640e2ae74efaa09a9fbe4fd703203')

    def test_file_list_cache(self):
        flist = FileListLocal()
        flist.fill_file_list_local(directory='tests/test_dir')
        fcache = FileListCache(pickle_file='.tmp_file_list_cache.pkl.gz')
        fcache.write_cache_file_list(flist.filelist)
        del flist
        flist = fcache.get_cache_file_list()
        output = []
        for fl in flist.filelist:
            output.append(('%s' % fl).replace(CURDIR, ''))
        output = sorted(output)
        #print 'file_cache', '\n'.join(output)
        m = hashlib.md5()
        for out in sorted(output):
            m.update(out)
        self.assertEqual(m.hexdigest(), '51e640e2ae74efaa09a9fbe4fd703203')


if __name__ == '__main__':
    unittest.main()
