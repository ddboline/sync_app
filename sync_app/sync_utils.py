#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Utility functions
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import argparse
from apiclient.errors import HttpError

from sync_app.file_cache import FileListCache
from sync_app.file_sync import FileSync
from sync_app.util import MIMETYPE_SUFFIXES, GOOGLEAPP_MIMETYPES

try:
    from apiclient.errors import UnknownFileType
except ImportError:

    class UknownFileType(Exception):
        """ dummy exception """
        pass


LOCAL_DISKS = ('/home/ddboline', '/media/sabrent2000', '/media/caviar2000', '/media/western2000')
LOCAL_DIRECTORIES = ('Documents/AudioBooks', 'Documents/mp3', 'Documents/podcasts',
                     'Documents/video', 'D0_Backup')


def build_onedrive_index(searchstr=None, verbose=True):
    """ build OneDrive index """
    from sync_app.onedrive_instance import OneDriveInstance
    from sync_app.file_list_onedrive import FileListOneDrive

    onedrive = OneDriveInstance()
    flist = FileListOneDrive(onedrive=onedrive)
    #### always rebuild index
    if verbose:
        print('download file metadata')
    flist.fill_file_list(searchstr=searchstr, verbose=verbose)
    return flist


def build_box_index(searchstr=None, verbose=True):
    """ build Box index """
    from sync_app.box_instance import BoxInstance
    from sync_app.file_list_box import FileListBox

    box = BoxInstance()
    flist = FileListBox(box=box)
    #### always rebuild index
    if verbose:
        print('download file metadata')
    flist.fill_file_list(searchstr=searchstr, verbose=verbose)
    return flist


def build_gdrive_index(searchstr=None, verbose=True):
    """ build GDrive index """
    from sync_app.gdrive_instance import GdriveInstance
    from sync_app.file_list_gdrive import FileListGdrive

    gdrive = GdriveInstance()
    flist = FileListGdrive(gdrive=gdrive)
    #### always rebuild index
    if verbose:
        print('download file metadata')
    flist.fill_file_list(searchstr=searchstr, verbose=verbose)
    return flist


def build_s3_index():
    """ build S3 index """
    from sync_app.s3_instance import S3Instance
    from sync_app.file_list_s3 import FileListS3

    s3_ = S3Instance()
    flist = FileListS3(s3=s3_)
    #### always rebuild index
    print('download file metadata')
    flist.fill_file_list()
    return flist


def build_local_index(directories=None, rebuild_index=False):
    """ build local index """
    from sync_app.file_list_local import FileListLocal

    if not directories:
        return False
    fcache = FileListCache(pickle_file='%s/.local_file_list_cache.pkl.gz' % os.getenv('HOME'))
    flist_cache = None
    if not rebuild_index:
        flist_cache = fcache.get_cache_file_list(file_list_class=FileListLocal)
    flist = FileListLocal(cache_file_list=flist_cache)
    print('index local directories')
    for direc in directories:
        print('directory', direc)
        flist.fill_file_list(directory=direc)
    print('write cache')
    fcache.write_cache_file_list(flist)
    return flist


