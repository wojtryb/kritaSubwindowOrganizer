from dataclasses import dataclass
from krita import *

from .Resizer import Resizer
from .actions import Actions, ActionBuilder
from .SettingsHandler import SettingsHandler


class SubwindowOrganizer(Extension):

    def __init__(self, parent):
        super(SubwindowOrganizer, self).__init__(parent)

        self.settingsNotifier: None  # Notifier

        self.actions: Actions
        self.resizer: Resizer
        self.settingsHandler = SettingsHandler()

    def setup(self):
        """reading values saved in krita settings and creating a
        notifier for settings changed event.
        """
        self.settingsNotifier = Application.notifier()
        self.settingsNotifier.setActive(True)
        self.settingsNotifier.configurationChanged.connect(
            self.settingsChangedEvent
        )

    def createActions(self, window):
        """creates actions displayed in the view menu"""
        qwin = window.qwindow()
        toggleAtStart = self.settingsHandler.is_toggled and self.settingsHandler.is_subwindows

        self.resizer = Resizer(qwin, toggleAtStart)
        self.actions = ActionBuilder(self, window).build_actions()

    def pickSubwindow(self):
        """switching between subwindows - user action"""
        if not self.resizer.subWindowFilterAll.isMaximized:
            self.resizer.userToggleSubwindow()

    def openOverview(self):
        """opens grayscale overview"""
        self.resizer.userOpenOverview()

    def organizerToggle(self, toggled):
        """toggles the whole plugin off and on"""
        self.settingsHandler.write_is_toggled(toggled)
        if self.settingsHandler.is_subwindows and self.settingsHandler.is_toggled:
            self.actions.pick_subwindow.setVisible(True)
            self.actions.open_overview.setVisible(True)
            self.resizer.userTurnOn()
        else:
            self.actions.pick_subwindow.setVisible(False)
            self.actions.open_overview.setVisible(False)
            self.resizer.userTurnOff()

    def settingsChangedEvent(self):
        """happens when document mode (subwindow and tabs) is changed in
         settings by the user
         """
        new_mode = self.settingsHandler.is_subwindows
        old_mode = self.settingsHandler.was_subwindows

        if old_mode ^ new_mode:  # mode was changed in krita settings
            if new_mode:  # changed from tabs to subwindows
                # addon now can be activated and deactivated
                self.actions.organizer_toggle.setVisible(True)
                if self.settingsHandler.was_toggled:  # addon is on, so we can activate it
                    self.resizer.userTurnOn()
            else:  # mode changed from subwindows to tab
                self.actions.organizer_toggle.setVisible(False)
                if self.settingsHandler.was_toggled:  # addon was on
                    self.resizer.userTurnOff()


Krita.instance().addExtension(SubwindowOrganizer(Krita.instance()))
