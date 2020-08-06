from krita import *

#event catcher for floating windows
class subWindowFilterFloater(QMdiSubWindow):
	def __init__(self, resizer, parent=None):
		super().__init__(parent)
		self.resizer = resizer
		self.cursor = None
		self.switchingInProgress = False
	def eventFilter(self, obj, e):
		if e.type() == QEvent.MouseButtonRelease:
			self.cursor = self.resizer.mdiArea.mapFromGlobal(e.globalPos())

		elif e.type() == QEvent.Move: #snap to border when floater moves
			print(self.cursor.x())
			if self.cursor != None and not self.resizer.refNeeded and self.cursor.x() < 5: # going into split mode
				h = self.resizer.mdiArea.height()
				if 0.3 * h < self.cursor.y() < 0.6 * h:
					self.switchingInProgress = True
					self.resizer.userToggleMode()
					self.switchingInProgress = False
					return True

			self.resizer.snapToBorder(obj)

		return False
 
