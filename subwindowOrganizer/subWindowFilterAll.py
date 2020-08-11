from krita import *

from .config import *

#event catcher for every window - both floaters and back ones
class subWindowFilterAll(QMdiSubWindow):
	def __init__(self, resizer, parent=None):
		super().__init__(parent)
		self.resizer = resizer

		self.isMaximized = False #is any window currently maximized
	def eventFilter(self, obj, e):
			#override krita minimize and maximize actions
		if e.type() == QEvent.WindowStateChange:
			if Application.readSetting("", "mdi_viewmode", "1") == "0": #prevent freeze on user changing krita windows mode
				oldMaximized = False
				if int(e.oldState()) & int(Qt.WindowMaximized) != 0:
					oldMaximized = True

				if obj.isMaximized() and not oldMaximized: #there was a change to maximized state
					self.hideAllExcept(self.resizer, exception=obj)
					self.isMaximized = True
				if not obj.isMaximized() and oldMaximized: #there was a change to normal from maximize
					self.showAll(self.resizer)
					self.isMaximized = False

			# krita will crush if there will be a maximized window in usual close handling - it has to be made normal before it
		if e.type() == QEvent.Close: #dont seem to work anyway...
			obj.showNormal()
			self.showAll(self.resizer)
			self.isMaximized = False

		return False

	#-----------FUNCTIONS----------
	#hiding windows, when one gets maximized
	def hideAllExcept(self, resizer, exception):
		for subwindow in resizer.mdiArea.subWindowList():
			if subwindow != exception: subwindow.hide()
		if resizer.activeSubwin != None: resizer.activeSubwin.setMinimumWidth(0) #minimal width would not allow them to hide properly
		if resizer.otherSubwin != None: resizer.otherSubwin.setMinimumWidth(0)

	#showind all hidden window, when maximized turns normal
	def showAll(self, resizer):
		for subwindow in resizer.mdiArea.subWindowList():
			subwindow.show()
		if resizer.activeSubwin != None: resizer.activeSubwin.setMinimumWidth(MINIMALCOLUMNWIDTH) #getting minimal width again
		if resizer.otherSubwin != None: resizer.otherSubwin.setMinimumWidth(MINIMALCOLUMNWIDTH)