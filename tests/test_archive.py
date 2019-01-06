# -*- coding: utf-8 -*-

import os
import platform
import shutil
import tempfile
import unittest
from nose.tools import ok_, eq_, raises

from v2c.archive import stretch_parent_path
from v2c.archive import remove_leading_slash

class TestArchive(unittest.TestCase):

    def setUp(self):
        # check platform
        if platform.system() != 'Linux':
            raise SystemError('Unable to run tests except Linux environment')
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if self.tmp_dir is not None and os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    @raises(OSError)
    def test_stretch_parent_path__throws_FileNotFoundError_given_path_NOT_exist(self):
        # given
        path = os.path.join(self.tmp_dir, 'dir_not_exist')

        # when, then
        stretch_parent_path(path)

    def test_stretch_parent_path__return_root_given_root(self):
        # given
        path = '/'

        # when, then
        eq_(stretch_parent_path(path), '/')

    def test_stretch_parent_path__return_realpath_given_parent_dir_is_symlink(self):
        # given
        link_target_dir = tempfile.mkdtemp(dir=self.tmp_dir)

        slink = os.path.join(self.tmp_dir, 'slink')
        os.symlink(link_target_dir, slink)

        (file_handler, file_under_symlink_dir) = tempfile.mkstemp(dir=slink)
        path_filename = os.path.basename(file_under_symlink_dir)
        realpath = os.path.join(link_target_dir, path_filename)

        # when, then
        eq_(stretch_parent_path(file_under_symlink_dir), realpath)

    def test_remove_leading_slash__remove_leading_slash_given_path_starts_with_slash(self):
        # given
        path = '/path/to/file'

        # when, then
        eq_(remove_leading_slash(path), 'path/to/file')

    def test_remove_leading_slash__do_nothing_given_path_does_NOT_start_with_slash(self):
        # given
        path = 'path/to/file'

        # when, then
        eq_(remove_leading_slash(path), 'path/to/file')
