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

def get_md5_old(fname):
    m = hashlib.md5()
    with open(fname, 'r') as infile:
        for line in infile:
            m.update(line)
    return m.hexdigest()

def get_md5(fname):
    try:
        return run_command('md5sum "%s" 2> /dev/null' % cleanup_path(fname),
                           do_popen=True).read().split()[0]
    except IndexError:
        return get_md5_old(fname)

def build_gdrive_index():
    from sync_app.file_list_gdrive import FileListGdrive

    fcache = FileListCache(pickle_file='%s/.gdrive_file_list_cache.pkl.gz' %
                           os.getenv('HOME'))
    flist = FileListGdrive()
    #### always rebuild index 
    ### (gdriveid isn't apparently persistent, also nothing saved by caching)
    print('update cache')
    flist.fill_file_list_gdrive()
    print('save cache')
    fcache.write_cache_file_list(flist.filelist)

def build_s3_index():
    from sync_app.file_list_s3 import FileListS3

    fcache = FileListCache(pickle_file='%s/.s3_file_list_cache.pkl.gz' %
                           os.getenv('HOME'))
    flist = FileListS3()
    flist = fcache.get_cache_file_list(file_list_class=FileListS3)
    flist.fill_file_list_s3()
    fcache.write_cache_file_list(flist.filelist)

def build_local_index(directories=None, rebuild_index=False):
    from sync_app.file_list_local import FileListLocal

    if not directories:
        return False
    fcache = FileListCache(pickle_file='%s/.local_file_list_cache.pkl.gz' %
                           os.getenv('HOME'))
    flist = FileListLocal()
    if not rebuild_index:
        flist = fcache.get_cache_file_list(file_list_class=FileListLocal)
    for direc in directories:
        flist.fill_file_list_local(directory=direc)
    fcache.write_cache_file_list(flist.filelist)

def build_indicies():
    print('build gdrive')
    build_gdrive_index()
#    print('build s3')
#    build_s3_index()
#
#    local_dirs = []
#    for basedir in ['/home/ddboline', '/media/sabrent2000',
#                    '/media/caviar2000', '/media/western2000']:
#        for subdir in ['Documents/AudioBooks', 'Documents/mp3',
#                       'Documents/podcasts', 'Documents/video', 'D0_Backup']:
#            local_dirs.append('%s/%s' % (basedir, subdir))
#    for basedir in ['/media/sabrent2000', '/media/caviar2000',
#                    '/media/western2000']:
#        for subdir in ['dilepton2_backup', 'dilepton_tower_backup']:
#            local_dirs.append('%s/%s' % (basedir, subdir))
#    print('build local %s' % ' '.join(local_dirs))
#    build_local_index(directories=local_dirs)

def compare_local(rebuild_index=True, directories=None):
    from sync_app.file_list_local import FileListLocal

    local_dirs = []
    for basedir in ['/home/ddboline', '/media/sabrent2000',
                    '/media/caviar2000', '/media/western2000']:
        local_dirs.append('%s/Documents/mp3' % basedir)

    fcache = FileListCache(pickle_file='%s/.local_file_list_cache.pkl.gz'
                           % os.getenv('HOME'))
    fcache.get_cache_file_list(file_list_class=FileListLocal)
    flists_ = []
    for d in local_dirs:
        flist = FileListLocal()
        flist.fill_file_list_local(directory=d)
        flists_.append(flist)

    flist = FileListLocal()
    if not rebuild_index:
        flist = fcache.get_cache_file_list(file_list_class=FileListLocal)
    for direc in directories:
        flist.fill_file_list_local(directory=direc)

    fsync = FileSync(flists=flists_)
    fsync.compare_lists()
