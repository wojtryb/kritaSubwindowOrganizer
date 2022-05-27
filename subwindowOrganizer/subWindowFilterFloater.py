from krita import *
from .config import *
from .SettingsHandler import SettingsHandler


class subWindowFilterFloater(QMdiSubWindow):
    """Event catcher for floating windows."""

    def __init__(self, resizer, parent=None):
        super().__init__(parent)
        self.resizer = resizer
        self.resizeBool = False
        self.cursor = None
        self.switchingInProgress = False

    def eventFilter(self, obj, e):
        if e.type() == QEvent.MouseButtonPress:
            self.handle_mouse_button_press(obj, e)
        elif e.type() == QEvent.MouseButtonRelease:
            self.handle_mouse_button_release(obj, e)
        elif e.type() == QEvent.Move:
            self.handle_floater_move(obj)
        return False

    def handle_mouse_button_press(self, obj, e):
        # reuse code from background filter!
        cursorLocal = e.pos()  # cursor in relation to window
        self.resizeBool = (
            -25 < cursorLocal.x() < 25
            or -3 < cursorLocal.y() < 3
            or obj.width()-25 < cursorLocal.x() < obj.width()+25
            or obj.height()-25 < cursorLocal.y() < obj.height()+25
        )

    def handle_mouse_button_release(self, obj, e):
        self.cursor = self.resizer.mdiArea.mapFromGlobal(e.globalPos())
        # deminimize on dragging minimized window
        if obj.isMinimized() and e.y() < -5:
            obj.showNormal()
            # move to cursor position
            obj.move(
                self.cursor.x() - 0.5*obj.width(),
                self.cursor.y() - 10
            )

    def handle_floater_move(self, obj):
        """prevent freeze on user changing krita windows mode"""
        if not SettingsHandler().is_subwindows:
            return

        if is_split_screen_event(self):
            if self.cursor.x() < 5:  # left edge
                self.resizer.refPosition = "left"
            else:
                self.resizer.refPosition = "right"

            h = self.resizer.mdiArea.height()
            if SPLITMODERANGE[0] * h < self.cursor.y() < SPLITMODERANGE[1] * h:
                self.switchingInProgress = True
                self.resizer.userModeSplit()
                self.switchingInProgress = False
                self.cursor = None

        elif is_minimizer_event(self):
            obj.showMinimized()

        # snap to border when floater moves
        else:
            self.resizer.snapToBorder(obj)


def is_split_screen_event(windowFilter):
    return (
        windowFilter.cursor
        and not windowFilter.resizer.refNeeded
        and not windowFilter.resizeBool
        and not 5 < windowFilter.cursor.x() < windowFilter.resizer.mdiArea.width() - 5)


def is_minimizer_event(windowFilter):
    return (
        windowFilter.cursor
        and not windowFilter.resizeBool
        and windowFilter.cursor.y() > windowFilter.resizer.mdiArea.height() - 5)
