from krita import *
from PyQt5.QtWidgets import QWidget, QToolButton, QMessageBox
from copy import copy
import sys
import sip

#event catcher for windows on back
class subWindowFilterBackground(QMdiSubWindow):
	def __init__(self, moveSubwindows, otherSubwin, parent=None):
		super().__init__(parent)
		self.moveSubwindows = moveSubwindows
		self.otherSubwin = otherSubwin
	def eventFilter(self, obj, e):
		if e.type() == QEvent.Resize:
			self.moveSubwindows()
		elif e.type() == QEvent.WindowStateChange:
			pass
			oldMinimized = False
			if int(e.oldState()) & int(Qt.WindowMinimized) != 0:
				oldMinimized = True
			if obj.isMinimized(): 
				obj.showNormal()
				return True
			if not obj.isMinimized() and oldMinimized:
				return True

		return False

#event catcher for floating windows
class subWindowFilterFloater(QMdiSubWindow):
	def __init__(self, snapToBorder, parent=None):
		super().__init__(parent)
		self.snapToBorder = snapToBorder
	def eventFilter(self, obj, e):
		if e.type() == QEvent.Move:
			self.snapToBorder(obj)

		return False

#event catcher for every window - both floaters and back ones
class subWindowFilterAll(QMdiSubWindow):
	def __init__(self, hideAllExcept, showAll, parent=None):
		super().__init__(parent)
		self.hide = hideAllExcept
		self.show = showAll

		self.isMaximized = False #is any window currently maximized
	def eventFilter(self, obj, e):
		#override krita minimize and maximize actions
		if e.type() == QEvent.WindowStateChange:
			oldMaximized = False
			if int(e.oldState()) & int(Qt.WindowMaximized) != 0:
				oldMaximized = True

			if obj.isMaximized() and not oldMaximized: #there was a change to maximized state
				self.hide(obj)
				self.isMaximized = True
			if not obj.isMaximized() and oldMaximized: #there was a change to normal from maximize
				self.show()
				self.isMaximized = False

		# krita will crush if there will be a maximized window in usual close handling - it has to be made normal before it
		if e.type() == QEvent.Close:
			obj.showNormal()
			self.show()
			self.isMaximized = False

		return False

#event catcher for the workspace - changes in size, and subwindows added and removed
class mdiAreaFilter(QMdiArea):
	def __init__(self, views, moveSubwindows, areaChanged, mdiArea, closeFun, openFun, parent=None):
		super().__init__(parent)
		self.moveSubwindows = moveSubwindows
		self.areaChanged = areaChanged
		self.views = views
		self.mdiArea = mdiArea

		self.closeFun = closeFun
		self.openFun = openFun

	def eventFilter(self, obj, e):
		if e.type() == QEvent.Resize:
			self.moveSubwindows()
			self.areaChanged()
		if not sip.isdeleted(self.mdiArea):
			#there are many more events, as subwindows aren't the only children, so the change have to be found as change in list size
			if e.type() == QEvent.ChildAdded:
				if self.views < len(self.mdiArea.subWindowList()):
					self.openFun()
					self.views = len(self.mdiArea.subWindowList())

			if e.type() == QEvent.ChildRemoved:
				if self.views > len(self.mdiArea.subWindowList()):
					self.closeFun()
					self.views = len(self.mdiArea.subWindowList())
		return False

