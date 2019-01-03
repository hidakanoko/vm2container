# -*- coding: utf-8 -*-

import os
import subprocess
import tempfile

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
        for f in files:
            if os.path.exists(f):
                filelist.write(f + '\n')

    def _create_archive(self, filelist_path, dest, gzip=True):
        cmd = self._cmd_tar + ' c'
        if gzip:
            cmd+= 'z'
        cmd += 'f ' + dest + ' -T '\
                + filelist_path\
                + ' --no-recursion'
        try:
            CommandExecutor.execute(cmd)
        except subprocess.CalledProcessError as e:
            self.logger.warn('Archive creation failed with status code ' + str(e.returncode))


def stretch_parent_path(path):
    return path
