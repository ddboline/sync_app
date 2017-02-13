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
import shutil
import unittest

CURDIR = os.path.abspath(os.curdir)
os.sys.path.append(CURDIR)

from sync_app.util import get_sha1, get_random_hex_string
from sync_app.file_list_box import FileListBox
from sync_app.box_instance import BoxInstance

TEST_FILE = 'tests/test_dir/hello_world.txt'
TEST_DIR = 'tests/test_dir'
TEST_GDR = 'fastcalosim_punch_through_simulation_CERN-THESIS-2011-112.pdf'

HOMEDIR = os.getenv('HOME')


class TestSyncAppBox(unittest.TestCase):
    """ SyncApp Unit Tests """

    def setUp(self):
        self.box = BoxInstance()
        self.test_title = None

    def test_box_list_files(self):
        """ Test BoxInstance.list_files """

        def get_title(item):
            """ callback fn """
            if TEST_GDR in item['name']:
                self.test_title = item['name']

        self.box.list_files(get_title)
        md_ = hashlib.md5()
        if hasattr(self.test_title, 'encode'):
            self.test_title = self.test_title.encode()
        md_.update(self.test_title)
        self.assertEqual(md_.hexdigest(), 'f11ee662020b5b00596e41ec4ab710f6')

    def test_box_upload_search(self):
        """ Test BoxInstance.upload """
        flist_box = FileListBox(box=self.box)

        self.box.get_folders(flist_box.append_dir)
        self.box.list_files(flist_box.append_item)

        for directory, finfo in flist_box.directory_name_dict.items():
            finfo = finfo.values()[0]
            print(directory)
            print(flist_box.get_export_path(finfo))

        flist_box.get_or_create_directory(TEST_DIR)
        test_file = '%s.%06x.txt' % (TEST_FILE, get_random_hex_string(4))
        shutil.copy(TEST_FILE, test_file)
        fid = flist_box.upload_file(test_file, pathname=TEST_DIR)
        print(fid)

        finf_ = flist_box.filelist_id_dict[fid]
        finf_.download()

        fname = '%s/Box/%s' % (HOMEDIR, test_file)

        self.assertEqual(fid, finf_.boxid)

        finf_.delete()
        flist_box.delete_directory(TEST_DIR)
        os.remove(test_file)

        self.assertEqual(flist_box.filelist_id_dict[fid].exportpath,
                         '%s/Box/%s' % (HOMEDIR, TEST_DIR))
        self.assertEqual(flist_box.filelist_id_dict[fid].sha1sum,
                         'a0b65939670bc2c010f4d5d6a0b3e4e4590fb92b')
        self.assertEqual(get_sha1(fname), 'a0b65939670bc2c010f4d5d6a0b3e4e4590fb92b')
        os.remove(fname)

    def test_box_search_directory(self):
        """ Test FileListBox """
        self.box = BoxInstance()
        flist_box = FileListBox()
        self.box.get_folders(flist_box.append_dir)
        flist_box.fix_export_path()
        print(flist_box.directory_name_dict)
        id_ = flist_box.directory_name_dict['Imported'].values()[0].boxid
        val = flist_box.directory_id_dict[id_]
        print(val)
        self.assertEqual(val.exportpath, '%s/Box/Documents' % HOMEDIR)

    def test_box_list_directories(self):
        """ Test FileListBox """
        flist_box = FileListBox(box=self.box)
        self.box.get_folders(flist_box.append_dir)
        flist_box.fix_export_path()
        print(flist_box.directory_name_dict)
        finf_ = flist_box.directory_name_dict['Imported'].values()[0]

        self.assertEqual(finf_.exportpath, '%s/Box/Documents' % HOMEDIR)


if __name__ == '__main__':
    unittest.main()
