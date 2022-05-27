from krita import *

from .config import *
from .SettingsHandler import SettingsHandler


class subWindowFilterAll(QMdiSubWindow):
    """event catcher for every window - both floaters and back ones"""

    def __init__(self, resizer, parent=None):
        super().__init__(parent)
        self.resizer = resizer
        self.isMaximized = False  # is any window currently maximized

    def eventFilter(self, obj, e):
        """Override krita minimize and maximize actions"""

        if e.type() == QEvent.WindowStateChange:
            # prevent freeze on user changing krita windows mode

            if not SettingsHandler().is_subwindows:
                return False

            oldMaximized = False
            if int(e.oldState()) & int(Qt.WindowMaximized) != 0:
                oldMaximized = True

            if obj.isMaximized() and not oldMaximized:  # there was a change to maximized state
                self.hideAllExcept(self.resizer, exception=obj)
                self.isMaximized = True
            if not obj.isMaximized() and oldMaximized:  # there was a change to normal from maximize
                self.showAll(self.resizer)
                self.isMaximized = False

        elif e.type() == QEvent.Close:  # dont seem to work anyway...
            # krita will crush if there will be a maximized window in usual close handling - it has to be made normal before it
            obj.showNormal()
            self.showAll(self.resizer)
            self.isMaximized = False

        return False

    def hideAllExcept(self, resizer, exception):
        """hiding windows, when one gets maximized"""
        for subwindow in resizer.all_subwindows:
            if subwindow != exception:
                subwindow.hide()

        for backgrounder in resizer.backgrounders:
            backgrounder.setMinimumWidth(0)

    def showAll(self, resizer):
        """showing all hidden window, when maximized turns normal"""
        for subwindow in resizer.mdiArea.subWindowList():
            subwindow.show()

        for backgrounder in resizer.backgrounders:
            backgrounder.setMinimumWidth(MINIMALCOLUMNWIDTH)
