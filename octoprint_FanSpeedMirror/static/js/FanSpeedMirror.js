/*
 * View model for OctoPrint-FanSpeedMirror
 *
 * Author: Brad Morgan
 * License: AGPLv3
 */
$(function() {
    function FanSpeedMirrorViewModel(parameters) {
        var self = this;

		self.settings = parameters[0];
		self.control = parameters[1];
		self.loginState = parameters[2];

		self.settings.M126command = new ko.observable("");
		self.settings.m127command = new ko.observable("");

		self.updateSettings = function () {
			try {
				self.settings.M126command(self.settings.settings.plugins.FanSpeedMirror.M126command());
				self.settings.M127command(self.settings.settings.plugins.FanSpeedMirror.M127command());
			}
			catch (error) {
				console.log(error);
			}
		}

		//update settings in case user changes them, otherwise a refresh of the UI is required
		self.onSettingsHidden = function () {
			self.updateSettings();
		}
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: FanSpeedMirrorViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: ["loginStateViewModel", "settingsViewModel"],
        // Elements to bind to, e.g. #settings_plugin_FanSpeedMirror, #tab_plugin_FanSpeedMirror, ...
        elements: [ /* ... */ ]
    });
});
