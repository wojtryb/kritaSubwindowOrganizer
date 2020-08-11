from krita import *
from PyQt5.QtWidgets import QWidget, QToolButton, QMessageBox
from copy import copy
import sys
import sip

from .mdiAreaFilter import mdiAreaFilter
from .subWindowFilterBackground import subWindowFilterBackground
from .subWindowFilterFloater import subWindowFilterFloater
from .subWindowFilterAll import subWindowFilterAll

from .config import *


from PyQt5.QtGui import QGuiApplication



class resizer:
	#user customization

	def __init__(self, qwin, toggleAtStart):
		self.activeSubwin = None #main canvas for drawing
		self.otherSubwin = None #second main canvas for reference and overview
		self.refNeeded = False #extension mode: 'split screen'(False) and 'one window'(True) 

		self.qWin = qwin

		self.mdiArea = self.qWin.centralWidget().findChild(QMdiArea)
		self.views = len(self.mdiArea.subWindowList()) #0 on start - amount of opened subwindows
		self.refPosition = REFPOSITION

		if toggleAtStart: self.mdiAreaFilter = mdiAreaFilter(self) #cant be created on a start if the plugin should be off

		self.subWindowFilterBackground = subWindowFilterBackground(self) #installation on subwindows happens later
		self.subWindowFilterFloater = subWindowFilterFloater(self)
		self.subWindowFilterAll = subWindowFilterAll(self)

	def toggleAlwaysOnTop(self, subwindow, check):
		menu = subwindow.children()[0]
		if menu.actions()[5].isChecked() ^ check:
			menu.actions()[5].trigger()

		menu.actions()[5].setVisible(False)

	#snapping floaters to border of the canvas
	def snapToBorder(self, subwindow):
		x = subwindow.pos().x()
		y = subwindow.pos().y()

		if x < SNAPDISTANCE : x = 0
		if y < SNAPDISTANCE: y = 0
		if x + subwindow.width() > self.mdiArea.width() - SNAPDISTANCE:
			x = self.mdiArea.width() - subwindow.width()
		if y + subwindow.height() > self.mdiArea.height() - SNAPDISTANCE:
			y = self.mdiArea.height() - subwindow.height()

		subwindow.move(x, y)

	def getActiveSubwin(self):
		if self.views == 1: #subwindow is added to list before setting it to active window - have to make this if
			self.activeSubwin = self.mdiArea.subWindowList()[0]
		else:
			self.activeSubwin = self.mdiArea.activeSubWindow()
		if self.activeSubwin != None: #bugfix - when multiple windows are closed at once, it can get here with both views deleted
			self.activeSubwin.setMinimumWidth(MINIMALCOLUMNWIDTH)
			self.activeSubwin.installEventFilter(self.subWindowFilterBackground)
			self.toggleAlwaysOnTop(self.activeSubwin, False)

	def getOtherSubwin(self):
		for subwindow in self.mdiArea.subWindowList():
			if subwindow != self.activeSubwin:
				self.otherSubwin = subwindow
				break
		self.otherSubwin.setMinimumWidth(MINIMALCOLUMNWIDTH)
		self.columnWidth = self.otherSubwin.width()
		self.otherSubwin.installEventFilter(self.subWindowFilterBackground)
		self.toggleAlwaysOnTop(self.otherSubwin, False)

	#window react to change in workspace size or adjust to changed size of the other 
	def moveSubwindows(self, checkSizeChange = True):
		#user changed size of one window in background - other has to know the right amount of space left 
		def checkSizeChanges(resizer): 
			if resizer.mdiAreaFilter.sizeBefore[0] == resizer.mdiArea.width(): #fix to prevent ref window to change on workspace resize
				if resizer.otherSubwin.width() != resizer.columnWidth:
					resizer.columnWidth = resizer.otherSubwin.width()
				elif resizer.activeSubwin.width() != resizer.mdiArea.width() - resizer.columnWidth:
					resizer.columnWidth = resizer.mdiArea.width() - resizer.activeSubwin.width()

		current = self.mdiArea.activeSubWindow()
		if current != None: #weird situation with maximized background window
			if self.refNeeded and self.activeSubwin != None and self.otherSubwin != None and (not current.isMaximized()): #two split windows
				if checkSizeChange == True:
					checkSizeChanges(self)

				self.getBackgroundSizes()
				self.otherSubwin.move(self.otherPos)
				self.otherSubwin.resize(self.otherSize)
				self.activeSubwin.move(self.activePos)
				self.activeSubwin.resize(self.activeSize)

			if (not self.refNeeded) and self.activeSubwin != None: #one window on whole workspace
				self.activeSubwin.move(0,0)
				self.activeSubwin.resize(self.mdiArea.size())

	#counting the size for newly created view
	def resizeFloater(self, floater, pyFloater = None):
		if DEFAULTFLOATERSIZE != None: #none, means that no resizing will be done
			if pyFloater == None: #getting python object of the same qt subwindow, if not working, needs to be taken other way and passed as argument
				self.mdiArea.setActiveSubWindow(floater)
				pyFloater = Application.activeWindow().activeView().document()
				
			if type(DEFAULTFLOATERSIZE) == int: #area is given in pixels
				ratio = pyFloater.width()/pyFloater.height()
				width = int((DEFAULTFLOATERSIZE*ratio)**0.5)
				height = int(width/ratio)

			if type(DEFAULTFLOATERSIZE) == float: #area given as part of the whole workspace area
				allPixels = self.mdiArea.width() * self.mdiArea.height() 
				spaceToGet = allPixels * DEFAULTFLOATERSIZE

				ratio = pyFloater.width()/pyFloater.height()
				width = int((spaceToGet*ratio)**0.5)
				height = int(width/ratio)

			elif DEFAULTFLOATERSIZE[0] == 0: #height given, width to be calculated
				height = DEFAULTFLOATERSIZE[1]
				width = pyFloater.width()/pyFloater.height() * height

			elif DEFAULTFLOATERSIZE[1] == 0: #width given, height to be calculated
				width = DEFAULTFLOATERSIZE[0]
				height = pyFloater.height()/pyFloater.width() * width

			else: #fixed size given
				width = DEFAULTFLOATERSIZE[0]
				height = DEFAULTFLOATERSIZE[1]

			floater.resize(width, height + 25)

	#calculating position and size of both backgrouders
	def getBackgroundSizes(self):
		if self.refPosition == "left":
			self.otherPos = QPoint(0,0)
			self.otherSize = QSize(self.columnWidth, self.mdiArea.height())
			self.activePos = QPoint(self.columnWidth, 0)
			self.activeSize = QSize(int(self.mdiArea.width()-self.columnWidth), self.mdiArea.height())

		elif self.refPosition == "right":
			self.otherPos = QPoint(int(self.mdiArea.width()-self.columnWidth), 0)
			self.otherSize = QSize(self.columnWidth, self.mdiArea.height())
			self.activePos = QPoint(0,0)
			self.activeSize = QSize(int(self.mdiArea.width()-self.columnWidth), self.mdiArea.height())

	#switch into one window mode
	def userModeOneWindow(self):
		if self.otherSubwin != None: self.otherSubwin.showNormal() #bugfix: helps if user toggled overridden minimize button on main windows
		self.refNeeded = False

		if self.otherSubwin != None:
			self.otherSubwin.removeEventFilter(self.subWindowFilterBackground) #no longer one of the two main windows
			self.otherSubwin.installEventFilter(self.subWindowFilterFloater)
			
			self.otherSubwin.move(0,0)
			self.resizeFloater(self.otherSubwin, None)
			self.toggleAlwaysOnTop(self.otherSubwin, True) #turn on
			self.otherSubwin = None

	#switch into split mode
	def userModeSplit(self):
		self.refNeeded = True
		if self.views >= 2:
			current = self.mdiArea.activeSubWindow()
			if current != self.activeSubwin: #get a active floater to make it reference window
				if current.isMinimized(): current.showNormal() #dont work!!!
				self.otherSubwin = current
				self.otherSubwin.installEventFilter(self.subWindowFilterBackground)
			else: #select random floater to make it reference window
				self.getOtherSubwin()
			self.columnWidth = self.otherSubwin.width()
			self.otherSubwin.resize(int(DEFAULTCOLUMNRATIO*self.mdiArea.width()), self.mdiArea.height()) #default width for ref subwindow
			self.toggleAlwaysOnTop(self.otherSubwin, False)

	#turn off the whole plugin
	def userTurnOff(self):
		for subwindow in self.mdiArea.subWindowList(): #remove all filters from all windows
			subwindow.removeEventFilter(self.subWindowFilterAll)
			subwindow.removeEventFilter(self.subWindowFilterFloater)
			subwindow.removeEventFilter(self.subWindowFilterBackground)

			menu = subwindow.children()[0] #enable "always on top action"
			menu.actions()[5].setVisible(True)

		#enable default organizing actions
		if (action := Application.action('windows_cascade')) != None: action.setVisible(True)
		if (action := Application.action('windows_tile')) != None: action.setVisible(True)

		#disable plugin actions
		Application.action("openOverview").setVisible(False)
		Application.action("pickSubwindow").setVisible(False)

		self.activeSubwin = None
		self.otherSubwin = None

		self.userModeOneWindow()

		#filter on the workspace have to be removed that way
		if not sip.isdeleted(self.mdiAreaFilter): del self.mdiAreaFilter
			
	#turn on the whole plugin
	def userTurnOn(self):
		self.mdiAreaFilter = mdiAreaFilter(self)

		if (action := Application.action('windows_cascade')) != None: action.setVisible(False)
		if (action := Application.action('windows_tile')) != None: action.setVisible(False)

		self.views = len(self.mdiArea.subWindowList())

		if self.views >= 1:
			self.getActiveSubwin()
			Application.action("openOverview").setVisible(True)
		if self.views >= 2:
			Application.action("pickSubwindow").setVisible(True)

		for subwindow in self.mdiArea.subWindowList():
			subwindow.installEventFilter(self.subWindowFilterAll)
			menu = subwindow.children()[0]
			menu.actions()[5].setVisible(False)

			if subwindow.isMinimized(): #this makes sure all the windows are shown normal
				subwindow.showMaximized()
			if subwindow.isMaximized():
				subwindow.showNormal()

			if subwindow != self.activeSubwin:
				subwindow.installEventFilter(self.subWindowFilterFloater)
				self.toggleAlwaysOnTop(subwindow, True)
				self.resizeFloater(subwindow)

		if self.views >= 1:	
			self.moveSubwindows()

	def switchBackgroundWindows(self):
		self.otherSubwin.resize(self.activeSubwin.size())

		temp = self.otherSubwin
		self.otherSubwin = self.activeSubwin
		self.activeSubwin = temp

		self.mdiArea.setActiveSubWindow(self.activeSubwin)

	#opens grayscale overwiev
	def userOpenOverview(self):
		self.mdiArea.setActiveSubWindow(self.activeSubwin)
		doc = Application.activeDocument()
		Application.activeWindow().addView(doc)
		if SOFTPROOFING: Application.action("softProof").trigger()
		overview = self.mdiArea.subWindowList()[-1]
		overview.move(self.mdiArea.width() - overview.width(), self.mdiArea.height() - overview.height())

	def switchBackgroundAndFloater(self, background, floater):
		if floater.isMinimized(): floater.showNormal()
		floaterPos = copy(floater.pos()) #resize and move both
		floaterSize = copy(floater.size())

		floater.removeEventFilter(self.subWindowFilterFloater)
		floater.installEventFilter(self.subWindowFilterBackground)
		self.toggleAlwaysOnTop(floater, False)

		if background == self.activeSubwin: #the only way it works well
			floater.move(self.activeSubwin.pos())
			floater.resize(self.activeSubwin.size())
			temp = self.activeSubwin
			self.activeSubwin = floater

		else: #background == self.otherSubwin
			floater.move(self.otherSubwin.pos())
			floater.resize(self.otherSubwin.size())
			temp = self.otherSubwin
			self.otherSubwin = floater

		self.mdiArea.setActiveSubWindow(temp)

		temp.removeEventFilter(self.subWindowFilterBackground)
		temp.installEventFilter(self.subWindowFilterFloater)

		temp.resize(floaterSize)
		temp.move(floaterPos)
		self.toggleAlwaysOnTop(temp, True)

	#swapping subwindows with the keyboard/menu action instead of drag and drop
	def userToggleSubwindow(self):

		self.activeSubwin.showNormal() #those help if user toggled overridden minimize button on main windows
		if self.otherSubwin != None: self.otherSubwin.showNormal() 

		current = self.mdiArea.activeSubWindow()
		if self.refNeeded:
			#switch two main windows
			if (current == self.activeSubwin or current == self.otherSubwin) and self.otherSubwin != None:
				self.switchBackgroundWindows()

			#set floater as ref
			elif current != self.activeSubwin and current != self.otherSubwin:
				self.switchBackgroundAndFloater(self.otherSubwin, current)
		else: #one window mode
			if current != self.activeSubwin:
				self.switchBackgroundAndFloater(self.activeSubwin, current)

		self.moveSubwindows()
