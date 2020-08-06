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

class resizer:
	#user customization

	def __init__(self, qwin):
		self.activeSubwin = None #main canvas for drawing
		self.otherSubwin = None #second main canvas for reference and overview
		self.refNeeded = False #extension mode: 'split screen'(False) and 'one window'(True) 

		self.qWin = qwin

		self.mdiArea = self.qWin.centralWidget().findChild(QMdiArea)
		self.views = len(self.mdiArea.subWindowList()) #0 on start - amount of opened subwindows

		self.mdiAreaFilter = mdiAreaFilter(self)
		self.mdiArea.installEventFilter(self.mdiAreaFilter)

		self.subWindowFilterBackground = subWindowFilterBackground(self) #installation on subwindows happens later
		self.subWindowFilterFloater = subWindowFilterFloater(self)
		self.subWindowFilterAll = subWindowFilterAll(self)

	def toggleAlwaysOnTop(self, subwindow, check):
		menu = subwindow.children()[0]
		if menu.actions()[5].isChecked() ^ check:
			menu.actions()[5].trigger()

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

	def getOtherSubwin(self):
		for subwindow in self.mdiArea.subWindowList():
			if subwindow != self.activeSubwin:
				self.otherSubwin = subwindow
				break
		self.otherSubwin.setMinimumWidth(MINIMALCOLUMNWIDTH)
		self.getRefSize()
		self.otherSubwin.installEventFilter(self.subWindowFilterBackground)

	def getRefSize(self, usual = True):
		if usual:
			if REFPOSITION in ["left", "right"]: self.columnWidth = self.otherSubwin.width()
			else: self.columnWidth = self.otherSubwin.height()
		else:
			if REFPOSITION in ["left", "right"]: self.columnWidth = self.otherSubwin.width() - self.activeSubwin.width()
			else: self.columnWidth = self.otherSubwin.height() - self.activeSubwin.height()

	#window react to change in workspace size or adjust to changed size of the other 
	def moveSubwindows(self, checkSizeChange = True):
		#user changed size of one window in background - other has to know the right amount of space left 
		def checkSizeChanges(resizer): 
			if REFPOSITION in ["left", "right"]:
				if resizer.mdiAreaFilter.sizeBefore[0] == resizer.mdiArea.width(): #fix to prevent ref window to change on workspace resize
					if resizer.otherSubwin.width() != resizer.columnWidth:
						self.getRefSize()
					elif resizer.activeSubwin.width() != resizer.mdiArea.width() - resizer.columnWidth:
						self.getRefSize(False)
			else:
				if resizer.mdiAreaFilter.sizeBefore[1] == resizer.mdiArea.height(): #fix to prevent ref window to change on workspace resize
					if resizer.otherSubwin.height() != resizer.columnWidth:
						self.getRefSize()
					elif resizer.activeSubwin.height() != resizer.mdiArea.height() - resizer.columnWidth:
						self.getRefSize(False)

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


	def getBackgroundSizes(self):
		if REFPOSITION == "left":
			self.otherPos = QPoint(0,0)
			self.otherSize = QSize(self.columnWidth, self.mdiArea.height())
			self.activePos = QPoint(self.columnWidth, 0)
			self.activeSize = QSize(int(self.mdiArea.width()-self.columnWidth), self.mdiArea.height())

		elif REFPOSITION == "right":
			self.otherPos = QPoint(int(self.mdiArea.width()-self.columnWidth), 0)
			self.otherSize = QSize(self.columnWidth, self.mdiArea.height())
			self.activePos = QPoint(0,0)
			self.activeSize = QSize(int(self.mdiArea.width()-self.columnWidth), self.mdiArea.height())

		elif REFPOSITION == "top":
			self.otherPos = QPoint(0,0)
			self.otherSize = QSize(self.mdiArea.width(), self.columnWidth)
			self.activePos = QPoint(0, self.columnWidth)
			self.activeSize = QSize(self.mdiArea.width(), int(self.mdiArea.height()-self.columnWidth))

		elif REFPOSITION == "bottom":
			self.otherPos = QPoint(0, int(self.mdiArea.width()-self.columnWidth))
			self.otherSize = QSize(self.mdiArea.width(), self.columnWidth)
			self.activePos = QPoint(0,0)
			self.activeSize = QSize(self.mdiArea.width(), int(self.mdiArea.height()-self.columnWidth))

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
				self.otherSubwin.resize(DEFAULTFLOATERSIZE)
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
				self.getRefSize()
				self.otherSubwin.resize(int(DEFAULTCOLUMNRATIO*self.mdiArea.width()), self.mdiArea.height()) #default width for ref subwindow
				self.toggleAlwaysOnTop(self.otherSubwin, False) #turn off

	def switchBackgroundWindows(self):
		temp = self.otherSubwin
		self.otherSubwin = self.activeSubwin
		self.activeSubwin = temp

		self.mdiArea.setActiveSubWindow(self.activeSubwin)
		self.getRefSize()
		self.otherSubwin.resize(int(DEFAULTCOLUMNRATIO*self.mdiArea.width()), self.mdiArea.height())

	def switchBackgroundAndFloater(self, background, floater):
		floaterPos = copy(floater.pos()) #resize and move both
		floaterSize = copy(floater.size())

		floater.removeEventFilter(self.subWindowFilterFloater)
		floater.installEventFilter(self.subWindowFilterBackground)
		self.toggleAlwaysOnTop(floater, False)
		print("shouldBeNow")

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
		print(floaterPos, floaterSize)
		temp.resize(floaterSize)
		temp.move(floaterPos)
		self.toggleAlwaysOnTop(temp, True)

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
				self.switchBackgroundWindows()

			#set floater as ref
			elif current != self.activeSubwin and current != self.otherSubwin:
				self.switchBackgroundAndFloater(self.otherSubwin, current)
		else: #one window mode
			if current != self.activeSubwin:
				self.switchBackgroundAndFloater(self.activeSubwin, current)

		self.moveSubwindows()
