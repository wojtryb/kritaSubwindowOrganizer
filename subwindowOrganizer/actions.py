from krita import *

from dataclasses import dataclass
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from subwindowOrganizer import SubwindowOrganizer


@dataclass
class Actions:
    organizer_toggle: QAction
    pick_subwindow: QAction
    open_overview: QAction


@dataclass
class ActionBuilder:
    organizer: 'SubwindowOrganizer'
    window: None  # window

    def build_actions(self):
        return Actions(
            self._build_organizer_toggle(),
            self._build_pick_subwindow(),
            self._build_open_overview()
        )

    def _build_organizer_toggle(self):
        organizer_toggle = self.window.createAction(
            "organizerToggle", "Toggle organizer", "view"
        )
        organizer_toggle.setCheckable(True)
        organizer_toggle.setChecked(self.organizer.isToggled)
        organizer_toggle.toggled.connect(self.organizer.organizerToggle)
        organizer_toggle.setVisible(self.organizer.kritaWindowsMode)

        return organizer_toggle

    def _build_pick_subwindow(self):
        pick_subwindow = self.window.createAction(
            "pickSubwindow", "Pick subwindow", "view")
        pick_subwindow.triggered.connect(self.organizer.pickSubwindow)
        pick_subwindow.setVisible(False)

        return pick_subwindow

    def _build_open_overview(self):
        open_overview = self.window.createAction(
            "openOverview", "Open canvas overview", "view")
        open_overview.triggered.connect(self.organizer.openOverview)
        open_overview.setVisible(False)

        return open_overview
