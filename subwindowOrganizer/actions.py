from krita import *

from dataclasses import dataclass
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from subwindowOrganizer import SubwindowOrganizer


@dataclass
class ActionsContainer:
    organizer_toggle: QAction
    pick_subwindow: QAction
    open_overview: QAction


@dataclass
class OrganizerActions:
    organizer: 'SubwindowOrganizer'

    def pickSubwindow(self) -> None:
        """switching between subwindows - user action"""
        if not self.organizer.resizer.subWindowFilterAll.isMaximized:
            self.organizer.resizer.userToggleSubwindow()

    def openOverview(self) -> None:
        """opens grayscale overview"""
        self.organizer.resizer.userOpenOverview()

    def organizerToggle(self, toggled: bool) -> None:
        """toggles the whole plugin off and on"""
        self.organizer.settingsHandler.write_is_toggled(toggled)
        if (self.organizer.settingsHandler.is_subwindows
                and self.organizer.settingsHandler.is_toggled):
            self.organizer.actions.pick_subwindow.setVisible(True)
            self.organizer.actions.open_overview.setVisible(True)
            self.organizer.resizer.userTurnOn()

        self.organizer.actions.pick_subwindow.setVisible(False)
        self.organizer.actions.open_overview.setVisible(False)
        self.organizer.resizer.userTurnOff()


class ActionBuilder:

    def __init__(self, organizer: 'SubwindowOrganizer', window):
        self.organizer = organizer
        self.window = window
        self.actions = OrganizerActions(organizer)

    def build_actions(self) -> ActionsContainer:
        return ActionsContainer(
            self._build_organizer_toggle(),
            self._build_pick_subwindow(),
            self._build_open_overview()
        )

    def _build_organizer_toggle(self) -> QAction:
        organizer_toggle = self.window.createAction(
            "organizerToggle", "Toggle organizer", "view"
        )
        organizer_toggle.setCheckable(True)
        organizer_toggle.setChecked(self.organizer.settingsHandler.is_toggled)
        organizer_toggle.toggled.connect(self.actions.organizerToggle)
        organizer_toggle.setVisible(
            self.organizer.settingsHandler.is_subwindows
        )

        return organizer_toggle

    def _build_pick_subwindow(self) -> QAction:
        pick_subwindow = self.window.createAction(
            "pickSubwindow", "Pick subwindow", "view")
        pick_subwindow.triggered.connect(self.actions.pickSubwindow)
        pick_subwindow.setVisible(False)

        return pick_subwindow

    def _build_open_overview(self) -> QAction:
        open_overview = self.window.createAction(
            "openOverview", "Open canvas overview", "view")
        open_overview.triggered.connect(self.actions.openOverview)
        open_overview.setVisible(False)

        return open_overview
