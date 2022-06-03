from krita import *
from .config import *
from .SettingsHandler import SettingsHandler
from .mouseEventHandler import MouseEventHandler


class subWindowFilterFloater(QMdiSubWindow):
    """Event catcher for floating windows."""

    def __init__(self, resizer, parent=None):
        super().__init__(parent)
        self.resizer = resizer

        self.mouseHandler = MouseEventHandler(resizer.mdiArea)
        self.mouseHandler.on_release_funs.append(
            self.handle_mouse_button_release
        )

        self.switching_in_progress = False

    @property
    def cursor(self):
        return self.mouseHandler.last_cursor_position

    def eventFilter(self, subwin, event):
        self.mouseHandler.update_on_event(subwin, event)

        if event.type() == QEvent.Move:
            self.handle_floater_move(subwin)

        return False

    def handle_mouse_button_release(self, subwin, event):
        # deminimize on dragging minimized window
        if subwin.isMinimized() and event.y() < -5:
            subwin.showNormal()
            # move to cursor position
            subwin.move(
                self.cursor.x() - 0.5*subwin.width(),
                self.cursor.y() - 10
            )

    # to resizer?
    def handle_floater_move(self, subwin):
        """prevent freeze on user changing krita windows mode"""
        if not SettingsHandler().is_subwindows:
            return

        if is_split_screen_event(self):
            if self.cursor.x() < 5:  # left edge
                self.resizer.refPosition = "left"
            else:
                self.resizer.refPosition = "right"

            h = self.resizer.mdiArea.height()
            lower_bound, upper_bound = SPLITMODERANGE
            if lower_bound * h < self.cursor.y() < upper_bound * h:
                self.switching_in_progress = True
                self.resizer.userModeSplit()
                self.switching_in_progress = False

        elif is_minimizer_event(self):
            subwin.showMinimized()

        # snap to border when floater moves
        else:
            self.resizer.snapToBorder(subwin)


def is_split_screen_event(windowFilter):
    return (
        windowFilter.cursor
        and not windowFilter.resizer.refNeeded
        and not windowFilter.mouseHandler.action_was_resize
        and not 5 < windowFilter.cursor.x() < windowFilter.resizer.mdiArea.width() - 5)


def is_minimizer_event(windowFilter):
    return (
        windowFilter.cursor
        and not windowFilter.mouseHandler.action_was_resize
        and windowFilter.cursor.y() > windowFilter.resizer.mdiArea.height() - 5)
