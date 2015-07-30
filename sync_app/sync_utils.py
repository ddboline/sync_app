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
import argparse

from .util import run_command, cleanup_path
from .file_cache import FileListCache
from .file_sync import FileSync

try:
    from apiclient.errors import UnknownFileType
except:
    class UknownFileType(Exception):
        pass

LOCAL_DISKS = ('/home/ddboline', '/media/sabrent2000', '/media/caviar2000',
               '/media/western2000')
LOCAL_DIRECTORIES = ('Documents/AudioBooks', 'Documents/mp3',
                     'Documents/podcasts', 'Documents/video', 'D0_Backup')

def get_md5_old(fname):
    """ python only md5 function """
    m = hashlib.md5()
    with open(fname, 'rb') as infile:
        for line in infile:
            m.update(line)
    return m.hexdigest()

def get_md5(fname):
    """ system md5 function """
#    print('using md5', fname)
    try:
        with run_command('md5sum "%s" 2> /dev/null' % cleanup_path(fname),
                           do_popen=True) as pop_:
            output = pop_.stdout.read().split()[0]
        return output.decode()
    except IndexError:
        return get_md5_old(fname)

def build_gdrive_index():
    """ build GDrive index """
    from .gdrive_instance import GdriveInstance
    from .file_list_gdrive import FileListGdrive

    gdrive = GdriveInstance()
    flist = FileListGdrive(gdrive=gdrive)
    #### always rebuild index
    print('download file metadata')
    flist.fill_file_list_gdrive()
    return flist

def build_s3_index():
    """ build S3 index """
    from .s3_instance import S3Instance
    from .file_list_s3 import FileListS3

    s3 = S3Instance()
    flist = FileListS3(s3=s3)
    #### always rebuild index
    print('download file metadata')
    flist.fill_file_list_s3()
    return flist

def build_local_index(directories=None, rebuild_index=False):
    """ build local index """
    from .file_list_local import FileListLocal

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

def sync_gdrive(dry_run=False, delete_file=None):
    """ build gdrive index """
    if delete_file:
        for df_ in delete_file:
            print('delete %s' % df_)
            if not dry_run and os.path.exists(df_):
                os.remove(df_)

    from .file_list_gdrive import BASE_DIR as BASE_DIR_GDRIVE
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
                return flist_gdrive.upload_file(finfo.filename)
            except UnknownFileType:
                return

    def download_file(finfo):
        """ callback to download from gdrive """
        if 'https' in finfo.urlname:
            if delete_file and finfo.filename in delete_file:
                print('delete %s' % finfo.filename)
                if not dry_run:
                    return finfo.delete()
            else:
                print('download', finfo.urlname, finfo.filename)
                if not dry_run:
                    return finfo.download()
        return


    fsync.compare_lists(callback0=download_file, callback1=upload_file)

def sync_s3(dry_run=False, delete_file=None):
    """ sync with s3 """
    if delete_file:
        for df_ in delete_file:
            if os.path.exists(df_):
                print('delete %s' % df_)
                if not dry_run:
                    os.remove(df_)

    from .file_list_s3 import BASE_DIR as BASE_DIR_S3
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
        if delete_file and finfo.filename in delete_file:
            print('delete', bn_, kn_, fn_)
            if not dry_run:
                return flist_s3.s3.delete_key(bn_, kn_)
        else:
            print('download', bn_, kn_, fn_)
            if not dry_run:
                flist_s3.s3.download(bn_, kn_, fn_)

    fsync.compare_lists(callback0=download_file, callback1=upload_file)

def sync_local(dry_run=False, delete_file=None):
    """ sync local directories """
    if delete_file:
        for df_ in delete_file:
            if os.path.exists(df_):
                print('delete %s' % df_)
                if not dry_run:
                    os.remove(df_)

    def sync_local_directories(ldirectories, ldisks):
        for directory in ldirectories:
            flists_local = []
            for disk in ldisks:
                ldir = '/'.join([disk, directory])
                print('build local %s' % ldir)
                flists_local.append(build_local_index(directories=[ldir]))

            def copy_file0(finfo):
                print(finfo.filename, disk, directory)

            def copy_file1(finfo):
                print(finfo.filename, disk, directory)

            fsync = FileSync(flists=[flists_local])
            fsync.compare_lists(callback0=copy_file0, callback1=copy_file1)


    sync_local_directories(LOCAL_DIRECTORIES, LOCAL_DISKS)
    sync_local_directories(('dilepton2_backup', 'dilepton_tower_backup'),
                           ('/media/sabrent2000', '/media/caviar2000',
                            '/media/western2000'))

def sync_arg_parse():
    commands = ('all', 'gdrive', 's3', 'local', 'dry_run', 'delete')
    help_text = 'usage: ./sync.py <%s>' % '|'.join(commands)
    parser = argparse.ArgumentParser(description='garmin app')
    parser.add_argument('command', nargs='*', help=help_text)
    args = parser.parse_args()

    do_local, do_gdrive, do_s3, do_dry_run = False, False, False, False
    delete_f = []

    for arg in getattr(args, 'command'):
        if any(arg == x for x in ['h', 'help', '-h', '--help']):
            print('usage: ./garmin.py <%s>' % '|'.join(commands))
            return

    for arg in getattr(args, 'command'):
        if arg in ('local', 'all'):
            do_local = True
        if arg in ('gdrive', 'all'):
            do_gdrive = True
        if arg in ('s3', 'all'):
            do_s3 = True
        if arg == 'dry_run':
            do_dry_run = True
        if 'delete' in arg:
            for temp_ in arg.split('=')[1].split(','):
                delete_f.append(temp_)

    if do_s3:
        sync_s3(dry_run=do_dry_run, delete_file=delete_f)
    if do_gdrive:
        sync_gdrive(dry_run=do_dry_run, delete_file=delete_f)
    if do_local:
        sync_local(dry_run=do_dry_run, delete_file=delete_f)

    return
