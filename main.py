#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse

from RpmUtils import RpmPackageHandler


def handle_args():
	parser = argparse.ArgumentParser(
		prog='vm2container',
		description='Create docker image from running full Linux environment.')

	parser.add_argument('-p', '--package', type=str, action='append', required=True)
	parser.add_argument('-s', '--showDeps', action='store_const', const=True, default=False)
	parser.add_argument('-l', '--listFiles', action='store_const', const=True, default=False)
	#parser.add_argument('-d', '--dest', type=str, default='/tmp/')
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

if arg.listFiles:
	rpm.list_files(arg.package)
