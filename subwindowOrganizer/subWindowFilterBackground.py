from krita import *
from PyQt5.QtWidgets import QWidget

from .config import *

#event catcher for windows on back
class subWindowFilterBackground(QMdiSubWindow):
	def __init__(self, resizer, parent=None):
		super().__init__(parent)
		self.resizer = resizer
		self.resetFlags()

	def eventFilter(self, obj, e):
		if e.type() == QEvent.Resize:
			self.resizer.moveSubwindows() #update the second window

		elif e.type() == QEvent.WindowStateChange:
			oldMinimized = False
			if int(e.oldState()) & int(Qt.WindowMinimized) != 0:
				oldMinimized = True
			if obj.isMinimized(): 
				if obj.isMaximized(): obj.showMaximized()
				else: obj.showNormal()
				return True
			if not obj.isMinimized() and oldMinimized:
				return True

			if self.resizer.views == 1:
				obj.showMaximized()

		elif e.type() == QEvent.MouseButtonPress:
			cursorLocal = e.pos() #cursor in relation to window 
			if -25 < cursorLocal.x() < 25 or obj.width()-25 < cursorLocal.x() < obj.width()+25 \
			or -3 < cursorLocal.y() < 3 or obj.height()-25 < cursorLocal.y() < obj.height()+25: #it is a resizeBool, not move
				self.resizeBool = True
			else:
				self.resizeBool = False

		elif e.type() == QEvent.MouseButtonRelease:
			self.cursor = self.resizer.mdiArea.mapFromGlobal(e.globalPos()) #self.cursor in relation to mdiarea

		elif e.type() == QEvent.Move:
			if (not self.resizeBool) and not self.switchingInProgress and self.cursor != None:
				self.switchingInProgress = True

				done = self.swapFloaters(obj)
				if not done: done = self.swapBackgrounders(obj)
				if not done: done = self.enterOneWindowMode(obj) #go out of split mode on mouse on bottom
				#entering split mode is done by floaters movement

			self.resetFlags()
			return True

		return False

	def isUnderMouse(self, subwindow, cursor):
		if subwindow.pos().x() < cursor.x() < subwindow.pos().x() + subwindow.width() \
			and subwindow.pos().y() < cursor.y() < subwindow.pos().y() + subwindow.height():
				return True
		return False

	def resetFlags(self): #these flags make sure that the move event was caused by mouse input, not script
		self.resizeBool = False
		self.cursor = None
		self.switchingInProgress = False

	def swapFloaters(self, obj):
		for subwindow in self.resizer.mdiArea.subWindowList(): #swapping with floaters
			if self.isUnderMouse(subwindow, self.cursor) and subwindow != obj:
				if subwindow != self.resizer.activeSubwin and subwindow != self.resizer.otherSubwin: #other floater, swap with it
					if obj == self.resizer.activeSubwin:
						self.resizer.switchBackgroundAndFloater(self.resizer.activeSubwin, subwindow)
					else:
						self.resizer.switchBackgroundAndFloater(self.resizer.otherSubwin, subwindow)
					return True
		return False

	def swapBackgrounders(self, obj):
		for subwindow in self.resizer.mdiArea.subWindowList(): #swapping backgrounders
			if self.isUnderMouse(subwindow, self.cursor) and subwindow != obj:
				if subwindow == self.resizer.activeSubwin or subwindow == self.resizer.otherSubwin: #other background window - swap
					self.resizer.switchBackgroundWindows()
					self.resizer.moveSubwindows()
					return True
		return False

	def enterOneWindowMode(self, obj):
		if self.resizer.refNeeded and obj == self.resizer.otherSubwin and self.cursor.y() > 200 \
		and 0 < self.cursor.x() < self.resizer.mdiArea.width() and 0 < self.cursor.y() < self.resizer.mdiArea.height(): #in mdiArea
			# self.resizer.userToggleMode()
			Application.action("splitScreen").trigger()
			return True
		return False
