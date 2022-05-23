from krita import *

from .Resizer import Resizer
from .actions import ActionsContainer, ActionBuilder
from .SettingsHandler import SettingsHandler, SettingsNotifier


class SubwindowOrganizer(Extension):
    """Plugin that changes the way subwindows in krita are handled."""

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
        """Initialize everything that need access to krita window
        object.
        """
        qwin = window.qwindow()
        toggleAtStart = self.settingsHandler.is_toggled and self.settingsHandler.is_subwindows

        self.resizer = Resizer(qwin, toggleAtStart)
        self.actionBuilder = ActionBuilder(self, window)
        self.actions = self.actionBuilder.build_actions()


Krita.instance().addExtension(SubwindowOrganizer(Krita.instance()))
