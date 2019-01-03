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
        self._output = None

    def create_archive(self, files, dest='/tmp/archive.tgz'):
        self._output = None
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
        if self._output is not None:
            self.logger.info(self._output)
        if os.path.exists(dest):
            self.logger.info('Archive created in ' + dest)

    def _create_archive_filelist(self, files, filelist):
        for f in files:
            if os.path.exists(f):
                filelist.write(stretch_parent_path(f) + '\n')

    def _create_archive(self, filelist_path, dest, gzip=True):
        cmd = self._cmd_tar + ' c'
        if gzip:
            cmd+= 'z'
        cmd += 'f ' + dest + ' -T '\
                + filelist_path\
                + ' --no-recursion'\
                + ' 2&>1'
        try:
            self._output = CommandExecutor.execute(cmd)
        except subprocess.CalledProcessError as e:
            self.logger.warn('Archive creation failed with status code ' + str(e.returncode)
                             + ', ' + str(e.output))


def stretch_parent_path(path):
    if not os.path.exists(path):
        raise OSError(path)
    if str(path).strip == '/':
        return path
    f_name = os.path.basename(path)
    parent_dir = path[:path.rfind(f_name)]
    return os.path.join(os.path.realpath(parent_dir), f_name)
