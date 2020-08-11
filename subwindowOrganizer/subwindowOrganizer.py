from krita import *
from PyQt5.QtWidgets import QMessageBox

from .resizer import resizer


class SubwindowOrganizer(Extension):
	# organizerToggleChecked = False
	isToggled = False
	# splitScreenChecked = False #for toggle on setup
	kritaWindowsMode = False #true if subwindows are on
	#===============================#
	def __init__(self, parent):
		super(SubwindowOrganizer, self).__init__(parent)
		self.inProgress = False

	#switching between subwindows - user action
	def pickSubwindow(self):
		if not self.extension.subWindowFilterAll.isMaximized:
			self.extension.userToggleSubwindow()

	#opens grayscale overview
	def openOverview(self):
		self.extension.userOpenOverview()
	
	#toggles the whole plugin off and on
	def organizerToggle(self, toggled):
		Application.writeSetting("SubwindowOrganizer", "organizerToggled", str(toggled).lower())
		self.isToggled = toggled
		if self.kritaWindowsMode and self.isToggled:
			self.pickSubwindowAction.setVisible(True)
			self.openOverviewAction.setVisible(True)
			self.extension.userTurnOn()
		else:
			self.pickSubwindowAction.setVisible(False)
			self.openOverviewAction.setVisible(False)
			self.extension.userTurnOff()

	#reading values saved in krita settings and creating a notifier for settings changed event
	def setup(self):
		if Application.readSetting("SubwindowOrganizer", "organizerToggled", "true") == "true":
			self.isToggled = True
		if Application.readSetting("", "mdi_viewmode", "1") == "0":
			self.kritaWindowsMode = True

		self.settingsNotifier = Application.notifier()
		self.settingsNotifier.setActive(True)
		self.settingsNotifier.configurationChanged.connect(self.settingsChangedEvent)

	#happens when document mode (subwindow and tabs) is changed in settings by the user
	def settingsChangedEvent(self):
		if Application.readSetting("", "mdi_viewmode", "1") == "0": newMode = True
		else: newMode = False

		if self.kritaWindowsMode ^ newMode: #mode was changed in krita settings
			self.kritaWindowsMode = newMode
			if self.kritaWindowsMode: #changed from tabs to subwindows
				self.organizerToggleAction.setVisible(True) #addon now can be activated and deactivated
				if self.isToggled: #addon is on, so we can activate it
					self.extension.userTurnOn()
			else: #mode changed from subwindows to tab
				self.organizerToggleAction.setVisible(False)
				if self.isToggled: #addon was on
					self.extension.userTurnOff()
	
	#creates actions displayed in the view menu	
	def createActions(self, window):
		qwin = window.qwindow() 
		toggleAtStart = self.isToggled and self.kritaWindowsMode
		self.extension = resizer(qwin, toggleAtStart)

		self.organizerToggleAction = window.createAction("organizerToggle", "Toggle organizer", "view")
		self.organizerToggleAction.setCheckable(True)
		self.organizerToggleAction.setChecked(self.isToggled)
		self.organizerToggleAction.toggled.connect(self.organizerToggle)
		self.organizerToggleAction.setVisible(self.kritaWindowsMode)

		self.pickSubwindowAction = window.createAction("pickSubwindow", "Pick subwindow", "view")
		self.pickSubwindowAction.triggered.connect(self.pickSubwindow)
		self.pickSubwindowAction.setVisible(False)

		self.openOverviewAction = window.createAction("openOverview", "Open canvas overview", "view")
		self.openOverviewAction.triggered.connect(self.openOverview)
		self.openOverviewAction.setVisible(False)

Krita.instance().addExtension(SubwindowOrganizer(Krita.instance()))
