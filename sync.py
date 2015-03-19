#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    syncing app
'''
import os

from sync_app.sync_utils import build_gdrive_index, build_s3_index, build_local_index
from sync_app.file_list_local import FileListLocal
from sync_app.gdrive_instance import GdriveInstance
from sync_app.file_cache import FileListCache
from sync_app.file_list_gdrive import FileListGdrive
from sync_app.file_list_s3 import FileListS3

def build_indicies():
    print 'build gdrive'
    build_gdrive_index()
    print 'build s3'
    build_s3_index()

    local_dirs = []
    for basedir in ['/home/ddboline', '/media/sabrent2000', '/media/caviar2000', '/media/western2000']:
        for subdir in ['Documents/AudioBooks', 'Documents/mp3', 'Documents/podcasts', 'Documents/video', 'D0_Backup']:
            local_dirs.append('%s/%s' % (basedir, subdir))
    for basedir in ['/media/sabrent2000', '/media/caviar2000', '/media/western2000']:
        for subdir in ['dilepton2_backup', 'dilepton_tower_backup']:
            local_dirs.append('%s/%s' % (basedir, subdir))
    print 'build local %s' % ' '.join(local_dirs)
    build_local_index(directories=local_dirs, build_local_index=True)

def compare_local():
    flists_ = []
    for basedir in ['/home/ddboline', '/media/sabrent2000', '/media/caviar2000', '/media/western2000']:
        flists_.append('%s/Documents/mp3' % basedir)
    
    fsync = FileSync(flists=flists_)
    fsync.compare_lists()

if __name__ == '__main__':
    build_indicies()
    compare_local()