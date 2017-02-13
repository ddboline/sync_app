#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" Utility functions """
from __future__ import (absolute_import, division, print_function, unicode_literals)

import os
import hashlib
from subprocess import call, Popen, PIPE

import requests
try:
    requests.packages.urllib3.disable_warnings()
except AttributeError:
    pass

HOMEDIR = os.getenv('HOME')

GOOGLEAPP_MIMETYPES = {
    'application/vnd.google-apps.document':
    'application/vnd.oasis.opendocument.text',
    'application/vnd.google-apps.drawing':
    'image/png',
    'application/vnd.google-apps.presentation':
    'application/pdf',
    'application/vnd.google-apps.spreadsheet':
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
}

MIMETYPE_SUFFIXES = {
    'application/vnd.oasis.opendocument.text': 'odt',
    'image/png': 'png',
    'application/pdf': 'pdf',
    'image/jpeg': 'jpg',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx'
}


class PopenWrapperClass(object):
    """ wrapper around subprocess.Popen """

    def __init__(self, command):
        """ init """
        self.command = command
        self.pop_ = Popen(self.command, shell=True, stdout=PIPE, close_fds=True)

    def __enter__(self):
        """ enter """
        return self.pop_

    def __exit__(self, exc_type, exc_value, traceback):
        """ exit """
        if hasattr(self.pop_, '__exit__'):
            return getattr(self.pop_, '__exit__')(exc_type, exc_value, traceback)
        self.pop_.wait()
        if exc_type or exc_value or traceback:
            return False
        else:
            return True


def run_command(command, do_popen=False, turn_on_commands=True, single_line=False):
    """ wrapper around os.system """
    if not turn_on_commands:
        print(command)
        return command
    elif do_popen:
        if single_line:
            with PopenWrapperClass(command) as pop_:
                return pop_.stdout.read()
        else:
            return PopenWrapperClass(command)
    else:
        return call(command, shell=True)


def cleanup_path(orig_path):
    """ cleanup path string using escape character """
    chars_to_escape = ' ()"[]&,!;$' + "'"
    for ch_ in chars_to_escape:
        orig_path = orig_path.replace(ch_, r'\%c' % ch_)
    return orig_path


def walk_wrapper(direc, callback, arg):
    """ wrapper around os.walk for py2/py3 compatibility """
    if hasattr(os.path, 'walk'):
        os.path.walk(direc, callback, arg)
    elif hasattr(os, 'walk'):
        for dirpath, dirnames, filenames in os.walk(direc):
            callback(arg, dirpath, dirnames + filenames)


def get_md5_old(fname):
    """ python only md5 function """
    md_ = hashlib.md5()
    with open(fname, 'rb') as infile:
        for line in infile:
            md_.update(line)
    return md_.hexdigest()


def get_md5(fname):
    """ system md5 function """
    try:
        with run_command('md5sum "%s" 2> /dev/null' % cleanup_path(fname), do_popen=True) as pop_:
            output = pop_.stdout.read().split()[0]
        return output.decode()
    except IndexError:
        return get_md5_old(fname)


def get_filetype(fname):
    with run_command('file %s' % cleanup_path(fname), do_popen=True) as pop_:
        output = ' '.join(pop_.stdout.read().split()[1:])
    return output.decode()


def test_get_md5():
    """ test get_md5 """
    tmp = get_md5_old('tests/test_dir/hello_world.txt')
    test = '8ddd8be4b179a529afa5f2ffae4b9858'
    assert tmp == test
    tmp = get_md5('tests/test_dir/hello_world.txt')
    assert tmp == test


def get_sha1_old(fname):
    """ python only sha1 function """
    md_ = hashlib.sha1()
    with open(fname, 'rb') as infile:
        for line in infile:
            md_.update(line)
    return md_.hexdigest()


def get_sha1(fname):
    """ system sha1 function """
    try:
        with run_command('sha1sum "%s" 2> /dev/null' % cleanup_path(fname), do_popen=True) as pop_:
            output = pop_.stdout.read().split()[0]
        return output.decode()
    except IndexError:
        return get_sha1_old(fname)


def get_random_hex_string(nbytes):
    ''' use os.urandom to create n byte random string, output integer '''
    from binascii import b2a_hex
    return int(b2a_hex(os.urandom(nbytes)), 16)


def get_random_base64_string(nbytes):
    ''' use os.urandom to create n byte random string, output integer '''
    from binascii import b2a_base64
    return b2a_base64(os.urandom(nbytes)).strip()


def test_get_sha1():
    """ test get_sha1 """
    tmp = get_sha1_old('tests/test_dir/hello_world.txt')
    test = 'a0b65939670bc2c010f4d5d6a0b3e4e4590fb92b'
    assert tmp == test
    tmp = get_sha1('tests/test_dir/hello_world.txt')
    assert tmp == test


def test_run_command():
    """ test run_command """
    cmd = 'echo "HELLO"'
    out = run_command(cmd, do_popen=True, single_line=True).strip()
    assert out == b'HELLO'


def test_cleanup_path():
    """ test cleanup_path """
    instr = '/home/ddboline/THIS TEST PATH (OR SOMETHING LIKE IT) ' + \
            '[OR OTHER!] & ELSE $;,""'
    outstr = r'/home/ddboline/THIS\ TEST\ PATH\ \(OR\ SOMETHING\ LIKE\ ' + \
             r'IT\)\ \[OR\ OTHER\!\]\ \&\ ELSE\ \$\;\,\"\"'
    assert cleanup_path(instr) == outstr
