# -*- coding: utf-8 -*-

import os
from v2c.message import info


def list_files(dirs, print_filelist=False):
    info('Creating file list in ' + str(len(dirs)) + ' directories...')
    entries = set()
    for d in dirs:
        entries.update(__get_filelist_recursive(d))
    entries_sorted = sorted(entries)
    if print_filelist:
        for e in entries_sorted:
            print(e)
    info('Total ' + str(len(entries)) + ' entries found.')
    return entries_sorted


def __get_filelist_recursive(d):
    entries = set()
    entries.add(remove_trailing_slash(d))
    if os.path.isdir(d):
        for entry in os.listdir(d):
            entries.update(__get_filelist_recursive(os.path.join(d, entry)))
    return entries


def remove_trailing_slash(d):
    path = str(d)
    if path.endswith('/'):
        path = path[:-1]
    return path


def remove_leading_slash(path):
    if str(path).find('/') == 0:
        return path[1:]
    else:
        return path


def stretch_parent_path(path):
    if not os.path.exists(path):
        raise OSError(path)
    if str(path).strip == '/':
        return path
    f_name = os.path.basename(path)
    parent_dir = path[:path.rfind(f_name)]
    return os.path.join(os.path.realpath(parent_dir), f_name)