def sync_gdrive(dry_run=False, delete_file=None, rebuild_index=False):
    """ build gdrive index """
    if delete_file:
        for df_ in delete_file:
            print('delete %s' % df_)
            if not dry_run and os.path.exists(df_):
                os.remove(df_)

    from sync_app.file_list_gdrive import BASE_DIR as BASE_DIR_GDRIVE
    print('build gdrive')
    flist_gdrive = build_gdrive_index()
    print('build local gdrive')
    flist_local = build_local_index(directories=[BASE_DIR_GDRIVE], rebuild_index=rebuild_index)
    fsync = FileSync(flists=[flist_gdrive, flist_local])

    def upload_file(finfo):
        """ callback to upload to gdrive """
        print('upload', finfo.filename, finfo)
        if not dry_run:
            try:
                return flist_gdrive.upload_file(finfo.filename)
            except UnknownFileType:
                print('unknown file type', finfo.filename)
                return

    def download_file(finfo):
        """ callback to download from gdrive """
        if delete_file and finfo.filename in delete_file:
            print('delete %s' % finfo.filename)
            if not dry_run:
                return finfo.delete()
        else:
            if finfo.mimetype in ('application/vnd.google-apps.map',
                                  'application/vnd.google-apps.form'):
                return False
            fname = finfo.filename
            if (finfo.mimetype in GOOGLEAPP_MIMETYPES or finfo.mimetype in MIMETYPE_SUFFIXES):
                mtype = GOOGLEAPP_MIMETYPES.get(finfo.mimetype, finfo.mimetype)
                ext = MIMETYPE_SUFFIXES[mtype]
                if not fname.lower().endswith(ext.lower()):
                    fname = '%s.%s' % (fname, ext)
                if fname.lower().endswith('.{ext}.{ext}'.format(ext=ext)):
                    print("don't download", finfo.filename, fname, ext)
                    return False
            print('download', finfo.urlname, fname, finfo.mimetype)

            mimetype_set = {
                ('application/vnd.google-apps.document', 'odt',
                 'maverick_packages_dileptoneee.txt.odt'),
                ('application/vnd.google-apps.spreadsheet', 'xlsx', 'Race Times.xlsx'),
                ('application/vnd.google-apps.presentation', 'pdf', 'Scalla_Xrootd.pdf'),
            }
            
            for mimetype, ext, fname_ in mimetype_set:
                if finfo.mimetype == mimetype:
                    basename = finfo.filename.split('/')[-1]
                    parent = flist_gdrive[fname_][0]
                    newpid = parent.parentid
                    if flist_local.filelist_name_dict.get(basename + '.' + ext) and finfo.parentid and finfo.parentid != newpid:
                        print(finfo)
                        print(parent)
                        finfo.gdrive.set_parent_id(finfo.gdriveid, newpid)
                        if basename + '.' + ext in flist_gdrive.filelist_name_dict:
                            _tmp = flist_gdrive.filelist_name_dict[basename + '.' + ext][0]
                            finfo.gdrive.set_parent_id(_tmp.gdriveid, newpid)
            if finfo.mimetype in GOOGLEAPP_MIMETYPES:
                return False
            if flist_local.filelist_name_dict.get(finfo.filename.split('/')[-1] + '.' + MIMETYPE_SUFFIXES.get(finfo.mimetype)):
                return False
            print(flist_gdrive, flist_local)

            if not dry_run and finfo.mimetype:
                try:
                    return finfo.download()
                except HttpError as exc:
                    print(exc, finfo.mimetype)
                    return False
        return

    fsync.compare_lists(callback0=download_file, callback1=upload_file)


def sync_onedrive(dry_run=False, delete_file=None, rebuild_index=False):
    """ build onedrive index """
    if delete_file:
        for df_ in delete_file:
            print('delete %s' % df_)
            if not dry_run and os.path.exists(df_):
                os.remove(df_)

    from sync_app.file_list_onedrive import BASE_DIR as BASE_DIR_ONEDRIVE
    print('build onedrive')
    flist_onedrive = build_onedrive_index()
    print('build local onedrive')
    flist_local = build_local_index(directories=[BASE_DIR_ONEDRIVE], rebuild_index=rebuild_index)
    fsync = FileSync(flists=[flist_onedrive, flist_local])

    def upload_file(finfo):
        """ callback to upload to onedrive """
        print('upload', finfo.filename)
        if not dry_run:
            try:
                return flist_onedrive.upload_file(finfo.filename)
            except UnknownFileType:
                return

    def download_file(finfo):
        """ callback to download from onedrive """
        if delete_file and finfo.filename in delete_file:
            print('delete %s' % finfo.filename)
            if not dry_run:
                return finfo.delete()
        else:
            print('download', finfo.urlname, finfo.filename)
            if not dry_run:
                print('not dry_run %s' % finfo)
                return finfo.download()
        return

    fsync.compare_lists(callback0=download_file, callback1=upload_file, use_sha1=True)


