#!/usr/bin/env python2

# To install the plugin run this script as root:
# ./setup.py install

from distutils.core import setup
from distutils.cmd import Command
from distutils.log import warn, info, error
from distutils.command.install_data import install_data
from distutils.command.build import build
from distutils.sysconfig import get_python_lib

import sys
import os
import shutil

PACKAGE_NAME = 'mailnag-messagingmenu-plugin'
PLUGIN_VERSION = '1.1'

# TODO : This hack won't work with --user and --home options
PREFIX = '/usr'
for arg in sys.argv:
	if arg.startswith('--prefix='):
		PREFIX = arg[9:]

BUILD_DIR = 'build'
for arg in sys.argv:
	if arg.startswith('--build-base='):
		BUILD_DIR = arg[13:]

BUILD_PATCH_DIR = os.path.join(BUILD_DIR, 'patched')
BUILD_PLUGIN_DIR = os.path.join(BUILD_DIR, 'plugins')


class BuildData(build):
	def run (self):
		# remove build dir (if existing)
		shutil.rmtree(BUILD_DIR, ignore_errors = True)
		
		os.makedirs(BUILD_PATCH_DIR)
		os.makedirs(BUILD_PLUGIN_DIR)
		shutil.copy2('messagingmenuplugin.py', BUILD_PLUGIN_DIR)
		
		# patch paths
		self._patch_file('./mailnag-messagingmenu.desktop.in', os.path.join(BUILD_PATCH_DIR, 
			'mailnag-messagingmenu.desktop'), '%PREFIX%', PREFIX)
		build.run (self)


	def _patch_file(self, infile, outfile, orig, replaced):
		with open(infile, 'r') as f:
			strn = f.read()
			strn = strn.replace(orig, replaced)
		with open(outfile, 'w') as f:
			f.write(strn)


class InstallData(install_data):
	def run (self):
		install_data.run (self)


class Uninstall(Command):
	def run (self):
		# TODO
		pass


setup(name=PACKAGE_NAME,
	version=PLUGIN_VERSION,
	description='MessagingMenu plugin for Mailnag',
	author='Patrick Ulbrich',
	author_email='zulu99@gmx.net',
	url='https://github.com/pulb/mailnag-messagingmenu-plugin',
	license='GNU GPL2',
	package_dir = {'Mailnag.plugins' : BUILD_PLUGIN_DIR},
	packages=['Mailnag.plugins'],
	scripts=['mailnag-messagingmenu-action-launcher'],
	data_files=[('share/applications', [os.path.join(BUILD_PATCH_DIR, 'mailnag-messagingmenu.desktop')])],
	cmdclass={'build': BuildData, 
                'install_data': InstallData,
                'uninstall': Uninstall}
	)
