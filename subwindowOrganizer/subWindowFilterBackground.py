from krita import *
from PyQt5.QtWidgets import QWidget

from .config import *

#event catcher for windows on back
class subWindowFilterBackground(QMdiSubWindow):
	def __init__(self, resizer, parent=None):
		super().__init__(parent)
		self.resizer = resizer
		self.resizeBool = True
		self.cursor = None
		self.switchingInProgress = False

	def eventFilter(self, obj, e):
		if e.type() == QEvent.Resize:
			self.resizer.moveSubwindows()
			pass

		elif e.type() == QEvent.WindowStateChange:
			oldMinimized = False
			if int(e.oldState()) & int(Qt.WindowMinimized) != 0:
				oldMinimized = True
			if obj.isMinimized(): 
				obj.showNormal()
				return True
			if not obj.isMinimized() and oldMinimized:
				return True

		elif e.type() == QEvent.MouseButtonPress:
			print("press")
			cursorLocal = e.pos() #cursor in relation to window 
			if -25 < cursorLocal.x() < 25 or  obj.width()-25 < cursorLocal.x() < obj.width()+25: #it is a resizeBool, not move
				self.resizeBool = True
			else:
				self.resizeBool = False

		elif e.type() == QEvent.MouseButtonRelease:
			if not self.resizeBool:
				self.cursor = self.resizer.mdiArea.mapFromGlobal(e.globalPos()) #self.cursor in relation to mdiarea

		elif e.type() == QEvent.Move:
			def isUnderMouse(subwindow, cursor):
				if subwindow.pos().x() < cursor.x() < subwindow.pos().x() + subwindow.width() \
				and subwindow.pos().y() < cursor.y() < subwindow.pos().y() + subwindow.height():
					return True
				return False

			print(self.resizeBool, self.cursor)
			if (not self.resizeBool) and self.cursor != None and not self.switchingInProgress:
				self.switchingInProgress = True
				for subwindow in self.resizer.mdiArea.subWindowList():
					if isUnderMouse(subwindow, self.cursor) and subwindow != obj:
						if subwindow != self.resizer.activeSubwin and subwindow != self.resizer.otherSubwin: #other floater, swap with it
							if obj == self.resizer.activeSubwin:
								self.resizer.switchBackgroundAndFloater(self.resizer.activeSubwin, subwindow)
							else:
								self.resizer.switchBackgroundAndFloater(self.resizer.otherSubwin, subwindow)

							self.resizeBool = False
							return False

				for subwindow in self.resizer.mdiArea.subWindowList():
					if isUnderMouse(subwindow, self.cursor) and subwindow != obj:
						if subwindow == self.resizer.activeSubwin or subwindow == self.resizer.otherSubwin: #other background window - swap
							self.resizer.switchBackgroundWindows()
							print("SWITCH")
							self.resizer.moveSubwindows()
							break

			self.resizeBool = True
			self.cursor = None
			self.switchingInProgress = False

			return True



		return False