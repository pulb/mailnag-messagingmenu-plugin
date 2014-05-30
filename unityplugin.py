#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# unityplugin.py
#
# Copyright 2014 Patrick Ulbrich <zulu99@gmx.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#

from gi.repository import Gtk, Gio, MessagingMenu
from common.plugins import Plugin, HookTypes
from common.exceptions import InvalidOperationException
from common.i18n import _

PLUGIN_VERSION = "1.0"

MAIL_ICON = 'mail-unread-symbolic'
OPEN_MAIL_READER_ICON = 'mail-read'

plugin_defaults = { 'max_visible_messages' : '10' }


class UserscriptPlugin(Plugin):
	def __init__(self):
		self._mails_added_hook = None
		self._mails_removed_hook = None
		self._app = None
		self._mails = None
		self._max_messages = 0
	
	
	def enable(self):
		icon = Gio.ThemedIcon.new(OPEN_MAIL_READER_ICON)
		
		self._app = MessagingMenu.App.new('mailnag-unity.desktop')
		self._app.connect('activate-source', self._source_activated)
		self._app.register()
		
		self._mails = []
		self._max_messages = int(self.get_config()['max_visible_messages'])
		
		def mails_added_hook(new_mails, all_mails):
			self._rebuild_with_new(new_mails)
		
		def mails_removed_hook(remaining_mails):
			self._rebuild_with_remaining(remaining_mails)
		
		self._mails_added_hook = mails_added_hook
		self._mails_removed_hook = mails_removed_hook
		
		controller = self.get_mailnag_controller()
		hooks = controller.get_hooks()
		
		hooks.register_hook_func(HookTypes.MAILS_ADDED, 
			self._mails_added_hook)
		
		hooks.register_hook_func(HookTypes.MAILS_REMOVED,
			self._mails_removed_hook)
	
	
	def disable(self):
		controller = self.get_mailnag_controller()
		hooks = controller.get_hooks()
		
		if self._mails_added_hook != None:
			hooks.unregister_hook_func(HookTypes.MAILS_ADDED,
				self._mails_added_hook)
			self._mails_added_hook = None
		
		if self._mails_removed_hook != None:
			hooks.unregister_hook_func(HookTypes.MAILS_REMOVED,
				self._mails_removed_hook)
			self._mails_removed_hook = None
		
		if self._app != None:
			self._app.unregister()
		
		self._mails = None

	
	def get_manifest(self):
		return (_("Ubuntu Unity"),
				_("Shows new mails in Ubuntu's Messaging menu."),
				PLUGIN_VERSION,
				"Patrick Ulbrich <zulu99@gmx.net>",
				False)


	def get_default_config(self):
		return plugin_defaults
	
	
	def has_config_ui(self):
		return True
	
	
	def get_config_ui(self):
		box = Gtk.Box()
		box.set_spacing(12)
		box.set_orientation(Gtk.Orientation.HORIZONTAL)
		
		label = Gtk.Label('Maximum number of visible mails:')
		spinner = Gtk.SpinButton.new_with_range(1.0, 20.0, 1.0)

		box.pack_start(label, False, False, 0)
		box.pack_start(spinner, False, False, 0)
		
		return box
	
	
	def load_ui_from_config(self, config_ui):
		config = self.get_config()
		max_msgs = float(config['max_visible_messages'])
		spinner = config_ui.get_children()[1]
		spinner.set_value(max_msgs)
	
	
	def save_ui_to_config(self, config_ui):
		config = self.get_config()
		spinner = config_ui.get_children()[1]
		max_msgs = spinner.get_value()
		config['max_visible_messages'] = str(int(max_msgs))


	def _rebuild_with_new(self, new_mails):
		menu_reset = (len(self._mails) > 0) and (not self._app.has_source(self._mails[0].id))
		
		# Clear messaging menu (remove current mails)
		for m in self._mails:
			self._app.remove_source(m.id)
		
		if menu_reset:
			# Reset detected (the Clear button has been pressed by the user).
			# Discard current mails and start a new mail list.
			self._mails = new_mails
		else:
			# Add new mails to the top of the mail list.
			self._mails = new_mails + self._mails
		
		self._add_mails_to_menu()
		
				
	def _rebuild_with_remaining(self, remaining_mails):
		menu_reset = (len(self._mails) > 0) and (not self._app.has_source(self._mails[0].id))
		
		# Clear messaging menu (remove current mails)
		for m in self._mails:
			self._app.remove_source(m.id)
		
		if menu_reset:
			# Reset detected (the Clear button has been pressed by the user).
			# Discard current mails.
			self._mails = []
		else:
			# Remove mails that are not in the remainder list.
			self._mails = [m for m in self._mails if m in remaining_mails]
		
		self._add_mails_to_menu()
	
	
	def _add_mails_to_menu(self):
		# Add mail list to the messaging menu.
		if len(self._mails) > 0:
			ubound = len(self._mails) if len(self._mails) <= self._max_messages \
				else self._max_messages

			for i in range(ubound):
				m = self._mails[i]
				name, addr = m.sender
				sender = name if len(name) > 0 else addr
				icon = Gio.ThemedIcon.new(MAIL_ICON)
				label = "%s  -  %s" % (sender, m.subject)
				if m.datetime > 0:
					time = m.datetime * 1000L * 1000L
					self._app.append_source_with_time(m.id, icon, label, time)
				else:
					self._app.append_source_with_string(m.id, icon, label, '?')
				
				self._app.draw_attention(m.id)
	
	
	def _source_activated(self, app, source_id):
		self._mails = filter(lambda m: m.id != source_id, self._mails)
		
		controller = self.get_mailnag_controller()
		try:
			controller.mark_mail_as_read(source_id)
		except InvalidOperationException:
			pass
		
		self._rebuild_with_new([])