class resizer:
	
	#user customization
	defaultColumnRatio = 0.33 #as part of the workspace width
	minimalColumnWidth = 100 #in pixels
	defaultFloatingSize = QSize(500,300) #size of newly created window

	def __init__(self, qwin):
		self.activeSubwin = None #main canvas for drawing
		self.otherSubwin = None #second main canvas for reference and overview
		self.refNeeded = False #extension mode: 'split screen'(False) and 'one window'(True) 

		self.qWin = qwin

		self.mdiArea = self.qWin.centralWidget().findChild(QMdiArea)
		self.views = len(self.mdiArea.subWindowList()) #0 on start - amount of opened subwindows

		self.mdiAreaFilter = mdiAreaFilter(self.views, self.moveSubwindows, self.areaChanged, self.mdiArea, self.viewClosedEvent, self.viewOpenedEvent)
		self.mdiArea.installEventFilter(self.mdiAreaFilter)

		self.subWindowFilterBackground = subWindowFilterBackground(self.moveSubwindows, self.otherSubwin) #installation on subwindows happens later
		self.subWindowFilterFloater = subWindowFilterFloater(self.snapToBorder)
		self.subWindowFilterAll = subWindowFilterAll(self.hideAllExcept, self.showAll)

	#hiding windows, when one gets maximized
	def hideAllExcept(self, exception):
		for subwindow in self.mdiArea.subWindowList():
			if subwindow != exception: subwindow.hide()
		if self.activeSubwin != None: self.activeSubwin.setMinimumWidth(0)
		if self.otherSubwin != None: self.otherSubwin.setMinimumWidth(0)

	#showind all hidden window, when maximized turns normal
	def showAll(self, exception = None):
		for subwindow in self.mdiArea.subWindowList():
			if subwindow != exception: subwindow.show()

	#each time when subwindow is closed
	def viewClosedEvent(self):
		def checkIfDeleted(obj):
			if obj in self.mdiArea.subWindowList():
				return obj
			else:
				return None

		self.views = len(self.mdiArea.subWindowList())

		self.activeSubwin = checkIfDeleted(self.activeSubwin)
		self.otherSubwin = checkIfDeleted(self.otherSubwin)

		#active was closed - make the reference take its place
		if self.activeSubwin == None and self.views >= 1: 
			if self.otherSubwin == None: #no ref window (non-split mode)
				self.getOtherSubwin()
				self.toggleAlwaysOnTop(self.otherSubwin, False)
			self.otherSubwin.resize(self.mdiArea.width() - self.columnWidth, self.mdiArea.height())
			self.otherSubwin.showNormal()
			self.activeSubwin = self.otherSubwin
			self.otherSubwin = None

		if self.views == 1:
			self.getActiveSubwin()
			if self.activeSubwin != None: #bugfix - when multiple windows are closed at once, it can get here with both views deleted
				view = self.activeSubwin.children()[3]
				view.showMaximized()

		if self.views > 1 and self.refNeeded:
			if self.otherSubwin == None:
				self.getOtherSubwin()
				self.otherSubwin.removeEventFilter(self.subWindowFilterFloater)
				self.toggleAlwaysOnTop(self.otherSubwin, False)
		
		self.moveSubwindows()

	#each time when subwindow is opened
	def viewOpenedEvent(self):
		self.views = len(self.mdiArea.subWindowList())

		if self.activeSubwin != None: self.activeSubwin.setMinimumWidth(self.minimalColumnWidth) #temporarily here, until I find a better place for it
		if self.otherSubwin != None: self.otherSubwin.setMinimumWidth(self.minimalColumnWidth)

		#event catcher for every window, never removed 
		newSubwindow = self.mdiArea.subWindowList()[-1]
		newSubwindow.installEventFilter(self.subWindowFilterAll)

		if self.views == 1:
			self.getActiveSubwin()

		if self.views >= 2:
			self.deMaximizeAll()

		if self.views == 2 and self.refNeeded: # open in split screen
			self.getOtherSubwin()
			self.otherSubwin.resize(int(self.defaultColumnRatio*self.mdiArea.width()), self.mdiArea.height()) #default width for ref subwindow
			self.areaChanged()#?

		if (self.views >= 3 and self.refNeeded) or (self.views >= 2 and (not self.refNeeded)): #open as floating window
			newSubwindow.installEventFilter(self.subWindowFilterFloater)
			self.toggleAlwaysOnTop(newSubwindow, True)
			newSubwindow.resize(self.defaultFloatingSize)

		self.moveSubwindows()

	def deMaximizeAll(self, exception = None):
		for subWindow in self.mdiArea.subWindowList():
			if subWindow != exception:
				subWindow.showNormal()

	def toggleAlwaysOnTop(self, subwindow, check):
		menu = subwindow.children()[0]
		if menu.actions()[5].isChecked() ^ check:
			menu.actions()[5].trigger()

	def snapToBorder(self, subwindow):
		x = subwindow.pos().x()
		y = subwindow.pos().y()

		if x < 0: x = 0
		if y < 0: y = 0
		if x + subwindow.width() > self.mdiArea.width():
			x = self.mdiArea.width() - subwindow.width()
		if y + subwindow.height() > self.mdiArea.height():
			y = self.mdiArea.height() - subwindow.height()

		subwindow.move(x, y)

	def getActiveSubwin(self):
		if self.views == 1: #subwindow is added to list before setting it to active window - have to make this if
			self.activeSubwin = self.mdiArea.subWindowList()[0]
		else:
			self.activeSubwin = self.mdiArea.activeSubWindow()
		if self.activeSubwin != None: #bugfix - when multiple windows are closed at once, it can get here with both views deleted
			self.activeSubwin.setMinimumWidth(self.minimalColumnWidth)
			self.activeSubwin.installEventFilter(self.subWindowFilterBackground)

	def getOtherSubwin(self):
		for subwindow in self.mdiArea.subWindowList():
			if subwindow != self.activeSubwin:
				self.otherSubwin = subwindow
				break
		self.otherSubwin.setMinimumWidth(self.minimalColumnWidth)
		self.columnWidth = self.otherSubwin.width()
		self.otherSubwin.installEventFilter(self.subWindowFilterBackground)

	#actialize the workspace width and snap all floaters to border
	def areaChanged(self):
		self.availableWidth = self.mdiArea.width()
		for subwindow in self.mdiArea.subWindowList():
			self.snapToBorder(subwindow)			

	#user changed size of one window in background - other has to know the right amount of space left 
	def checkSizeChanges(self):
		if self.availableWidth == self.mdiArea.width():
			if self.otherSubwin.width() != self.columnWidth:
				self.columnWidth = self.otherSubwin.width()
			elif self.activeSubwin.width() != self.mdiArea.width() - self.columnWidth:
				self.columnWidth = self.mdiArea.width() - self.activeSubwin.width()

	#window react to change in workspace size or adjust to changed size of the other 
	def moveSubwindows(self):
		if self.refNeeded and self.activeSubwin != None and self.otherSubwin != None: #two split windows
			self.checkSizeChanges()
			self.otherSubwin.move(0,0)
			self.otherSubwin.resize(self.columnWidth, self.mdiArea.height())
			self.activeSubwin.move(self.columnWidth, 0)
			self.activeSubwin.resize(int(self.mdiArea.width()-self.columnWidth), self.mdiArea.height())

		if (not self.refNeeded) and self.activeSubwin != None: #one window on whole workspace
			self.activeSubwin.move(0,0)
			self.activeSubwin.resize(self.mdiArea.size())

	#switch between 'split mode' and 'one window' mode
	def userToggleMode(self):

		#into 'one window' mode
		if self.refNeeded:
			if self.otherSubwin != None: self.otherSubwin.showNormal() #bugfix: helps if user toggled overridden minimize button on main windows
			self.refNeeded = False

			if self.otherSubwin != None:
				self.otherSubwin.removeEventFilter(self.subWindowFilterBackground) #no longer one of the two main windows
				self.otherSubwin.installEventFilter(self.subWindowFilterFloater)
				self.otherSubwin.move(0,0)
				self.otherSubwin.resize(self.defaultFloatingSize)
				self.toggleAlwaysOnTop(self.otherSubwin, True) #turn on
				self.otherSubwin = None

		#into 'split mode'
		else:
			self.refNeeded = True
			if self.views >= 2:
				current = self.mdiArea.activeSubWindow()
				if current != self.activeSubwin:
					self.otherSubwin = self.mdiArea.activeSubWindow()
				else:
					self.getOtherSubwin()
				self.columnWidth = self.otherSubwin.width()
				self.otherSubwin.resize(int(self.defaultColumnRatio*self.mdiArea.width()), self.mdiArea.height()) #default width for ref subwindow
				self.toggleAlwaysOnTop(self.otherSubwin, False) #turn off

	def userToggleSubwindow(self):

		# current = None
		# for subwindow in self.mdiArea.subWindowList():
		# 	if subwindow.underMouse():
		# 		current = subwindow
		# if current == None: current = self.mdiArea.activeSubWindow()
		

		self.activeSubwin.showNormal() #those help if user toggled overridden minimize button on main windows
		if self.otherSubwin != None: self.otherSubwin.showNormal() 

		current = self.mdiArea.activeSubWindow()
		if self.refNeeded:
			#switch two main windows
			if (current == self.activeSubwin or current == self.otherSubwin) and self.otherSubwin != None:
				temp = self.otherSubwin
				self.otherSubwin = self.activeSubwin
				self.activeSubwin = temp

				self.mdiArea.setActiveSubWindow(self.activeSubwin)

				self.columnWidth = self.otherSubwin.width()
				self.otherSubwin.resize(int(self.defaultColumnRatio*self.mdiArea.width()), self.mdiArea.height())

			#set floater as ref
			elif current != self.activeSubwin and current != self.otherSubwin:
				floaterPos = copy(current.pos()) #resize and move both
				floaterSize = copy(current.size())

				current.removeEventFilter(self.subWindowFilterFloater)
				current.installEventFilter(self.subWindowFilterBackground)
				current.move(self.otherSubwin.pos())
				current.resize(self.otherSubwin.size())
				self.toggleAlwaysOnTop(current, False)

				temp = self.otherSubwin
				self.otherSubwin = current

				self.mdiArea.setActiveSubWindow(temp)

				temp.removeEventFilter(self.subWindowFilterBackground)
				temp.resize(floaterSize)
				temp.move(floaterPos)
				temp.installEventFilter(self.subWindowFilterFloater)
				self.toggleAlwaysOnTop(temp, True)
		else: #one window mode
			if current != self.activeSubwin:
				#its the same code as above, but it just don't work when made into function...
				floaterPos = copy(current.pos()) #resize and move both
				floaterSize = copy(current.size())

				current.removeEventFilter(self.subWindowFilterFloater)
				current.installEventFilter(self.subWindowFilterBackground)
				current.move(self.activeSubwin.pos())
				current.resize(self.activeSubwin.size())
				self.toggleAlwaysOnTop(current, False)

				temp = self.activeSubwin
				self.activeSubwin = current

				self.mdiArea.setActiveSubWindow(temp)

				temp.removeEventFilter(self.subWindowFilterBackground)
				temp.resize(floaterSize)
				temp.move(floaterPos)
				temp.installEventFilter(self.subWindowFilterFloater)
				self.toggleAlwaysOnTop(temp, True)

		self.moveSubwindows()

