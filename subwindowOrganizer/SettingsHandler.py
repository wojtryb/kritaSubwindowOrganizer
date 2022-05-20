from dataclasses import dataclass
from krita import *


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
