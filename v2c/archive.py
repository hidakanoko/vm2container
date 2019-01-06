# -*- coding: utf-8 -*-

import os
import subprocess
import tempfile
import time

from .command import CommandExecutor
from .message import ConsoleLogger
from .message import PrintProgressThread


class ArchiveHandler:

    def __init__(self):
        self.logger = ConsoleLogger.get_instance()
        self._cmd_tar = CommandExecutor.find_tool('tar')

    def create_archive(self, files, dest='/tmp/archive.tgz'):
        t = PrintProgressThread()
        t.set_start_message('Creating archive...')
        try:
            t.start()
            with tempfile.NamedTemporaryFile() as filelist:
                self._create_archive_filelist(files, filelist)
                self._create_archive(filelist.name, dest)
        finally:
            t.stop()
            t.join(20)
        if os.path.exists(dest):
            self.logger.info('Archive created in ' + dest)

    def _create_archive_filelist(self, files, filelist):
        line_count = 0
        for f in files:
            if os.path.exists(f):
                line_count += 1
                filelist.write(remove_leading_slash(stretch_parent_path(f)) + '\n')
                if line_count % 100 == 0:
                    filelist.flush()
        filelist.flush()

    def _create_archive(self, filelist_path, dest, gzip=True):
        cmd = 'cd / ; ' + self._cmd_tar + ' c'
        if gzip:
            cmd += 'z'
        cmd += 'f ' + dest + ' -T '\
                + filelist_path\
                + ' --no-recursion --numeric-owner'
        try:
            CommandExecutor.execute(cmd)
        except subprocess.CalledProcessError as e:
            self.logger.warn('Archive creation failed with status code ' + str(e.returncode)
                             + ', ' + str(e.stderr))


def stretch_parent_path(path):
    if not os.path.exists(path):
        raise OSError(path)
    if str(path).strip == '/':
        return path
    f_name = os.path.basename(path)
    parent_dir = path[:path.rfind(f_name)]
    return os.path.join(os.path.realpath(parent_dir), f_name)

def remove_leading_slash(path):
    if str(path).find('/') == 0:
        return path[1:]
    else:
        return path