def sync_box(dry_run=False, delete_file=None, rebuild_index=False):
    """ build box index """
    if delete_file:
        for df_ in delete_file:
            print('delete %s' % df_)
            if not dry_run and os.path.exists(df_):
                os.remove(df_)

    from sync_app.file_list_box import BASE_DIR as BASE_DIR_BOX
    print('build box')
    flist_box = build_box_index()
    print('build local box')
    flist_local = build_local_index(directories=[BASE_DIR_BOX], rebuild_index=rebuild_index)
    fsync = FileSync(flists=[flist_box, flist_local])

    def upload_file(finfo):
        """ callback to upload to box """
        print('upload', finfo.filename)
        if not dry_run:
            try:
                return flist_box.upload_file(finfo.filename)
            except UnknownFileType:
                return

    def download_file(finfo):
        """ callback to download from box """
        if delete_file and finfo.filename in delete_file:
            print('delete %s' % finfo.filename)
            if not dry_run:
                return finfo.delete()
        else:
            print('download', finfo.urlname, finfo.filename)
            if not dry_run:
                print('not dry_run %s' % finfo)
                return finfo.download()
        return

    fsync.compare_lists(callback0=download_file, callback1=upload_file, use_sha1=True)


def sync_s3(dry_run=False, delete_file=None, rebuild_index=False):
    """ sync with s3 """
    if delete_file:
        for df_ in delete_file:
            if os.path.exists(df_):
                print('delete %s' % df_)
                if not dry_run:
                    os.remove(df_)

    from sync_app.file_list_s3 import BASE_DIR as BASE_DIR_S3
    print('build s3')
    flist_s3 = build_s3_index()
    print('build local s3')
    flist_local = build_local_index(directories=[BASE_DIR_S3], rebuild_index=rebuild_index)
    fsync = FileSync(flists=[flist_s3, flist_local])

    def upload_file(finfo):
        """ callback to upload to S3 """
        fn_ = finfo.filename
        _tmp = fn_.replace(BASE_DIR_S3 + '/', '')
        bn_ = _tmp.split('/')[0]
        kn_ = _tmp.replace(bn_ + '/', '')
        print('upload', bn_, kn_, fn_)
        if not dry_run:
            flist_s3.s3_.upload(bn_, kn_, fn_)

    def download_file(finfo):
        """ callback to download from S3 """
        bn_ = finfo.bucket
        kn_ = finfo.filename
        fn_ = '%s/%s/%s' % (BASE_DIR_S3, bn_, kn_)
        if delete_file and finfo.filename in delete_file:
            print('delete', bn_, kn_, fn_)
            if not dry_run:
                return flist_s3.s3_.delete_key(bn_, kn_)
        else:
            print('download', bn_, kn_, fn_)
            if not dry_run:
                flist_s3.s3_.download(bn_, kn_, fn_)

    fsync.compare_lists(callback0=download_file, callback1=upload_file)


def sync_local(dry_run=False, delete_file=None, rebuild_index=False):
    """ sync local directories """
    if delete_file:
        for df_ in delete_file:
            if os.path.exists(df_):
                print('delete %s' % df_)
                if not dry_run:
                    os.remove(df_)

    def sync_local_directories(ldirectories, ldisks):
        """ sync two local directories """
        for directory in ldirectories:
            flists_local = []
            for disk in ldisks:
                ldir = '/'.join([disk, directory])
                print('build local %s' % ldir)
                flists_local.append(
                    build_local_index(directories=[ldir], rebuild_index=rebuild_index))

            def copy_file0(finfo):
                """ callback """
                for disk in ldisks:
                    print('copy0', finfo.filename, disk, directory)

            def copy_file1(finfo):
                """ callback """
                for disk in ldisks:
                    print('copy1', finfo.filename, disk, directory)

            fsync = FileSync(flists=[flists_local])
            fsync.compare_lists(callback0=copy_file0, callback1=copy_file1)

    sync_local_directories(LOCAL_DIRECTORIES, LOCAL_DISKS)
    sync_local_directories(('dilepton2_backup', 'dilepton_tower_backup'),
                           ('/media/sabrent2000', '/media/caviar2000', '/media/western2000'))