class SubwindowOrganizer(Extension):
	splitScreenChecked = False #for toggle on setup
	#===============================#
	def __init__(self, parent):
		super(SubwindowOrganizer, self).__init__(parent)

	#switching between subwindows - user action
	def pickSubwindow(self):
		if not self.extension.subWindowFilterAll.isMaximized:
			self.extension.userToggleSubwindow()

	#toggle mode - user action
	def splitScreen(self):
		self.extension.userToggleMode()

	def setup(self):
		if Application.readSetting("SubwindowOrganizer", "splitScreen", "true") == "true":
			self.splitScreenChecked = True

	def splitScreenSetup(self, toggled):
		Application.writeSetting("SubwindowOrganizer", "splitScreen", str(toggled).lower())
		self.splitScreen = toggled
		
	def createActions(self, window):
		if Application.readSetting("", "mdi_viewmode", "1") == "0":
			qwin = window.qwindow() 
			self.extension = resizer(qwin)

			pickSubwindow = window.createAction("pickSubwindow", "Pick subwindow", "view")
			pickSubwindow.triggered.connect(self.pickSubwindow)

			#split screen actions
			action = window.createAction("splitScreenSetup", "", "")
			action.setCheckable(True)
			action.setChecked(self.splitScreenChecked) 

			action = window.createAction("splitScreen", "Split screen", "view")
			action.toggled.connect(self.splitScreen)
			action.setCheckable(True)
			action.setChecked(self.splitScreenChecked)
			action.toggled.connect(self.splitScreenSetup)
		else:
			msg = QMessageBox()
			msg.setText("Subwindow organizer plugin requires the multiple document mode to be set to 'subwindows', not 'tabs'. \n\n" +
						"This setting can be found at Settings -> Configure Krita... -> General -> Window -> Multiple Document Mode. " +
						"Once the setting has been changed, please restart Krita. Thank you for trying out my plugin.")
			msg.exec_()

Krita.instance().addExtension(SubwindowOrganizer(Krita.instance()))
