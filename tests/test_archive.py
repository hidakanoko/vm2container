# -*- coding: utf-8 -*-

import os
import shutil
import tempfile
import unittest

from v2c.archive import stretch_parent_path


class TestArchive(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if self.tmp_dir is not None and os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def test__stretch_parent_path__return_None_given_path_is_None(self):
        # given
        path = None

        # when, then
        self.assertIsNone(stretch_parent_path(path))

    def test__stretch_parent_path__return_none_given_path_is_Empty(self):
        # given
        path = ''

        # when, then
        self.assertIsNone(stretch_parent_path(path))
