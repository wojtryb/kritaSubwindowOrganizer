"""Module for interacting with krita settings."""

from krita import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from subwindowOrganizer import SubwindowOrganizer


class SettingsHandler:
    """Stores current and past information about settings state.

    Current values are implemented as properties which read from krita
    config file, and overwrite internal ones.
    """

    def __init__(self) -> None:
        self.was_toggled: bool = self.is_toggled
        self.was_subwindows: bool = self.is_subwindows

    @property
    def is_toggled(self) -> bool:
        """Read from krita settings, whether the plugin should be
        toggled.
        """
        is_toggled = Application.readSetting(
            "SubwindowOrganizer",
            "organizerToggled",
            "true")
        self.was_toggled = is_toggled == "true"
        return self.was_toggled

    @property
    def is_subwindows(self) -> bool:
        """Read from krita settings, whether the subwindows mode is
        turned on.
        """
        self.was_subwindows = \
            Application.readSetting("", "mdi_viewmode", "1") == "0"
        return self.was_subwindows

    def write_is_toggled(self, toggled) -> None:
        """Save whether the plugin should be on, or not to krita
        settings."""
        Application.writeSetting(
            "SubwindowOrganizer", "organizerToggled", str(toggled).lower()
        )
        self.was_toggled = toggled


class SettingsNotifier:
    """Stores a settings notifier (krita object), to handle the event of
     user making changes to krita settings using GUI.
     """

    def __init__(self, organizer: 'SubwindowOrganizer') -> None:
        self.notifier = self._init_notifier()
        self.organizer = organizer

    def _init_notifier(self) -> Notifier:
        """Initializes settings notifier, binding a callback method."""
        notifier = Application.notifier()
        notifier.setActive(True)
        notifier.configurationChanged.connect(
            self._settings_changed_event
        )
        return notifier

    def _settings_changed_event(self):
        """Handle the event of user changing the subwindows mode in GUI"""
        is_subwindows = self.organizer.settingsHandler.is_subwindows
        was_subwindows = self.organizer.settingsHandler.was_subwindows

        # (XNOR) mode was not changed in krita settings
        if not was_subwindows ^ is_subwindows:
            return
        if is_subwindows:
            self._turn_organizer_on()
        else:
            self._turn_organizer_off()

    def _turn_organizer_on(self):
        self.organizer.actions.organizer_toggle.setVisible(True)
        if self.organizer.settingsHandler.was_toggled:
            self.organizer.resizer.userTurnOn()

    def _turn_organizer_off(self):
        self.organizer.actions.organizer_toggle.setVisible(False)
        if self.organizer.settingsHandler.was_toggled:
            self.organizer.resizer.userTurnOff()
