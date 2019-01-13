import argparse

from . import archive
from . import dir
from . import rpm


def handle_args():
    parser = argparse.ArgumentParser(
        prog='vm2container',
        description='Create docker image from running full Linux environment.')

    parser.add_argument('-p', '--package', type=str, action='append', required=False)
    parser.add_argument('-s', '--showDeps', action='store_const', const=True, default=False)
    parser.add_argument('-l', '--listFiles', action='store_const', const=True, default=False)
    parser.add_argument('-a', '--createArchive', action='store_const', const=True, default=False)
    parser.add_argument('-d', '--directory', type=str, action='append', required=False)

    args = parser.parse_args()
    return args


def create_filelist(arg, print_filelist=False):
    if arg.package is None and arg.directory is None:
        print("no packages nor directories are specified. exiting.")
        exit(1)

    files = set()
    if arg.package is not None:
        files.update(rpm.list_files(arg.package, print_filelist))
    if arg.directory is not None:
        files.update(dir.list_files(arg.directory, print_filelist))

    return sorted(files)


arg = handle_args()
rpm = rpm.RpmPackageHandler()

if arg.showDeps:
    rpm.show_deps(arg.package)

filelist = None
if arg.listFiles:
    filelist = create_filelist(arg, True)

if arg.createArchive:
    if filelist is None:
        filelist = create_filelist(arg, False)
    archive_handler = archive.ArchiveHandler()
    archive_handler.create_archive(filelist)