def sync_arg_parse():
    """ parse args """
    commands = ('all', 'gdrive', 'onedrive', 's3', 'box', 'local', 'dry_run', 'delete')
    help_text = 'usage: ./sync.py <%s> [rebuild]' % '|'.join(commands)
    parser = argparse.ArgumentParser(description='sync app')
    parser.add_argument('command', nargs='*', help=help_text)
    args = parser.parse_args()

    do_local, do_gdrive, do_onedrive, do_s3, do_box, do_dry_run, do_rebuild = \
        7*[False]
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
        if arg in ('onedrive', 'all'):
            do_onedrive = True
        if arg in ('box', 'all'):
            do_box = True
        if arg in ('s3', 'all'):
            do_s3 = True
        if arg == 'dry_run':
            do_dry_run = True
        if arg == 'rebuild':
            do_rebuild = True
        if 'delete' in arg:
            for temp_ in arg.split('=')[1].split(','):
                delete_f.append(temp_)

    if do_s3:
        sync_s3(dry_run=do_dry_run, delete_file=delete_f, rebuild_index=do_rebuild)
    if do_gdrive:
        sync_gdrive(dry_run=do_dry_run, delete_file=delete_f, rebuild_index=do_rebuild)
    if do_onedrive:
        sync_onedrive(dry_run=do_dry_run, delete_file=delete_f, rebuild_index=do_rebuild)
    if do_box:
        sync_box(dry_run=do_dry_run, delete_file=delete_f, rebuild_index=do_rebuild)
    if do_local:
        sync_local(dry_run=do_dry_run, delete_file=delete_f, rebuild_index=do_rebuild)

    return


def list_drive_parse():
    """ main routine, parse arguments """
    commands = ('list', 'search', 'upload', 'directories', 'delete')
    cmd = 'list'
    search_strings = []
    parent_directory = None
    number_to_list = -1

    for arg in os.sys.argv:
        if 'list_drive_files' in arg:
            continue
        elif arg in ['h', '--help', '-h']:
            print('list_drive_files <' + '|'.join(commands) +
                  '> <file/key> directory=<id of directory>')
            exit(0)
        elif arg in commands:
            cmd = arg
        elif 'directory=' in arg:
            parent_directory = arg.replace('directory=', '')
        elif arg.startswith('-n'):
            try:
                number_to_list = int(arg.split('-n')[1])
            except ValueError:
                raise
        else:
            try:
                number_to_list = int(arg)
            except ValueError:
                search_strings.append(arg)

    from sync_app.gdrive_instance import GdriveInstance
    from sync_app.file_list_gdrive import FileListGdrive
    gdrive = GdriveInstance(number_to_process=number_to_list)
    flist_gdrive = FileListGdrive(gdrive=gdrive)

    if cmd == 'list':
        flist_gdrive.fill_file_list(verbose=False, number_to_process=number_to_list)
        for key, val in flist_gdrive.filelist_id_dict.items():
            if parent_directory \
                    and parent_directory not in os.path.dirname(val.filename):
                continue
            if val.md5sum:
                print(key, val.filename)
    elif cmd == 'search':
        if search_strings:
            for search_string in search_strings:
                flist_gdrive.fill_file_list(verbose=False, searchstr=search_string)
                for key, val in flist_gdrive.filelist_id_dict.items():
                    if val.md5sum:
                        print(key, val.filename)
    elif cmd == 'directories':
        flist_gdrive.get_folders()
        for key, val in flist_gdrive.directory_name_dict.items():
            if search_strings and not any(st_ in key for st_ in search_strings):
                continue
            export_path = flist_gdrive.get_export_path(val, abspath=False)
            if val.isroot:
                export_path += '/gDrive'
            print(key, '%s/%s' % (export_path, val.filename))
    elif cmd == 'upload':
        flist_gdrive.get_folders()
        for fname in search_strings:
            flist_gdrive.upload_file(fname=fname, pathname=parent_directory)
    elif cmd == 'delete':
        for search_string in search_strings:
            if os.path.exists(search_string):
                fn_ = os.path.basename(search_string)
                flist_gdrive.fill_file_list(verbose=False, searchstr=fn_)
                for key, val in flist_gdrive.filelist_name_dict.items():
                    if fn_ == key:
                        for finf in val:
                            fid_ = finf.gdriveid
                            gdrive.delete_file(fileid=fid_)
            else:
                gdrive.delete_file(fileid=search_string)


