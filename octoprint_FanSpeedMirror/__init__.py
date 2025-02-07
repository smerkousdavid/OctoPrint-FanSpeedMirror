# coding=utf-8
from __future__ import absolute_import

from decimal import *
import re
import octoprint.plugin
import subprocess

class FanSpeedMirror(octoprint.plugin.StartupPlugin,
					 octoprint.plugin.TemplatePlugin,
					 octoprint.plugin.SettingsPlugin,
					 octoprint.plugin.AssetPlugin):

	def __init__(self):
#		self._logger.info("__init__")
		self.M126command=""
		self.M127command=""

	def on_after_startup(self):
#		self._logger.info("on_after_startup")
		self.get_settings_updates()

	def get_settings_defaults(self):
#		self._logger.info("get_settings_defaults")
		return dict(
			M126command="",
			M127command=""
		)

	def on_settings_save(self, data):
#		self._logger.info("on_settings_save")
		s = self._settings
		if "M126command" in data.keys():
			s.set(["M126command"], data["M126command"])
		if "M127command" in data.keys():
			s.set(["M127command"], data["M127command"])
		self.get_settings_updates()
		#clean up settings if everything's default
		self.on_settings_cleanup()
		s.save()

	def on_settings_cleanup(self):
#		self._logger.info("on_settings_cleanup")
		import octoprint.util
		from octoprint.settings import NoSuchSettingsPath

		try:
			config = self._settings.get_all_data(merged=False, incl_defaults=False, error_on_path=True)
		except NoSuchSettingsPath:
			return

		if config is None:
			self._settings.clean_all_data()
			return

		if self.config_version_key in config and config[self.config_version_key] is None:
			del config[self.config_version_key]

		defaults = self.get_settings_defaults()
		diff = octoprint.util.dict_minimal_mergediff(defaults, config)

		if not diff:
			self._settings.clean_all_data()
		else:
			self._settings.set([], diff)

	def get_assets(self):
#		self._logger.info("get_assets")
		return dict(
			js=["js/FanSpeedMirror.js"],
			css=["css/FanSpeedMirror.css"],
			less=["less/FanSpeedMirror.less"]
		)

	def get_template_configs(self):
#		self._logger.info("get_template_configs")
		return [
			dict(type="settings", custom_bindings=False)
		]

	def get_settings_updates(self):
#		self._logger.info("get_settings_updates")
		self.M126command = self._settings.get(["M126command"])
		self.M127command = self._settings.get(["M127command"])

	def mirror_fan(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
		if gcode and gcode.startswith('M126'):
			cmd_line = self.M126command
			self._logger.debug("Executing (" + cmd_line + ")")
			try:
				r = subprocess.call([self.M126command])
				if r < 0:
					self._logger.error("Error executing command %s: %s" % (cmd_line, r))
			except OSError as e:
				self._logger.exception("Exception executing command %s: %s" % (cmd_line, e))
		elif gcode and gcode.startswith('M127'):
			if self.M127command != "":
				cmd_line = self.M127command
				self._logger.debug("Executing (" + cmd_line + ")")
				try:
					r = subprocess.call(cmd_line)
					if r < 0:
						self._logger.error("Error executing command %s: %s" % (cmd_line, r))
				except OSError as e:
					self._logger.exception("Exception executing command %s: %s" % (cmd_line, e))
			else:
				self._logger.debug("M127command is empty")

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
		# for details.
		return dict(
			FanSpeedMirror=dict(
				displayName="Fan Speed Mirror",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="smerkousdavid",
				repo="OctoPrint-FanSpeedMirror",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/smerkousdavid/OctoPrint-FanSpeedMirror/archive/{target_version}.zip"
			)
		)


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Fan Speed Mirror"
__plugin_pythoncompat__ = ">=2.7,<4"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = FanSpeedMirror()
	
	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.comm.protocol.gcode.sent": __plugin_implementation__.mirror_fan,
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

