from krita import *
import sip
 
from .config import *

#event catcher for the workspace - changes in size, and subwindows added and removed
class mdiAreaFilter(QMdiArea):
	def __init__(self, resizer, parent=None):
		super().__init__(parent)
		self.resizer = resizer
		self.sizeBefore = [resizer.mdiArea.width(), resizer.mdiArea.height()]

	def eventFilter(self, obj, e):
		if not sip.isdeleted(self.resizer.mdiArea):
			if e.type() == QEvent.Resize:
				if Application.readSetting("", "mdi_viewmode", "1") == "0":
					self.resizer.moveSubwindows()
					self.moveFloatersOnAreaChange(self.resizer) #move floaters
					self.resizeFloatersOnAreaChange()
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

		if resizer.activeSubwin == None: #active was closed, other is the new active (only in split mode, in one window, there is no other)
			resizer.activeSubwin = resizer.otherSubwin
			resizer.otherSubwin = None

		if resizer.otherSubwin == None: #other was closed, or was transformed into active
			if resizer.refNeeded: # split mode
				resizer.userModeOneWindow()

		if resizer.activeSubwin == None: # at first it was one window mode, active was closed, and nothing took its place
			resizer.getActiveSubwin()
			if resizer.activeSubwin != None and resizer.activeSubwin.isMinimized(): # closing everything at once, can cause it
				resizer.activeSubwin.showMaximized() #workaround - minimized windows have problems with getting normal, so I maximize them first
				resizer.activeSubwin.showNormal()

		if resizer.views == 1:
			resizer.activeSubwin.showMaximized() #one view is always maximized
			Application.action("pickSubwindow").setVisible(False)

		if resizer.views == 0:
			Application.action("openOverview").setVisible(False)

		resizer.moveSubwindows() #update changes

	#each time when subwindow is opened
	def viewOpenedEvent(self, resizer):

		Application.action('windows_cascade').setVisible(False)
		Application.action('windows_tile').setVisible(False)

		resizer.views = len(resizer.mdiArea.subWindowList())
		current = resizer.mdiArea.activeSubWindow()

		#event catcher for every window, never removed 
		newSubwindow = resizer.mdiArea.subWindowList()[-1]
		newSubwindow.installEventFilter(resizer.subWindowFilterAll)

		menu = newSubwindow.children()[0] #when the addon is enabled, user cant toggle "always on top" action
		menu.actions()[5].setVisible(False)

		if resizer.views == 1:
			resizer.getActiveSubwin()
			Application.action("openOverview").setVisible(True)

		if resizer.views == 2:
			Application.action("pickSubwindow").setVisible(True)

		maximizedList = [sub.isMaximized() for sub in resizer.mdiArea.subWindowList()] 
		if resizer.views >= 2 and any(maximizedList): #if something was maximized, demaximize it
			resizer.mdiArea.subWindowList()[maximizedList.index(True)].showNormal()
			
		if resizer.views == 2 and SPLITBYDEFAULT: # open new in split screen
			self.resizer.userModeSplit()
			resizer.getOtherSubwin()
			resizer.otherSubwin.resize(int(DEFAULTCOLUMNRATIO*resizer.mdiArea.width()), resizer.mdiArea.height()) #default width for ref subwindow

		if (resizer.views >= 3 and resizer.refNeeded) or (resizer.views >= 2 and (not resizer.refNeeded)): #open as floating window
			newSubwindow.installEventFilter(resizer.subWindowFilterFloater)
			resizer.toggleAlwaysOnTop(newSubwindow, True)
			pyNewSubwindow = Application.views()[-1].document()
			self.resizer.resizeFloater(newSubwindow, pyNewSubwindow)

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

	#when krita window gets very small, floaters shouldn't be bigger than it
	def resizeFloatersOnAreaChange(self):
		for subwindow in self.resizer.mdiArea.subWindowList():
			if subwindow != self.resizer.activeSubwin and subwindow != self.resizer.otherSubwin:

				w = min(subwindow.width(), self.resizer.mdiArea.width())
				h = min(subwindow.height(), self.resizer.mdiArea.height()) 

				subwindow.resize(w, h)