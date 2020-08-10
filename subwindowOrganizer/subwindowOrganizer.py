from krita import *
from PyQt5.QtWidgets import QMessageBox

from .resizer import resizer


class kritaWindow(QObject):
	def __init__(self, parent=None):
		super().__init__(parent)
	def eventFilter(self, obj, e):
		if e.type() == QEvent.WindowBlocked:
			print("block")
		elif e.type() == QEvent.WindowUnblocked:
			print("unblock")
		return False

class SubwindowOrganizer(Extension):
	# organizerToggleChecked = False
	isToggled = False
	splitScreenChecked = False #for toggle on setup
	kritaWindowsMode = False #true if subwindows are on
	#===============================#
	def __init__(self, parent):
		super(SubwindowOrganizer, self).__init__(parent)
		self.inProgress = False

	#switching between subwindows - user action
	def pickSubwindow(self):
		if not self.extension.subWindowFilterAll.isMaximized:
			self.extension.userToggleSubwindow()

	#toggle mode - user action
	def splitScreen(self, toggled):
		Application.writeSetting("SubwindowOrganizer", "splitScreen", str(toggled).lower())
		self.splitScreen = toggled

		if self.extension.refNeeded:
			self.extension.userModeOneWindow()
		else:
			self.extension.userModeSplit()

	def openOverview(self):
		self.extension.userOpenOverview()
	
	def organizerToggle(self, toggled):
		Application.writeSetting("SubwindowOrganizer", "organizerToggled", str(toggled).lower())
		self.isToggled = toggled
		if self.kritaWindowsMode and self.isToggled:
			self.splitScreenToggleAction.setVisible(True)
			self.pickSubwindowAction.setVisible(True)
			self.openOverviewAction.setVisible(True)
			self.extension.userTurnOn()
		else:
			self.splitScreenToggleAction.setVisible(False)
			self.pickSubwindowAction.setVisible(False)
			self.openOverviewAction.setVisible(False)
			self.extension.userTurnOff()
	
	def setup(self):
		if Application.readSetting("SubwindowOrganizer", "organizerToggled", "true") == "true":
			self.isToggled = True
		if Application.readSetting("SubwindowOrganizer", "splitScreen", "true") == "true":
			self.splitScreenChecked = True
		if Application.readSetting("", "mdi_viewmode", "1") == "0":
			self.kritaWindowsMode = True

		self.settingsNotifier = Application.notifier()
		self.settingsNotifier.setActive(True)
		self.settingsNotifier.configurationChanged.connect(self.settingsChangedEvent)



	# def settingsOpenedEvent(self):
	# 	print("settings opened")

	def settingsChangedEvent(self):
		print("settings closed")
		if Application.readSetting("", "mdi_viewmode", "1") == "0": newMode = True
		else: newMode = False

		# if not self.inProgress:
		if self.kritaWindowsMode ^ newMode: #mode was changed in krita settings
			self.kritaWindowsMode = newMode
			if self.kritaWindowsMode: #changed from tabs to subwindows
				self.organizerToggleAction.setVisible(True) #addon now can be activated and deactivated
				if self.isToggled: #addon is on, so we can activate it
					self.splitScreenToggleAction.setVisible(True)
					self.pickSubwindowAction.setVisible(True)
					self.openOverviewAction.setVisible(True)
					self.extension.userTurnOn()
			else: #mode changed from subwindows to tab
				self.organizerToggleAction.setVisible(False)
				if self.isToggled: #addon was on
					# print("TOGGLIGN")
					Application.writeSetting("", "mdi_viewmode", "0")
					self.kritaWindowsMode = True
					self.organizerToggleAction.setVisible(True)
					# self.extension.userTurnOff()
					# self.pickSubwindowAction.setVisible(False)
					# self.openOverviewAction.setVisible(False)
					# self.splitScreenToggleAction.setVisible(False)
					# self.organizerToggleAction.setVisible(False)
					# self.extension.fixTabs()
					# Application.writeSetting("", "mdi_viewmode", "1")


	def createActions(self, window):
		qwin = window.qwindow() 
		toggleAtStart = self.isToggled and self.kritaWindowsMode
		self.extension = resizer(qwin, toggleAtStart)

		self.organizerToggleAction = window.createAction("organizerToggle", "Toggle organizer", "view")
		self.organizerToggleAction.setCheckable(True)
		self.organizerToggleAction.setChecked(self.isToggled)
		self.organizerToggleAction.toggled.connect(self.organizerToggle)
		self.organizerToggleAction.setVisible(self.kritaWindowsMode)

		self.splitScreenToggleAction = window.createAction("splitScreen", "Split screen", "view")
		self.splitScreenToggleAction.setCheckable(True)
		self.splitScreenToggleAction.setChecked(self.splitScreenChecked)
		self.splitScreenToggleAction.toggled.connect(self.splitScreen)
		self.splitScreenToggleAction.setVisible(toggleAtStart)

		self.pickSubwindowAction = window.createAction("pickSubwindow", "Pick subwindow", "view")
		self.pickSubwindowAction.triggered.connect(self.pickSubwindow)
		self.pickSubwindowAction.setVisible(toggleAtStart)

		self.openOverviewAction = window.createAction("openOverview", "Open canvas overview", "view")
		self.openOverviewAction.triggered.connect(self.openOverview)
		self.openOverviewAction.setVisible(toggleAtStart)

		self.kritaFilter = kritaWindow()
		window.qwindow().installEventFilter(self.kritaFilter)
		# window.qwindow().menuBar().

Krita.instance().addExtension(SubwindowOrganizer(Krita.instance()))
