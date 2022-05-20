from dataclasses import dataclass
from krita import *

from .Resizer import Resizer
from .actions import Actions, ActionBuilder
from .SettingsHandler import SettingsHandler, SettingsNotifier


class SubwindowOrganizer(Extension):

    def __init__(self, parent):
        super(SubwindowOrganizer, self).__init__(parent)

        self.settingsHandler = SettingsHandler()
        self.settingsNotifier = SettingsNotifier(self)

        # created in createActions
        self.actions: Actions
        self.resizer: Resizer

    def setup(self):
        pass

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


Krita.instance().addExtension(SubwindowOrganizer(Krita.instance()))
