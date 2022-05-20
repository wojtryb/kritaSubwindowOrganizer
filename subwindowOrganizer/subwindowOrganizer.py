from krita import *

from .Resizer import Resizer
from .actions import ActionsContainer, ActionBuilder
from .SettingsHandler import SettingsHandler, SettingsNotifier


class SubwindowOrganizer(Extension):

    def __init__(self, parent):
        super(SubwindowOrganizer, self).__init__(parent)

        self.settingsHandler = SettingsHandler()
        self.settingsNotifier = SettingsNotifier(self)

        # created in createActions
        self.actionBuilder: ActionBuilder
        self.actions: ActionsContainer
        self.resizer: Resizer

    def setup(self):
        pass

    def createActions(self, window):
        """creates actions displayed in the view menu"""
        qwin = window.qwindow()
        toggleAtStart = self.settingsHandler.is_toggled and self.settingsHandler.is_subwindows

        self.resizer = Resizer(qwin, toggleAtStart)
        self.actionBuilder = ActionBuilder(self, window)
        self.actions = self.actionBuilder.build_actions()


Krita.instance().addExtension(SubwindowOrganizer(Krita.instance()))
