from krita import *
from PyQt5.QtWidgets import QMessageBox

from .resizer import resizer

class SubwindowOrganizer(Extension):
	organizerToggleChecked = False
	isToggled = False
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
		# print("split wait")
		# if self.isToggled:
		# print("split done")
		self.extension.userToggleMode()
		print("split")

	def openOverview(self):
		self.extension.userOpenOverview()
	
	def organizerToggle(self):
		if self.isToggled:
			self.extension.userTurnOn()
			# self.isToggled = True
			print("======")
			print("on")
		else:
			self.extension.userTurnOff()
			# self.isToggled = False
			print("======")
			print("off")

	# def turnOff(self):
	# 	self.extension.userTurnOff()

	# def turnOn(self):
	# 	self.extension.userTurnOn()		

	def setup(self):
		if Application.readSetting("SubwindowOrganizer", "organizerToggled", "true") == "true":
			self.isToggled = True
			# self.organizerToggleChecked = True
		if Application.readSetting("SubwindowOrganizer", "splitScreen", "true") == "true":
			self.splitScreenChecked = True

	def organizerToggleSetup(self, toggled):
		Application.writeSetting("SubwindowOrganizer", "organizerToggled", str(toggled).lower())
		self.isToggled = toggled

	def splitScreenSetup(self, toggled):
		Application.writeSetting("SubwindowOrganizer", "splitScreen", str(toggled).lower())
		self.splitScreen = toggled

	def createActions(self, window):
		if Application.readSetting("", "mdi_viewmode", "1") == "0":
			qwin = window.qwindow() 
			self.extension = resizer(qwin, self.isToggled)

			pickSubwindow = window.createAction("pickSubwindow", "Pick subwindow", "view")
			pickSubwindow.triggered.connect(self.pickSubwindow)

			openOverview = window.createAction("openOverview", "Open canvas overview", "view")
			openOverview.triggered.connect(self.openOverview)

			action = window.createAction("organizerToggle", "Toggle organizer", "view")
			action.toggled.connect(self.organizerToggleSetup)
			action.setCheckable(True)
			action.setChecked(self.isToggled)
			action.toggled.connect(self.organizerToggle)

			# turnOff = window.createAction("turnOff", "turnOff", "view")
			# turnOff.triggered.connect(self.turnOff)

			# turnOn = window.createAction("turnOn", "turnOn", "view")
			# turnOn.triggered.connect(self.turnOn)

			#split screen actions
			action = window.createAction("splitScreenSetup", "", "")
			action.setCheckable(True)
			action.setChecked(self.splitScreenChecked) 

			action = window.createAction("splitScreen", "Split screen", "view")
			action.toggled.connect(self.splitScreen)
			action.setCheckable(True)
			action.setChecked(self.splitScreenChecked)
			action.toggled.connect(self.splitScreenSetup)


			# Application.action('windows_cascade').setDisabled(True)

		else:
			msg = QMessageBox()
			msg.setText("Subwindow organizer plugin requires the multiple document mode to be set to 'subwindows', not 'tabs'. \n\n" +
						"This setting can be found at Settings -> Configure Krita... -> General -> Window -> Multiple Document Mode. " +
						"Once the setting has been changed, please restart Krita. Thank you for trying out my plugin.")
			msg.exec_()

Krita.instance().addExtension(SubwindowOrganizer(Krita.instance()))
