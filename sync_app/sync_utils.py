#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Utility functions
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import hashlib

from sync_app.util import run_command, cleanup_path
from sync_app.file_cache import FileListCache
from sync_app.file_sync import FileSync

from apiclient.errors import UnknownFileType

LOCAL_DISKS = ('/home/ddboline', '/media/sabrent2000', '/media/caviar2000',
               '/media/western2000')
LOCAL_DIRECTORIES = ('Documents/AudioBooks', 'Documents/mp3',
                     'Documents/podcasts', 'Documents/video', 'D0_Backup')

def get_md5_old(fname):
    """ python only md5 function """
    m = hashlib.md5()
    with open(fname, 'r') as infile:
        for line in infile:
            m.update(line)
    return m.hexdigest()

def get_md5(fname):
    """ system md5 function """
#    print('using md5', fname)
    try:
        return run_command('md5sum "%s" 2> /dev/null' % cleanup_path(fname),
                           do_popen=True).read().split()[0]
    except IndexError:
        return get_md5_old(fname)

def build_gdrive_index():
    """ build GDrive index """
    from sync_app.gdrive_instance import GdriveInstance
    from sync_app.file_list_gdrive import FileListGdrive

    gdrive = GdriveInstance()
    flist = FileListGdrive(gdrive=gdrive)
    #### always rebuild index
    print('download file metadata')
    flist.fill_file_list_gdrive()
    return flist

def build_s3_index():
    """ build S3 index """
    from sync_app.s3_instance import S3Instance
    from sync_app.file_list_s3 import FileListS3

    s3 = S3Instance()
    flist = FileListS3(s3=s3)
    #### always rebuild index
    print('download file metadata')
    flist.fill_file_list_s3()
    return flist

def build_local_index(directories=None, rebuild_index=False):
    """ build local index """
    from sync_app.file_list_local import FileListLocal

    if not directories:
        return False
    fcache = FileListCache(pickle_file='%s/.local_file_list_cache.pkl.gz' %
                           os.getenv('HOME'))
    flist_cache = None
    if not rebuild_index:
        flist_cache = fcache.get_cache_file_list(file_list_class=FileListLocal)
    flist = FileListLocal(cache_file_list=flist_cache)
    print('index local directories')
    for direc in directories:
        print('directory', direc)
        flist.fill_file_list_local(directory=direc)
    print('write cache')
    fcache.write_cache_file_list(flist)
    return flist

def sync_gdrive(dry_run=False):
    """ build gdrive index """
    from sync_app.file_list_gdrive import BASE_DIR as BASE_DIR_GDRIVE
    print('build gdrive')
    flist_gdrive = build_gdrive_index()
    print('build local gdrive')
    flist_local = build_local_index(directories=[BASE_DIR_GDRIVE])
    fsync = FileSync(flists=[flist_gdrive, flist_local])

    def upload_file(finfo):
        """ callback to upload to gdrive """
        print('upload', finfo.filename)
        if not dry_run:
            try:
                flist_gdrive.upload_file(finfo.filename)
            except UnknownFileType:
                return

    def download_file(finfo):
        """ callback to download from gdrive """
        if 'https' in finfo.urlname:
            print('download', finfo.urlname, finfo.filename)
            if not dry_run:
                finfo.download()

    fsync.compare_lists(callback0=download_file, callback1=upload_file)

def sync_s3(dry_run=False):
    """ build s3 index """
    from sync_app.file_list_s3 import BASE_DIR as BASE_DIR_S3
    print('build s3')
    flist_s3 = build_s3_index()
    print('build local s3')
    flist_local = build_local_index(directories=[BASE_DIR_S3])
    fsync = FileSync(flists=[flist_s3, flist_local])

    def upload_file(finfo):
        """ callback to upload to S3 """
        fn_ = finfo.filename
        _tmp = fn_.replace(BASE_DIR_S3 + '/', '')
        bn_ = _tmp.split('/')[0]
        kn_ = _tmp.replace(bn_ + '/', '')
        print(bn_, kn_, fn_)
        if not dry_run:
            flist_s3.s3.upload(bn_, kn_, fn_)

    def download_file(finfo):
        """ callback to download from S3 """
        bn_ = finfo.bucket
        kn_ = finfo.filename
        fn_ = '%s/%s/%s' % (BASE_DIR_S3, bn_, kn_)
        print(bn_, kn_, fn_)
        if not dry_run:
            flist_s3.s3.download(bn_, kn_, fn_)

    fsync.compare_lists(callback0=download_file, callback1=upload_file)

def sync_local(dry_run=False):
    local_dirs = []
    for basedir in LOCAL_DISKS:
        for subdir in LOCAL_DIRECTORIES:
            local_dirs.append('%s/%s' % (basedir, subdir))
    for basedir in ('/media/sabrent2000', '/media/caviar2000',
                    '/media/western2000'):
        for subdir in ('dilepton2_backup', 'dilepton_tower_backup'):
            local_dirs.append('%s/%s' % (basedir, subdir))
    print('build local %s' % ' '.join(local_dirs))
    build_local_index(directories=local_dirs)

    for directory in LOCAL_DIRECTORIES:
        flists_local = []
        for disk in LOCAL_DISKS:
            ldir = '/'.join([disk, directory])
            flists_local.append(build_local_index(directories=[ldir]))
        def copy_file0(finfo):
            print(finfo.filename)
        def copy_file1(finfo):
            print(finfo.filename)
        fsync = FileSync(flists=[flists_local])
        fsync.compare_lists(callback0=copy_file0, callback1=copy_file1)
