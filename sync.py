#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    syncing app
'''
import os

from sync_app.file_list_local import FileListLocal
from sync_app.gdrive_instance import GdriveInstance
from sync_app.file_cache import FileListCache
from sync_app.file_list_gdrive import FileListGdrive

from sync_app.file_list_s3 import FileListS3

def parse_gdrive():
    flist = FileListGdrive()
    flist.fill_file_list_gdrive()
    fcache = FileListCache(pickle_file='%s/.gdrive_file_list_cache.pkl.gz' % os.getenv('HOME'))
    fcache.write_cache_file_list(flist.filelist)

def print_gdrive():
    #gdrive = GdriveInstance()
    fcache = FileListCache(pickle_file='%s/.gdrive_file_list_cache.pkl.gz' % os.getenv('HOME'))
    flist = fcache.get_cache_file_list(file_list_class=FileListGdrive)
    n = 0
    for fn, val in flist.filelist_name_dict.items():
        if n > 10:
            return
        finfo = val[0]
        fullname = '%s/%s' % (finfo.exportpath, finfo.filename)
        print fullname, finfo.urlname
        #gdrive.download(finfo.urlname, fullname)
        n += 1

def parse_s3():
    flist = FileListS3()
    flist.fill_file_list_gdrive()
    fcache = FileListCache(pickle_file='%s/.s3_file_list_cache.pkl.gz' % os.getenv('HOME'))
    fcache.write_cache_file_list(flist.filelist)

def print_s3():
    fcache = FileListCache(pickle_file='%s/.s3_file_list_cache.pkl.gz' % os.getenv('HOME'))
    flist = fcache.get_cache_file_list(file_list_class=FileListS3)
    for finfo in flist.filelist[:10]:
        print finfo

def parse_mp3():
    flist = FileListLocal()
    flist.fill_file_list_local(directory='%s/Documents/mp3' % os.getenv('HOME'))
    fcache = FileListCache(pickle_file='%s/.local_file_list_cache.pkl.gz' % os.getenv('HOME'))
    fcache.write_cache_file_list(flist.filelist)

def print_mp3():
    fcache = FileListCache(pickle_file='%s/.local_file_list_cache.pkl.gz' % os.getenv('HOME'))
    flist = fcache.get_cache_file_list(file_list_class=FileListLocal)
    for finfo in flist.filelist[:10]:
        print finfo

if __name__ == '__main__':
    #parse_gdrive()
    #print_gdrive()
    #parse_s3()
    #print_s3()
    parse_mp3()
    print_mp3()
    
    