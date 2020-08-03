from krita import *
import sip
 
#event catcher for the workspace - changes in size, and subwindows added and removed
class mdiAreaFilter(QMdiArea):
	def __init__(self, resizer, parent=None):
		super().__init__(parent)
		self.resizer = resizer
		self.sizeBefore = [resizer.mdiArea.width(), resizer.mdiArea.height()]

	def eventFilter(self, obj, e):
		if not sip.isdeleted(self.resizer.mdiArea):
			if e.type() == QEvent.Resize:
				self.resizer.moveSubwindows()
				self.moveFloatersOnAreaChange(self.resizer) #move floaters
				self.sizeBefore = [self.resizer.mdiArea.width(), self.resizer.mdiArea.height()] #changes done, can actualize width and height of workspace

			#there are many more events, as subwindows aren't the only children, so the change have to be found as change in list size
			if e.type() == QEvent.ChildAdded:
				if self.resizer.views < len(self.resizer.mdiArea.subWindowList()):
					self.viewOpenedEvent(self.resizer)
					self.resizer.views = len(self.resizer.mdiArea.subWindowList())

			if e.type() == QEvent.ChildRemoved:
				if self.resizer.views > len(self.resizer.mdiArea.subWindowList()):
					self.viewClosedEvent(self.resizer)
					self.resizer.views = len(self.resizer.mdiArea.subWindowList())

		return False



	#-----------FUNCTIONS----------#
	#each time when subwindow is closed
	def viewClosedEvent(self, resizer):
		def checkIfDeleted(obj):
			if obj in resizer.mdiArea.subWindowList():
				return obj
			else:
				return None

		resizer.views = len(resizer.mdiArea.subWindowList())

		resizer.activeSubwin = checkIfDeleted(resizer.activeSubwin)
		resizer.otherSubwin = checkIfDeleted(resizer.otherSubwin)

		#active was closed - make the reference take its place
		if resizer.activeSubwin == None and resizer.views >= 1: 
			if resizer.otherSubwin == None: #no ref window (non-split mode)
				resizer.getOtherSubwin()
				resizer.toggleAlwaysOnTop(resizer.otherSubwin, False)
			resizer.otherSubwin.resize(resizer.mdiArea.width() - resizer.columnWidth, resizer.mdiArea.height())
			resizer.otherSubwin.showNormal()
			resizer.activeSubwin = resizer.otherSubwin
			resizer.otherSubwin = None

		if resizer.views == 1:
			resizer.getActiveSubwin()
			if resizer.activeSubwin != None: #bugfix - when multiple windows are closed at once, it can get here with both views deleted
				view = resizer.activeSubwin.children()[3]
				view.showMaximized()

		if resizer.views > 1 and resizer.refNeeded:
			if resizer.otherSubwin == None:
				resizer.getOtherSubwin()
				resizer.otherSubwin.removeEventFilter(resizer.subWindowFilterFloater)
				resizer.toggleAlwaysOnTop(resizer.otherSubwin, False)
		
		resizer.moveSubwindows()

	#each time when subwindow is opened
	def viewOpenedEvent(self, resizer):

		resizer.views = len(resizer.mdiArea.subWindowList())
		current = resizer.mdiArea.activeSubWindow()

		if resizer.activeSubwin != None: resizer.activeSubwin.setMinimumWidth(resizer.minimalColumnWidth) #temporarily here, until I find a better place for it
		if resizer.otherSubwin != None: resizer.otherSubwin.setMinimumWidth(resizer.minimalColumnWidth)

		#event catcher for every window, never removed 
		newSubwindow = resizer.mdiArea.subWindowList()[-1]
		newSubwindow.installEventFilter(resizer.subWindowFilterAll)

		if resizer.views == 1:
			resizer.getActiveSubwin()

		if current != None: #happens with psd, ora dropped?
			if resizer.views >= 2 and current.isMaximized():
				current.showNormal()

		if resizer.views == 2 and resizer.refNeeded: # open in split screen
			resizer.getOtherSubwin()
			resizer.otherSubwin.resize(int(resizer.defaultColumnRatio*resizer.mdiArea.width()), resizer.mdiArea.height()) #default width for ref subwindow

		if (resizer.views >= 3 and resizer.refNeeded) or (resizer.views >= 2 and (not resizer.refNeeded)): #open as floating window
			newSubwindow.installEventFilter(resizer.subWindowFilterFloater)
			resizer.toggleAlwaysOnTop(newSubwindow, True)
			newSubwindow.resize(resizer.defaultFloatingSize)

		resizer.moveSubwindows()

	#keep snapping to border when screen got bigger
	def moveFloatersOnAreaChange(self, resizer):
		
		for subwindow in resizer.mdiArea.subWindowList():
			if subwindow != resizer.activeSubwin and subwindow != resizer.otherSubwin:
				x = subwindow.pos().x()
				y = subwindow.pos().y()

				if x > resizer.mdiArea.width() - subwindow.width() - x: #closer to the right border of canvas than left one
					x += resizer.mdiArea.width() - self.sizeBefore[0]
				if y > resizer.mdiArea.height() - subwindow.height() - y: #closer to the right border of canvas than left one
					y += resizer.mdiArea.height() - self.sizeBefore[1]
				subwindow.move(x, y)

				resizer.snapToBorder(subwindow)

