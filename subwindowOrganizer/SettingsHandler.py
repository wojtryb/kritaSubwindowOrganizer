from krita import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from subwindowOrganizer import SubwindowOrganizer


class SettingsHandler:
    def __init__(self) -> None:
        self.was_toggled: bool = False
        self.was_subwindows: bool = False

    @property
    def is_toggled(self) -> bool:
        is_toggled = Application.readSetting(
            "SubwindowOrganizer",
            "organizerToggled",
            "true"
        )
        self.was_toggled = is_toggled == "true"
        return self.was_toggled

    @property
    def is_subwindows(self) -> bool:
        self.was_subwindows = \
            Application.readSetting("", "mdi_viewmode", "1") == "0"
        return self.was_subwindows

    def write_is_toggled(self, toggled) -> None:
        Application.writeSetting(
            "SubwindowOrganizer", "organizerToggled", str(toggled).lower()
        )
        self.was_toggled = toggled


class SettingsNotifier:
    def __init__(self, organizer: 'SubwindowOrganizer') -> None:
        self.notifier = self._init_notifier()
        self.organizer = organizer

    def _init_notifier(self) -> Notifier:
        notifier = Application.notifier()
        notifier.setActive(True)
        notifier.configurationChanged.connect(
            self._settings_changed_event
        )
        return notifier

    def _settings_changed_event(self):
        """happens when document mode (subwindow and tabs) is changed in
         settings by the user
         """
        new_mode = self.organizer.settingsHandler.is_subwindows
        old_mode = self.organizer.settingsHandler.was_subwindows

        if not old_mode ^ new_mode:  # mode was not changed in krita settings
            return
        if new_mode:  # changed from tabs to subwindows
            self._turn_organizer_on()
            # addon now can be activated and deactivated
        else:  # mode changed from subwindows to tab
            self._turn_organizer_off()

    def _turn_organizer_on(self):
        self.organizer.actions.organizer_toggle.setVisible(True)
        if self.organizer.settingsHandler.was_toggled:  # addon is on, so we can activate it
            self.organizer.resizer.userTurnOn()

    def _turn_organizer_off(self):
        self.organizer.actions.organizer_toggle.setVisible(False)
        if self.organizer.settingsHandler.was_toggled:  # addon was on
            self.organizer.resizer.userTurnOff()
