from krita import *
from .config import *

#event catcher for floating windows
class subWindowFilterFloater(QMdiSubWindow):
	def __init__(self, resizer, parent=None):
		super().__init__(parent)
		self.resizer = resizer
		self.resizeBool = False
		self.cursor = None
		self.switchingInProgress = False
	def eventFilter(self, obj, e):

		if e.type() == QEvent.MouseButtonPress:
			cursorLocal = e.pos() #cursor in relation to window 
			if -25 < cursorLocal.x() < 25 or obj.width()-25 < cursorLocal.x() < obj.width()+25 \
			or -3 < cursorLocal.y() < 3 or obj.height()-25 < cursorLocal.y() < obj.height()+25: #it is a resizeBool, not move
				self.resizeBool = True
			else:
				self.resizeBool = False

		elif e.type() == QEvent.MouseButtonRelease:
			self.cursor = self.resizer.mdiArea.mapFromGlobal(e.globalPos())

			if obj.isMinimized() and e.y() < -5: #deminimize on dragging minimized window
				obj.showNormal()
				obj.move(self.cursor.x() - 0.5*obj.width(), self.cursor.y() - 10) #move to cursor position

		elif e.type() == QEvent.Move:
			if Application.readSetting("", "mdi_viewmode", "1") == "0": #prevent freeze on user changing krita windows mode
				# drag and drop action - going into split mode
				if self.cursor != None and not self.resizer.refNeeded and not self.resizeBool\
				and (self.cursor.x() < 5 or self.cursor.x() > self.resizer.mdiArea.width() - 5): 

					if self.cursor.x() < 5: #left edge
						self.resizer.refPosition = "left"
					else:
						self.resizer.refPosition = "right"

					h = self.resizer.mdiArea.height()
					if SPLITMODERANGE[0] * h < self.cursor.y() < SPLITMODERANGE[1] * h:
						self.switchingInProgress = True
						self.resizer.userModeSplit()
						self.switchingInProgress = False
						self.cursor = None
						return True

				#drag and dtop action for minimizing the window
				if self.cursor != None and not self.resizeBool and self.cursor.y() > self.resizer.mdiArea.height() - 5:
					obj.showMinimized()
					return True

				self.resizer.snapToBorder(obj) #snap to border when floater moves

		return False