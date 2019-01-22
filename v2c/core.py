import argparse

from . import archive
from . import dir
from . import rpm
from . import pkg
from . import message


def handle_args():
    parser = argparse.ArgumentParser(
        prog='vm2container',
        description='Create docker image from running full Linux environment.')

    parser.add_argument('-p', '--package', type=str, action='append', required=False)
    parser.add_argument('-s', '--showDeps', action='store_const', const=True, default=False)
    parser.add_argument('-l', '--listFiles', action='store_const', const=True, default=False)
    parser.add_argument('-a', '--createArchive', action='store_const', const=True, default=False)
    parser.add_argument('-d', '--directory', type=str, action='append', required=False)
    parser.add_argument('-v', '--verbose', type=str, action='store', default="INFO", help="ERROR, WARN, INFO, DEBUG", required=False)

    args = parser.parse_args()
    return args


def create_filelist(arg, print_filelist=False):
    files = set()
    if arg.package is not None:
        files.update(pkg_handler.list_files(arg.package, print_filelist))
    if arg.directory is not None:
        files.update(dir.list_files(arg.directory, print_filelist))

    return sorted(files)


def check_args(arg):
    if arg.package is None and arg.directory is None:
        message.error("no packages nor directories are specified. exiting.")
        exit(1)

def get_instance():
    if pkg.is_rpm_environment():
        return rpm.RpmPackageHandler()
    elif pkg.is_deb_environment():
        raise ModuleNotFoundError()
    else:
        raise NotImplementedError()

arg = handle_args()

message.configure_logger(log_level=arg.verbose)

check_args(arg)

pkg_handler = get_instance()

if arg.showDeps:
    pkg_handler.show_deps(arg.package)

filelist = None
if arg.listFiles:
    filelist = create_filelist(arg, True)

if arg.createArchive:
    if filelist is None:
        filelist = create_filelist(arg, False)
    archive.create_archive(filelist)
