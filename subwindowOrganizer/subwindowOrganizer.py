from krita import *
from PyQt5.QtWidgets import QMessageBox

from .resizer import resizer

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
