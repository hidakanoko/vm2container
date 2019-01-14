# -*- coding: utf-8 -*-

import os
import subprocess
import tempfile

from v2c import command
from v2c.message import info, warn, PrintProgressThread
from v2c import dir


def create_archive(files, dest='/tmp/archive.tgz'):
    t = PrintProgressThread()
    t.set_start_message('Creating archive...')
    try:
        t.start()
        with tempfile.NamedTemporaryFile() as filelist:
            _create_archive_filelist(files, filelist)
            _create_archive(filelist.name, dest)
    finally:
        t.stop()
        t.join(20)
    if os.path.exists(dest):
        info('Archive created in ' + dest)


def _create_archive_filelist(files, filelist):
    line_count = 0
    for f in files:
        if os.path.exists(f):
            line_count += 1
            filelist.write(dir.remove_leading_slash(dir.stretch_parent_path(f)) + '\n')
            if line_count % 100 == 0:
                filelist.flush()
    filelist.flush()

def _create_archive(filelist_path, dest, gzip=True):
    cmd = 'cd / ; ' + command.find_tool('tar') + ' c'
    if gzip:
        cmd += 'z'
    cmd += 'f ' + dest + ' -T '\
            + filelist_path\
            + ' --no-recursion --numeric-owner'
    try:
        command.execute(cmd)
    except subprocess.CalledProcessError as e:
        warn('Archive creation failed with status code ' + str(e.returncode)
                         + ', ' + str(e.stderr))
