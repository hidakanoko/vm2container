#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse

from ArchiveUtils import ArchiveHandler
from RpmUtils import RpmPackageHandler


def handle_args():
	parser = argparse.ArgumentParser(
		prog='vm2container',
		description='Create docker image from running full Linux environment.')

	parser.add_argument('-p', '--package', type=str, action='append', required=True)
	parser.add_argument('-s', '--showDeps', action='store_const', const=True, default=False)
	parser.add_argument('-l', '--listFiles', action='store_const', const=True, default=False)
	parser.add_argument('-a', '--createArchive', action='store_const', const=True, default=False)
	#parser.add_argument('-s', '--skipDownload', action='store_const', const=True, default=False)
	#parser.add_argument('-o', '--detectObject', action='store_const', const=True, default=False)
	#parser.add_argument('-t', '--searchImageType', type=str, default=None)
	#parser.add_argument('-l', '--downloadLimit', type=int, choices=range(1,101), default=100)

	args = parser.parse_args()
	return args


arg = handle_args()
rpm = RpmPackageHandler()

if arg.showDeps:
	rpm.show_deps(arg.package)

filelist = None
if arg.listFiles:
	filelist = rpm.list_files(arg.package, True)

if arg.createArchive:
	if filelist is None:
		filelist = rpm.list_files(arg.package, False)
	archive_handler = ArchiveHandler()
	archive_handler.create_archive(filelist)
