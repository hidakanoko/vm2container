# -*- coding: utf-8 -*-

import os
from v2c import command


def is_rpm_environment():
    return os.path.exists("/etc/redhat-release") and str(command.find_tool('rpm')).find('/rpm') >= 0


def is_deb_environment():
    return False


class PackageHandler(object):

    def __init__(self):
        self._find_tools()

    def show_deps(self, packages):
        raise NotImplementedError()

    def list_files(self, packages, print_filelist=False):
        raise NotImplementedError()

    def _find_tools(self):
        raise NotImplementedError()


class PkgInfo:
    def __init__(self, name):
        self._name = name
        self._deps = set()

    def set_full_name(self, full_name):
        self._full_name = full_name

    def get_name(self):
        return self._name

    def get_full_name(self):
        return self._full_name

    def add_dep_pkg(self, p):
        self._deps.add(p)

    def get_dep_pkgs(self):
        return self._deps

    def find_dependency(self, pkg_name):
        for pkg_dep in self.get_dep_pkgs():
            if pkg_dep.pkg.get_name() == pkg_name:
                return pkg_dep
        return None


class DepInfo:
    def __init__(self, pkg):
        self.pkg = pkg
        self.required_by = set()

    def add_required_by(self, dep_str):
        self.required_by.add(dep_str)
