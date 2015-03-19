#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    Utility functions
'''
import os
import hashlib

from sync_app.util import run_command, cleanup_path
from sync_app.file_cache import FileListCache

def get_md5_old(fname):
    if not os.path.exists(fname):
        return None
    m = hashlib.md5()
    with open(fname, 'r') as infile:
        for line in infile:
            m.update(line)
    return m.hexdigest()

def get_md5(fname):
    if not os.path.exists(fname):
        return None
    try:
        return run_command('md5sum "%s" 2> /dev/null' % cleanup_path(fname), do_popen=True).read().split()[0]
    except IndexError:
        return get_md5_old(fname)

def build_gdrive_index():
    from sync_app.file_list_gdrive import FileListGdrive
    
    fcache = FileListCache(pickle_file='%s/.gdrive_file_list_cache.pkl.gz' % os.getenv('HOME'))
    flist = FileListGdrive()
    #### always rebuild index (gdriveid isn't apparently persistent, also nothing saved by caching)
    #flist = fcache.get_cache_file_list(file_list_class=FileListGdrive)
    print 'update cache'
    flist.fill_file_list_gdrive()
    print 'save cache'
    fcache.write_cache_file_list(flist.filelist)

def build_s3_index():
    from sync_app.file_list_s3 import FileListS3

    fcache = FileListCache(pickle_file='%s/.s3_file_list_cache.pkl.gz' % os.getenv('HOME'))
    flist = FileListS3()
    flist = fcache.get_cache_file_list(file_list_class=FileListS3)
    flist.fill_file_list_s3()
    fcache.write_cache_file_list(flist.filelist)

def build_local_index(directories=None, rebuild_index=False):
    from sync_app.file_list_local import FileListLocal

    if not directories:
        return False
    fcache = FileListCache(pickle_file='%s/.local_file_list_cache.pkl.gz' % os.getenv('HOME'))
    flist = FileListLocal()
    if not rebuild_index:
        flist = fcache.get_cache_file_list(file_list_class=FileListLocal)
    for direc in directories:
        flist.fill_file_list_local(directory=direc)
    fcache.write_cache_file_list(flist.filelist)
