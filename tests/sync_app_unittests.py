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

from sync_app.file_list_local import FileInfoLocal, FileListLocal

TEST_FILE = 'tests/test_dir/hello_world.txt'

class TestGarminApp(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_file_info_local(self):
        finfo = FileInfoLocal(fn=TEST_FILE)
        output = ('%s' % finfo).replace(CURDIR, '')
        print output
        m = hashlib.md5()
        m.update(output)
        
        self.assertEqual(m.hexdigest(), '84bd4e40788a20e79ef5ead344ff1cd3')
        pass

    def test_file_list_local(self):
        flist = FileListLocal()
        flist.fill_cache_file_list_local(directory='tests/test_dir')
        print flist

if __name__ == '__main__':
    unittest.main()