def parse_s3_args():
    """ Parse command line arguments """
    from sync_app.s3_instance import S3Instance
    commands = ('list', 'search', 'get', 'upload', 'delete', 'delete_bucket')
    bucket_name = None
    cmd = 'list'
    kname = []
    for arg in os.sys.argv[1:]:
        if 'list_s3' in arg:
            continue
        elif arg in ['h', '--help', '-h']:
            print('get_from_s3 <%s> <bucket|file|key>' % '|'.join(commands))
            exit(0)
        elif arg in commands:
            cmd = arg
        elif 'bucket=' in arg:
            bucket_name = arg.split('=')[1]
        else:
            kname.append(arg)

    s3_ = S3Instance()

    if cmd == 'list' or cmd == 'search':
        if 'bucket' in kname:
            print('\n'.join(s3_.get_list_of_buckets()))
        else:
            if bucket_name:
                for key in s3_.get_list_of_keys(bucket_name=bucket_name, callback_fn=lambda x: 0):
                    if kname and not any(_ in key.key for _ in kname):
                        continue
                    try:
                        print(key.key, key.etag.replace('"', ''), key.last_modified,
                              key.bucket.name)
                    except IOError:
                        raise
            else:
                for bucket_name in s3_.get_list_of_buckets():
                    for key in s3_.get_list_of_keys(
                            bucket_name=bucket_name, callback_fn=lambda x: 0):
                        if kname and not any(_ in key.key for _ in kname):
                            continue
                        try:
                            print(key.key, key.etag.replace('"', ''), key.last_modified,
                                  key.bucket.name)
                        except IOError:
                            raise
    elif cmd == 'get':
        for kn_ in kname:
            s3_.download(bucket_name=bucket_name, key_name=kn_, fname=kn_)
    elif cmd == 'upload':
        for fn_ in kname:
            kn_ = os.path.basename(fn_)
            s3_.upload(bucket_name=bucket_name, key_name=kn_, fname=fn_)
    elif cmd == 'delete':
        for kn_ in kname:
            s3_.delete_key(bucket_name=bucket_name, key_name=kn_)
    elif cmd == 'delete_bucket':
        s3_.delete_bucket(bucket_name=bucket_name)


def list_onedrive_parse():
    """ main routine, parse arguments """
    commands = ('list', 'search', 'upload', 'directories', 'delete')
    cmd = 'list'
    search_strings = []
    parent_directory = None
    number_to_list = -1

    for arg in os.sys.argv:
        if 'list_onedrive_files' in arg:
            continue
        elif arg in ['h', '--help', '-h']:
            print('list_onedrive_files <' + '|'.join(commands) +
                  '> <file/key> directory=<id of directory>')
            exit(0)
        elif arg in commands:
            cmd = arg
        elif 'directory=' in arg:
            parent_directory = arg.replace('directory=', '')
        elif arg.startswith('-n'):
            try:
                number_to_list = int(arg.split('-n')[1])
            except ValueError:
                raise
        else:
            try:
                number_to_list = int(arg)
            except ValueError:
                search_strings.append(arg)

    from sync_app.onedrive_instance import OneDriveInstance
    from sync_app.file_list_onedrive import FileListOneDrive
    onedrive = OneDriveInstance(number_to_process=number_to_list)
    flist_onedrive = FileListOneDrive(onedrive=onedrive)

    if cmd == 'list':
        flist_onedrive.fill_file_list(verbose=False, number_to_process=number_to_list)
        for key, val in flist_onedrive.filelist_id_dict.items():
            if parent_directory \
                    and parent_directory not in os.path.dirname(val.filename):
                continue
            if val.sha1sum:
                print(key, val)
    elif cmd == 'search':
        flist_onedrive.fill_file_list(verbose=False)
        if search_strings:
            for search_string in search_strings:
                for key, val in flist_onedrive.filelist_id_dict.items():
                    if val.sha1sum and search_string in val.filename:
                        print(key, val.filename)
    elif cmd == 'directories':
        onedrive.get_folders(flist_onedrive.append_dir)
        for key, val in flist_onedrive.directory_name_dict.items():
            if search_strings and not any(st_ in key for st_ in search_strings):
                continue
            export_path = flist_onedrive.get_export_path(val, abspath=False)
            print(key, '%s/%s' % (export_path, val.filename))
    elif cmd == 'upload':
        onedrive.get_folders(flist_onedrive.append_dir)
        for fname in search_strings:
            flist_onedrive.upload_file(fname=fname, pathname=parent_directory)
    elif cmd == 'delete':
        flist_onedrive.fill_file_list(verbose=False)
        for search_string in search_strings:
            if os.path.exists(search_string):
                fn_ = os.path.basename(search_string)
                for key, val in flist_onedrive.filelist_name_dict.items():
                    if fn_ == key:
                        for finf in val:
                            fid_ = finf.onedriveid
                            onedrive.delete_file(fileid=fid_)
            else:
                for key, val in flist_onedrive.filelist_name_dict.items():
                    if search_string == key:
                        for finf in val:
                            onedrive.delete_file(fileid=finf.onedriveid)


