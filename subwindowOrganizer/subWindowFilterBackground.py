from krita import *
from PyQt5.QtWidgets import QWidget

#event catcher for windows on back
class subWindowFilterBackground(QMdiSubWindow):
	def __init__(self, resizer, parent=None):
		super().__init__(parent)
		self.resizer = resizer
		self.resize = True

	def eventFilter(self, obj, e):
		if e.type() == QEvent.Resize:
			self.resizer.moveSubwindows()

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
			cursorLocal = e.pos() #cursor in relation to window 
			if -25 < cursorLocal.x() < 25 or  obj.width()-25 < cursorLocal.x() < obj.width()+25: #it is a resize, not move
				self.resize = True
			else:
				self.resize = False

		elif e.type() == QEvent.MouseButtonRelease:
			cursor = self.resizer.mdiArea.mapFromGlobal(e.globalPos()) #cursor in relation to mdiarea
			def isUnderMouse(subwindow, cursor):
				if subwindow.pos().x() < cursor.x() < subwindow.pos().x() + subwindow.width() \
				and subwindow.pos().y() < cursor.y() < subwindow.pos().y() + subwindow.height():
					return True
				return False

			if not self.resize:
				for subwindow in self.resizer.mdiArea.subWindowList():
					if isUnderMouse(subwindow, cursor) and subwindow != obj:
						if subwindow != self.resizer.activeSubwin and subwindow != self.resizer.otherSubwin: #other floater, swap with it
							if obj == self.resizer.activeSubwin:
								self.resizer.switchBackgroundAndFloater(self.resizer.activeSubwin, subwindow)
							else:
								self.resizer.switchBackgroundAndFloater(self.resizer.otherSubwin, subwindow)

							self.resize = False
							return False

				for subwindow in self.resizer.mdiArea.subWindowList():
					if isUnderMouse(subwindow, cursor) and subwindow != obj:
						if subwindow == self.resizer.activeSubwin or subwindow == self.resizer.otherSubwin: #other background window - swap
							self.resizer.switchBackgroundWindows()

							# print(subwindow.children())
							# for i in range(4):
							# 	print(i)
							# 	v = subwindow.children()[i]
							# 	v2 = obj.children()[i]
							# 	if not i == 1:
							# 		sv = v.size()
							# 		sv2 = v2.size()

							# 	temp = QWidget()
							# 	v.setParent(temp)
							# 	v2.setParent(subwindow)
							# 	v.setParent(obj)

							# 	if not i == 1:
							# 		v.show()
							# 		v2.show()
							# 		v.resize(sv2)
							# 		v2.resize(sv)

							break

			self.resize = True
		return False