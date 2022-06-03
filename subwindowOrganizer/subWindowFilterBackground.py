from krita import *
from typing import Optional

from .config import *
from .mouseEventHandler import MouseEventHandler

# TODO: event handler class?


class subWindowFilterBackground(QMdiSubWindow):
    """Event catcher for background windows"""

    def __init__(self, resizer, parent=None):
        super().__init__(parent)
        self.resizer = resizer
        self.mouseHandler = MouseEventHandler(resizer.mdiArea)
        self.switching_in_progress: bool = False

    @property
    def cursor(self):
        return self.mouseHandler.last_cursor_position

    def eventFilter(self, subwin, event):
        self.mouseHandler.update_on_event(subwin, event)

        if event.type() == QEvent.Resize:
            self.resizer.moveSubwindows()  # update the second window

        elif event.type() == QEvent.WindowStateChange:  # title bar buttons override
            return self.handle_window_state_change_event(subwin, event)

        elif event.type() == QEvent.Move:
            return self.handle_move_event(subwin)

        return False

    def handle_window_state_change_event(self, subwin, event):
        oldMinimized = int(event.oldState()) & int(Qt.WindowMinimized) != 0

        # TODO: refractor this, whatever it does
        if subwin.isMinimized():  # minimize button toggled - discard all changes
            if subwin.isMaximized():
                subwin.showMaximized()
            else:
                subwin.showNormal()
            return True

        if not subwin.isMinimized() and oldMinimized:  # ?
            return True

        if self.resizer.views == 1:  # to make sure
            subwin.showMaximized()
        return False

    def handle_move_event(self, subwin):
        if not is_move_event(self):
            return False

        self.switching_in_progress = True
        done = self.swap_floaters_if_needed(subwin)
        if not done:
            done = self.swap_backgrounders_if_needed(subwin)
        if not done:
            done = self.enter_one_window_mode(subwin)
        self.switching_in_progress = False
        return True

    def swap_floaters_if_needed(self, subwin):
        """Drag and drop action for swapping a background window with
        floater.
        """
        def is_swap_needed(subwindow):
            return (
                isUnderMouse(subwindow, self.cursor)
                and not subwindow.isMinimized())

        # swapping with floaters
        for floater in self.resizer.floaters - {subwin}:
            if not is_swap_needed(floater):
                continue

            self.resizer.switchBackgroundAndFloater(subwin, floater)

            # TODO: can floater snap be reused here?
            # snapping to border, if floater got smaller and was on
            # bottom or right closer to the right border of canvas than left one
            x = subwin.pos().x()
            y = subwin.pos().y()
            sX = subwin.width()
            sY = subwin.height()
            self.resizer.resizeFloater(subwin)
            sX -= subwin.width()
            sY -= subwin.height()

            if x > self.resizer.mdiArea.width() - subwin.width() - x:
                x += sX  # self.resizer.mdiArea.width() - sX
            # closer to the right border of canvas than left one
            if y > self.resizer.mdiArea.height() - subwin.height() - y:
                y += sY  # self.resizer.mdiArea.height() - sY
            subwin.move(x, y)

            return True
        return False

    def swap_backgrounders_if_needed(self, subwin):
        """Drag and drop action for swapping two background windows."""
        def is_swap_needed(subwin):
            if not subwin in self.resizer.backgrounders:
                return False
            other_window = tuple((self.resizer.backgrounders - {subwin}))[0]
            return isUnderMouse(other_window, self.cursor)

        if is_swap_needed(subwin):
            self.resizer.switchBackgroundWindows()
            self.resizer.moveSubwindows()
            return True
        return False

    def enter_one_window_mode(self, subwin):
        """Drag and drop action for leaving split screen mode."""
        if not (
                self.resizer.refNeeded
                and subwin in self.resizer.backgrounders
                and 200 < self.cursor.y() < self.resizer.mdiArea.height() - 10
                and 5 < self.cursor.x() < self.resizer.mdiArea.width() - 5):  # in mdiArea
            return False

        if subwin == self.resizer.activeSubwin:
            self.resizer.swap_backgrounders()

        self.resizer.userModeOneWindow()
        subwin.move(
            self.cursor.x() - 0.5*subwin.width(),
            self.cursor.y() - 10
        )
        return True


def isUnderMouse(subwin, cursor):
    if (
            subwin.pos().x() < cursor.x() < subwin.pos().x() + subwin.width() and
            subwin.pos().y() < cursor.y() < subwin.pos().y() + subwin.height()):
        return True
    return False


def is_move_event(windowFilter):
    return (
        not windowFilter.mouseHandler.action_was_resize
        and not windowFilter.switching_in_progress
        and windowFilter.cursor)
