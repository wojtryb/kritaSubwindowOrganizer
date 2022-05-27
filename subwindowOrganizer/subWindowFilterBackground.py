from krita import *
from typing import Optional
from copy import copy

from .config import *

# TODO: event handler class?

# TODO: move to: subwindow helpers


def isUnderMouse(subwin, cursor):
    if (
            subwin.pos().x() < cursor.x() < subwin.pos().x() + subwin.width() and
            subwin.pos().y() < cursor.y() < subwin.pos().y() + subwin.height()):
        return True
    return False


class subWindowFilterBackground(QMdiSubWindow):
    """Event catcher for background windows"""

    def __init__(self, resizer, parent=None):
        super().__init__(parent)
        self.resizer = resizer

        self.resetFlags()
        self.resizeBool: bool
        self.cursor: Optional[QCursor]
        self.switchingInProgress: bool

    def resetFlags(self):
        '''These flags make sure that the move event was caused by mouse
        input, not script.'''
        self.resizeBool = False
        self.cursor = None
        self.switchingInProgress = False

    def eventFilter(self, obj, e):
        if e.type() == QEvent.Resize:
            self.resizer.moveSubwindows()  # update the second window

        elif e.type() == QEvent.WindowStateChange:  # title bar buttons override
            ret = self.handle_window_state_change_event(obj, e)
            if ret:
                return True

        elif e.type() == QEvent.MouseButtonPress:
            cursorLocal = e.pos()  # cursor in relation to window
            self.resizeBool = is_resize_event(cursorLocal, obj)

        elif e.type() == QEvent.MouseButtonRelease:
            self.cursor = self.resizer.mdiArea.mapFromGlobal(e.globalPos())
            self.lastCursorReleased = copy(self.cursor)

        elif e.type() == QEvent.Move:
            self.handle_move_event(obj)
            self.resetFlags()
            return True

        return False

    def handle_window_state_change_event(self, obj, e):
        oldMinimized = int(e.oldState()) & int(Qt.WindowMinimized) != 0

        # TODO: refractor this, whatever it does
        if obj.isMinimized():  # minimize button toggled - discard all changes
            if obj.isMaximized():
                obj.showMaximized()
            else:
                obj.showNormal()
            return True

        if not obj.isMinimized() and oldMinimized:  # ?
            return True

        if self.resizer.views == 1:  # to make sure
            obj.showMaximized()

    def handle_move_event(self, obj):
        if is_move_event(self):
            self.switchingInProgress = True

            done = self.swap_floaters_if_needed(obj)
            if not done:
                done = self.swap_backgrounders_if_needed(obj)
            if not done:
                done = self.enter_one_window_mode(obj)
            # entering split mode is done by floaters movement

    def swap_floaters_if_needed(self, obj):
        """Drag and drop action for swapping a background window with
        floater.
        """
        def is_swap_needed(subwindow):
            return (
                isUnderMouse(subwindow, self.cursor)
                and not subwindow.isMinimized())

        for floater in self.resizer.floaters - {obj}:  # swapping with floaters
            if not is_swap_needed(floater):
                continue

            self.resizer.switchBackgroundAndFloater(obj, floater)

            # TODO: can floater snap be reused here?
            # snapping to border, if floater got smaller and was on
            # bottom or right closer to the right border of canvas than left one
            x = obj.pos().x()
            y = obj.pos().y()
            sX = obj.width()
            sY = obj.height()
            self.resizer.resizeFloater(obj)
            sX -= obj.width()
            sY -= obj.height()

            if x > self.resizer.mdiArea.width() - obj.width() - x:
                x += sX  # self.resizer.mdiArea.width() - sX
            # closer to the right border of canvas than left one
            if y > self.resizer.mdiArea.height() - obj.height() - y:
                y += sY  # self.resizer.mdiArea.height() - sY
            obj.move(x, y)

            return True
        return False

    def swap_backgrounders_if_needed(self, obj):
        """Drag and drop action for swapping two background windows."""
        def is_swap_needed(obj):
            if not obj in self.resizer.backgrounders:
                return False
            other_window = tuple((self.resizer.backgrounders - {obj}))[0]
            return isUnderMouse(other_window, self.cursor)

        if is_swap_needed(obj):
            self.resizer.switchBackgroundWindows()
            self.resizer.moveSubwindows()
            return True
        return False

    def enter_one_window_mode(self, obj):
        """Drag and drop action for leaving split screen mode."""
        if not (
                self.resizer.refNeeded
                and obj in self.resizer.backgrounders
                and 200 < self.cursor.y() < self.resizer.mdiArea.height() - 10
                and 5 < self.cursor.x() < self.resizer.mdiArea.width() - 5):  # in mdiArea
            return False

        if obj == self.resizer.activeSubwin:
            self.resizer.swap_backgrounders()

        self.resizer.userModeOneWindow()
        obj.move(
            self.lastCursorReleased.x() - 0.5*obj.width(),
            self.lastCursorReleased.y() - 10
        )
        return True


def is_resize_event(cursor, obj):
    return (
        -25 < cursor.x() < 25
        or -3 < cursor.y() < 3
        or obj.width()-25 < cursor.x() < obj.width()+25
        or obj.height()-25 < cursor.y() < obj.height()+25)


def is_move_event(windowFilter):
    return (
        not windowFilter.resizeBool
        and not windowFilter.switchingInProgress
        and windowFilter.cursor)
