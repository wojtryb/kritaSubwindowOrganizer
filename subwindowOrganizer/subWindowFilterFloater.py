from krita import *

#event catcher for floating windows
class subWindowFilterFloater(QMdiSubWindow):
	def __init__(self, resizer, parent=None):
		super().__init__(parent)
		self.resizer = resizer
	def eventFilter(self, obj, e):
		if e.type() == QEvent.Move: #snap to border when floater moves
			self.resizer.snapToBorder(obj)

		return False
 
