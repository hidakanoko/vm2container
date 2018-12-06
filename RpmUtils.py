# -*- coding: utf-8 -*-

import os
import subprocess

class RpmPackageHandler:
	"""
	This class handles RPM package
	"""

	def __init__(self):
		self._find_tools()
		self._pkg_list = set()
		self._dep_list = {}
		self._name_full_name_list = {}
		self._full_name_name_list = {}

	def query_full_name(self, pkg_name):
		if pkg_name in self._name_full_name_list:
			return self._name_full_name_list[pkg_name]
		try:
			pkg_full_name = self._exec(self._cmd_rpm + ' -q "' + pkg_name + '"')
			self._name_full_name_list[pkg_name] = pkg_full_name
			return self._name_full_name_list[pkg_name]
		except subprocess.CalledProcessError as e:
			print 'ERROR : ' + pkg_name + ' NOT installed on the system'
			print e
			return None;

	def query_name(self, query_name):
		if query_name in self._full_name_name_list:
			return self._full_name_name_list[query_name]
		try:
			pkg_name = self._exec(self._cmd_rpm + ' -q "' + query_name + '"')
			self._full_name_name_list[query_name] = pkg_name
			return self._full_name_name_list[query_name]
		except subprocess.CalledProcessError as e:
			print 'ERROR : ' + query_name + ' NOT installed on the system'
			print e
			return None;

	def show_deps(self, packages):
		pkgs = [];
		for pkg_name in packages:
			pkg = self._get_rpm_pkg(pkg_name)
			if pkg is None:
				pkg = RpmPkg(pkg_name)
				self._pkg_list.add(pkg)
			full_name = self.query_full_name(pkg_name)
			if full_name is None:
				continue;
			pkg.set_full_name(full_name)
			pkgs.append(pkg)
			self._get_dep_pkgs(pkg)

	def get_a_provide_pkg(self, req):
		dep_query_str = self._trim_dep_version(req)
		if dep_query_str in self._dep_list:
			return self._dep_list[dep_query_str];
		try:
			provide_pkgs = self._exec(self._cmd_rpm + ' -q --whatprovides "' + dep_query_str + '"')
			if provide_pkgs is None or len(provide_pkgs.strip()) == 0:
				print 'WARN: No package provides dependency ' + req
				return None
			self._dep_list[dep_query_str] = provide_pkgs.strip().splitlines()[0]
			return self._dep_list[dep_query_str]
		except subprocess.CalledProcessError as e:
			print 'ERROR: Cannot get packages which provides requirement ' + req
			return None

	def _get_dep_pkgs(self, pkg):
		reqs = self._exec(self._cmd_rpm + ' -q --requires ' + pkg.get_name())
		if reqs is None or len(reqs.strip()) == 0:
			return
		for req in list(set(reqs.splitlines())):
			if self._is_rpmlib(req):
				# "rpm -q --whatprovides XXX" don't handle rpmlib
				# Add 'RPM' as dependency?
				continue

			dep_pkg_full_name = self.get_a_provide_pkg(req)
			dep_pkg_name = self.query_name(dep_pkg_full_name)

			dep_pkg = self._get_rpm_pkg(dep_pkg_name)
			if dep_pkg is None:
				dep_pkg = RpmPkg(dep_pkg_name)
				dep_pkg.set_full_name(dep_pkg_full_name)
				self._pkg_list.add(dep_pkg)
				self._get_dep_pkgs(dep_pkg)

			dep_obj = pkg.find_dependency(dep_pkg_name)
			if dep_obj is None:
				dep_obj = PkgDep(dep_pkg)
				pkg.add_dep_pkg(dep_obj)

			dep_obj.add_required_by(req)

		print 'Handling dependency for ' + pkg.get_name()
		for dep in pkg.get_dep_pkgs():
			required_by = ''
			for req in dep.required_by:
				if len(required_by) > 0:
					required_by += ', '
				required_by += req
			print ' - ' + dep.pkg.get_name() + ' (' + required_by + ')'

	def _get_rpm_pkg(self, pkg_name):
		for p in self._pkg_list:
			if p.get_name() == pkg_name:
				return p
		return None

	def _find_pkg_in_list(self, pkg_name):
		for p in self._pkg_list:
			if p.get_name == pkg_name:
				return p
		return None

	def _trim_dep_version(self, dep_str):
		if (dep_str.find('<') >= 0 or dep_str.find('=') >= 0 or dep_str.find('>') >= 0) and len(dep_str.split(' ')) == 3:
			return dep_str.split(' ')[0]
		else:
			return dep_str

	def _is_rpmlib(self, pkg_name):
		return pkg_name.startswith('rpmlib')

	def _find_tools(self):
		cmd_which = "/usr/bin/which"
		if not os.path.exists(cmd_which):
			cmd_which = "/bin/which"
			if not os.path.exists(cmd_which):
				raise FileNotFoundError("ERROR: which command not found!")
		self._cmd_which = cmd_which
		print 'INFO: Command which found at ' + self._cmd_which

		self._detect_cmd_path('rpm')

	def _detect_cmd_path(self, tool):
		# check if "which" is detected
		if self._cmd_which is None:
			raise FileNotFoundError("ERROR: which command not found!")

		self._cmd_rpm = self._exec(self._cmd_which + " " + tool)
		print 'INFO: Command ' + tool + ' found at ' + self._cmd_rpm

	def _exec(self, cmd):
		#print 'Executing ' + cmd
		return subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True).strip();


class RpmPkg:
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


class PkgDep:
	def __init__(self, pkg):
		self.pkg = pkg
		self.required_by = set()

	def add_required_by(self, dep_str):
		self.required_by.add(dep_str)

