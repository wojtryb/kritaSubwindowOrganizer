from krita import *
from PyQt5.QtWidgets import QWidget

#event catcher for windows on back
class subWindowFilterBackground(QMdiSubWindow):
	def __init__(self, resizer, parent=None):
		super().__init__(parent)
		self.resizer = resizer

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
		return False