def list_box_parse():
    """ main routine, parse arguments """
    commands = ('list', 'search', 'upload', 'directories', 'delete')
    cmd = 'list'
    search_strings = []
    parent_directory = None
    number_to_list = -1

    for arg in os.sys.argv:
        if 'list_box_files' in arg:
            continue
        elif arg in ['h', '--help', '-h']:
            print('list_box_files <' + '|'.join(commands) +
                  '> <file/key> directory=<id of directory>')
            exit(0)
        elif arg in commands:
            cmd = arg
        elif 'directory=' in arg:
            parent_directory = arg.replace('directory=', '')
        elif arg.startswith('-n'):
            try:
                number_to_list = int(arg.split('-n')[1])
            except ValueError:
                raise
        else:
            try:
                number_to_list = int(arg)
            except ValueError:
                search_strings.append(arg)

    from sync_app.box_instance import BoxInstance
    from sync_app.file_list_box import FileListBox
    box = BoxInstance(number_to_process=number_to_list)
    flist_box = FileListBox(box=box)

    if cmd == 'list':
        flist_box.fill_file_list(verbose=False, number_to_process=number_to_list)
        for key, val in flist_box.filelist_id_dict.items():
            if parent_directory \
                    and parent_directory not in os.path.dirname(val.filename):
                continue
            if val.sha1sum:
                print(key, val)
    elif cmd == 'search':
        flist_box.fill_file_list(verbose=False)
        if search_strings:
            for search_string in search_strings:
                for key, val in flist_box.filelist_id_dict.items():
                    if val.sha1sum and search_string in val.filename:
                        print(key, val.filename)
    elif cmd == 'directories':
        box.get_folders(flist_box.append_dir)
        for key, val in flist_box.directory_name_dict.items():
            if search_strings and not any(st_ in key for st_ in search_strings):
                continue
            export_path = flist_box.get_export_path(val, abspath=False)
            print(key, '%s/%s' % (export_path, val.filename))
    elif cmd == 'upload':
        box.get_folders(flist_box.append_dir)
        for fname in search_strings:
            flist_box.upload_file(fname=fname, pathname=parent_directory)
    elif cmd == 'delete':
        flist_box.fill_file_list(verbose=False)
        for search_string in search_strings:
            if os.path.exists(search_string):
                fn_ = os.path.basename(search_string)
                for key, val in flist_box.filelist_name_dict.items():
                    if fn_ == key:
                        for finf in val:
                            fid_ = finf.boxid
                            box.delete_file(fileid=fid_)
            else:
                for key, val in flist_box.filelist_name_dict.items():
                    if search_string == key:
                        for finf in val:
                            box.delete_file(fileid=finf.boxid)
