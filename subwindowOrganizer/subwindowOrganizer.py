from dataclasses import dataclass
from krita import *
from PyQt5.QtWidgets import QMessageBox

from .Resizer import Resizer
from .actions import Actions, ActionBuilder


class SubwindowOrganizer(Extension):

    def __init__(self, parent):
        super(SubwindowOrganizer, self).__init__(parent)

        self.inProgress: bool
        self.isToggled: bool
        self.kritaWindowsMode: bool

        self.settingsNotifier: None  # Notifier

        self.actions: Actions
        self.resizer: Resizer

    def setup(self):
        """reading values saved in krita settings and creating a
        notifier for settings changed event.
        """
        if Application.readSetting("SubwindowOrganizer", "organizerToggled", "true") == "true":
            self.isToggled = True
        if Application.readSetting("", "mdi_viewmode", "1") == "0":
            self.kritaWindowsMode = True

        self.settingsNotifier = Application.notifier()
        self.settingsNotifier.setActive(True)
        self.settingsNotifier.configurationChanged.connect(
            self.settingsChangedEvent
        )

    def createActions(self, window):
        """creates actions displayed in the view menu"""
        qwin = window.qwindow()
        toggleAtStart = self.isToggled and self.kritaWindowsMode

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
        Application.writeSetting("SubwindowOrganizer",
                                 "organizerToggled", str(toggled).lower())
        self.isToggled = toggled
        if self.kritaWindowsMode and self.isToggled:
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
        if Application.readSetting("", "mdi_viewmode", "1") == "0":
            newMode = True
        else:
            newMode = False

        if self.kritaWindowsMode ^ newMode:  # mode was changed in krita settings
            self.kritaWindowsMode = newMode
            if self.kritaWindowsMode:  # changed from tabs to subwindows
                # addon now can be activated and deactivated
                self.organizerToggleAction.setVisible(True)
                if self.isToggled:  # addon is on, so we can activate it
                    self.resizer.userTurnOn()
            else:  # mode changed from subwindows to tab
                self.organizerToggleAction.setVisible(False)
                if self.isToggled:  # addon was on
                    self.resizer.userTurnOff()


Krita.instance().addExtension(SubwindowOrganizer(Krita.instance()))
