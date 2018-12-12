# -*- coding: utf-8 -*-

import ast
import os
import subprocess
import sys
import threading
import time

from MessageUtils import ConsoleLogger


class RpmPackageHandler:
	"""
	This class handles RPM package
	"""

	def __init__(self):
		self.logger = ConsoleLogger.get_instance()
		self._find_tools()
		self._pkg_list = set()
		self._dep_list = {}
		self._query_pkg_cache = {}

	def query_pkg(self, any_query_str):
		# check if name exists
		if any_query_str in self._query_pkg_cache:
			return self._query_pkg_cache[any_query_str]

		# check if full_name exists
		for pkg_info in self._query_pkg_cache.values():
			if any_query_str == pkg_info['full_name']:
				return pkg_info

		# not found, do query
		try:
			cmd = self._cmd_rpm
			cmd += ' -q "' + any_query_str
			cmd += '" --qf "\\{\'name\' : \'%{NAME}\', \'version\' : \'%{VERSION}\','
			cmd += ' \'release\' : \'%{RELEASE}\', \'arch\' : \'%{ARCH}\', \'requires\' : \'[%{REQUIRES},]\','
			cmd += ' \'full_name\' : \'%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}\'\\}"'
			pkg_info = ast.literal_eval(self._exec(cmd))
			self._query_pkg_cache[pkg_info['name']] = pkg_info
			return self._query_pkg_cache[pkg_info['name']]
		except subprocess.CalledProcessError as e:
			self.logger.error(any_query_str + ' NOT installed on the system')
			return None

	def get_pkg_requires(self, pkg_name):
		pkg_info = self.query_pkg(pkg_name)
		requires = set()
		for r in pkg_info['requires'].split(','):
			if len(str(r).strip()) > 0:
				requires.add(str(r).strip())
		return requires

	def show_deps(self, packages):
		pkgs = []
		for pkg_name in packages:
			pkg = self._get_rpm_pkg(pkg_name)
			if pkg is None:
				pkg = RpmPkg(pkg_name)
				self._pkg_list.add(pkg)
			pkg_info = self.query_pkg(pkg_name)
			full_name = pkg_info['name']
			if full_name is None:
				continue
			pkg.set_full_name(full_name)
			pkgs.append(pkg)

			t = PrintProgressThread()
			t.set_start_message('Resolving dependency for ' + pkg_name + '...')
			try:
				t.start()
				self._get_dep_pkgs(pkg)
			finally:
				t.stop()
				t.join(20)

			self._print_dep_tree(pkg, 0, set())

		self.logger.info('[*]=Child dependencies are omitted as already described above.')

	def list_files(self, packages):
		pkgs = []

	def _print_dep_tree(self, pkg, indent_level, handled):
		msg = (' ' * 4 * indent_level) + pkg.get_name()
		if pkg in handled:
			print(msg + ' [*]')
			return
		else:
			print(msg)
		handled.add(pkg)
		indent_level += 1
		for dep_obj in pkg.get_dep_pkgs():
			self._print_dep_tree(dep_obj.pkg, indent_level, handled)

	def _print_wait_cursor(self):
		while True:
			for cursor in '|/-\\':
				sys.stdout.write(cursor + ' Calculating dependencies...')
				sys.stdout.flush()
				time.sleep(0.5)
				sys.stdout.write('\r')

	def get_a_provide_pkg(self, req):
		dep_query_str = self._trim_dep_version(req)
		if dep_query_str in self._dep_list:
			return self._dep_list[dep_query_str]
		try:
			provide_pkgs = self._exec(self._cmd_rpm + ' -q --whatprovides "' + dep_query_str + '"')
			if provide_pkgs is None or len(provide_pkgs.strip()) == 0:
				self.logger.warn('No package provides dependency ' + req)
				return None
			self._dep_list[dep_query_str] = provide_pkgs.strip().splitlines()[0]
			return self._dep_list[dep_query_str]
		except subprocess.CalledProcessError as e:
			self.logger.error('Cannot get packages which provides requirement ' + req)
			return None

	def _get_dep_pkgs(self, pkg):
		#reqs = self._exec(self._cmd_rpm + ' -q --requires ' + pkg.get_name())
		requires = self.get_pkg_requires(pkg.get_name())
		if requires is None or len(requires) == 0:
			return
		for req in requires:
			if self._is_rpmlib(req):
				# "rpm -q --whatprovides XXX" don't handle rpmlib
				# Add 'RPM' as dependency?
				continue

			dep_pkg_full_name = self.get_a_provide_pkg(req)
			pkg_info = self.query_pkg(dep_pkg_full_name)
			dep_pkg_name = pkg_info['name']

			if dep_pkg_name == pkg.get_name():
				# don't handle the dependency if it is itself
				continue

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

		#for dep in pkg.get_dep_pkgs():
		#	required_by = ''
		#	for req in dep.required_by:
		#		if len(required_by) > 0:
		#			required_by += ', '
		#		required_by += req

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
		self.logger.info('Command which found at ' + self._cmd_which)

		self._detect_cmd_path('rpm')

	def _detect_cmd_path(self, tool):
		# check if "which" is detected
		if self._cmd_which is None:
			raise FileNotFoundError("ERROR: which command not found!")

		self._cmd_rpm = self._exec(self._cmd_which + " " + tool)
		self.logger.info('Command ' + tool + ' found at ' + self._cmd_rpm)

	def _exec(self, cmd):
		#self.logger.debug('Executing ' + cmd)
		return subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True).strip()


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


class PrintProgressThread(threading.Thread):
	def __init__(self):
		super(PrintProgressThread, self).__init__()
		self.stop_event = threading.Event()
		self.setDaemon(True)
		self._start_message = 'Thread running...'
		self._end_message = 'done!'

	def run(self):
		while not self.stop_event.is_set():
			for cursor in '|/-\\':
				sys.stdout.write(cursor + self._start_message)
				sys.stdout.flush()
				time.sleep(0.5)
				sys.stdout.write('\r')
		if self._end_message is not None:
			sys.stdout.write(self._end_message + '\n')

	def set_start_message(self, start_message):
		self._start_message = start_message

	def set_end_message(self, end_message):
		self._end_message = end_message

	def stop(self):
		self.stop_event.set()

