from dataclasses import dataclass
from krita import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from subwindowOrganizer import SubwindowOrganizer


@dataclass
class SettingsHandler:
    was_toggled: bool = False
    was_subwindows: bool = False

    @property
    def is_toggled(self):
        is_toggled = Application.readSetting(
            "SubwindowOrganizer",
            "organizerToggled",
            "true"
        )
        self.was_toggled = is_toggled == "true"
        return self.was_toggled

    @property
    def is_subwindows(self):
        self.was_subwindows = \
            Application.readSetting("", "mdi_viewmode", "1") == "0"
        return self.was_subwindows

    def write_is_toggled(self, toggled):
        Application.writeSetting(
            "SubwindowOrganizer", "organizerToggled", str(toggled).lower()
        )
        self.was_toggled = toggled


@dataclass
class SettingsNotifier:
    def __init__(self, organizer: 'SubwindowOrganizer') -> None:
        self.notifier = Application.notifier()
        self.notifier.setActive(True)
        self.notifier.configurationChanged.connect(
            self.settingsChangedEvent
        )
        self.organizer = organizer

    def settingsChangedEvent(self):
        """happens when document mode (subwindow and tabs) is changed in
         settings by the user
         """
        organizer = self.organizer
        new_mode = organizer.settingsHandler.is_subwindows
        old_mode = organizer.settingsHandler.was_subwindows

        if not old_mode ^ new_mode:  # mode was not changed in krita settings
            return
        if new_mode:  # changed from tabs to subwindows
            # addon now can be activated and deactivated
            self.organizer.actions.organizer_toggle.setVisible(True)
            if self.organizer.settingsHandler.was_toggled:  # addon is on, so we can activate it
                self.organizer.resizer.userTurnOn()
        else:  # mode changed from subwindows to tab
            self.organizer.actions.organizer_toggle.setVisible(False)
            if self.organizer.settingsHandler.was_toggled:  # addon was on
                self.organizer.resizer.userTurnOff()
