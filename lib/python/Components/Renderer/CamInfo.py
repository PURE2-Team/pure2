from Components.VariableText import VariableText
from enigma import eLabel
from Renderer import Renderer
from Tools.Directories import fileExists
import os

class CamInfo(Renderer, VariableText):
	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self)
		self.USERFILE = "/etc/clist.list"
	GUI_WIDGET = eLabel

	def changed(self, what):
		userLine = ""
		f = open("/etc/enigma2/pbsettings", "r")
		for line in f:
			if 'caminfo' in line:
				caminfodummy = line.strip().split("=")
				caminfo = caminfodummy[1]
		f.close()
		if caminfo == "0" and not self.suspended:
			userLine = "N/A"
			if fileExists(self.USERFILE):
				try:
					myuf = open("/etc/clist.list", "r")
					for line in myuf:
						userLine = line
					myuf.close()
				except:
					userLine = "No Cam"
			self.text = userLine
		else:
			userLine = ""

	def onShow(self):
		self.suspended = False
		self.changed(None)

	def onHide(self):
		self.suspended = True