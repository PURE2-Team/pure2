from Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.config import config
from Components.Sources.StaticText import StaticText
from Components.Harddisk import harddiskmanager
from Components.NimManager import nimmanager
from Components.About import about
from Components.ScrollLabel import ScrollLabel
from Components.Button import Button
from Components.Console import Console
from enigma import eTimer, getEnigmaVersionString, eLabel, eConsoleAppContainer
from boxbranding import getBoxType, getMachineBuild, getMachineBrand, getMachineName, getImageVersion, getImageBuild, getDriverDate

from Components.Pixmap import MultiPixmap
from Components.Network import iNetwork

from Tools.StbHardware import getFPVersion


from os import path
from re import search
import skin, os

class About(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)

		AboutText = _("Hardware:\t\t%s %s\n") % (getMachineBrand(), getMachineName())
		
		bootloader = ""
		if path.exists('/sys/firmware/devicetree/base/bolt/tag'):
			f = open('/sys/firmware/devicetree/base/bolt/tag', 'r')
			bootloader = f.readline().replace('\x00', '').replace('\n', '')
			f.close()
			AboutText += _("Bootloader:\t\t%s\n") % (bootloader)
		
		if path.exists('/proc/stb/info/chipset'):
			AboutText += _("Chipset:\t\t%s") % about.getChipSetString() + "\n"
		cpuMHz = ""
		if getMachineBuild() in ('vusolo4k','vuultimo4k','vuzero4k'):
			cpuMHz = "   (1,5 GHz)"
		elif getMachineBuild() in ('formuler1tc','formuler1', 'triplex', 'tiviaraplus'):
			cpuMHz = "   (1,3 GHz)"
		elif getMachineBuild() in ('u5','u5pvr','h9'):
			cpuMHz = "   (1,6 GHz)"
		elif getMachineBuild() in ('vuuno4kse','vuuno4k','dm900','dm920', 'gb7252', 'dags7252','xc7439','8100s'):
			cpuMHz = "   (1,7 GHz)"
		elif getMachineBuild() in ('hd51','hd52','sf4008','vs1500','et1x000','h7','et13000'):
			try:
				import binascii
				f = open('/sys/firmware/devicetree/base/cpus/cpu@0/clock-frequency', 'rb')
				clockfrequency = f.read()
				f.close()
				cpuMHz = "   (%s MHz)" % str(round(int(binascii.hexlify(clockfrequency), 16)/1000000,1))
			except:
				cpuMHz = "   (1,7 GHz)"
		else:
			if path.exists('/proc/cpuinfo'):
				f = open('/proc/cpuinfo', 'r')
				temp = f.readlines()
				f.close()
				try:
					for lines in temp:
						lisp = lines.split(': ')
						if lisp[0].startswith('cpu MHz'):
							cpuMHz = "   (" +  str(int(float(lisp[1].replace('\n', '')))) + " MHz)"
							break
				except:
					pass

		AboutText += _("CPU:\t\t%s") % about.getCPUString() + cpuMHz + "\n"
		AboutText += _("Cores:\t\t%s") % about.getCpuCoresString() + "\n"

		tempinfo = ""
		if path.exists('/proc/stb/sensors/temp0/value'):
			f = open('/proc/stb/sensors/temp0/value', 'r')
			tempinfo = f.read()
			f.close()
		elif path.exists('/proc/stb/fp/temp_sensor'):
			f = open('/proc/stb/fp/temp_sensor', 'r')
			tempinfo = f.read()
			f.close()
		elif path.exists('/proc/stb/sensors/temp/value'):
			f = open('/proc/stb/sensors/temp/value', 'r')
			tempinfo = f.read()
			f.close()
		if tempinfo and int(tempinfo.replace('\n', '')) > 0:
			mark = str('\xc2\xb0')
			AboutText += _("System temperature:\t%s") % tempinfo.replace('\n', '').replace(' ','') + mark + "C\n"

		tempinfo = ""
		if path.exists('/proc/stb/fp/temp_sensor_avs'):
			f = open('/proc/stb/fp/temp_sensor_avs', 'r')
			tempinfo = f.read()
			f.close()
		elif path.exists('/sys/devices/virtual/thermal/thermal_zone0/temp'):
			try:
				f = open('/sys/devices/virtual/thermal/thermal_zone0/temp', 'r')
				tempinfo = f.read()
				tempinfo = tempinfo[:-4]
				f.close()
			except:
				tempinfo = ""
		if tempinfo and int(tempinfo.replace('\n', '')) > 0:
			mark = str('\xc2\xb0')
			AboutText += _("Processor temperature:\t%s") % tempinfo.replace('\n', '').replace(' ','') + mark + "C\n"

		imagestarted = ""
		bootname = ''
		if path.exists('/boot/bootname'):
			f = open('/boot/bootname', 'r')
			bootname = f.readline().split('=')[1]
			f.close()

		if path.exists('/boot/STARTUP'):
			f = open('/boot/STARTUP', 'r')
			f.seek(22)
			image = f.read(1) 
			f.close()
			if bootname: bootname = "   (%s)" %bootname 
			AboutText += _("Selected Image:\t\t%s") % "STARTUP_" + image + bootname + "\n"

		elif path.exists('/boot/cmdline.txt'):
			f = open('/boot/cmdline.txt', 'r')
			f.seek(38)
			image = f.read(1) 
			f.close()
			if bootname: bootname = "   (%s)" %bootname 
			AboutText += _("Selected Image:\t%s") % "STARTUP_" + image + bootname + "\n"

		AboutText += _("Image:\t\t") + about.getImageTypeString() + "\n"

		if getMachineBuild() not in ('h9','vuzero4k','sf5008','et13000','et1x000','hd51','hd52','vusolo4k','vuuno4k','vuuno4kse','vuultimo4k','sf4008','dm820','dm7080','dm900','dm920', 'gb7252', 'dags7252', 'vs1500','h7','xc7439','8100s','u5','u5pvr'):
			AboutText += _("Installed:\t\t%s") % about.getFlashDateString() + "\n"
		AboutText += _("Kernel:\t\t") + about.getKernelVersionString() + "\n"

		AboutText += _("Drivers:\t\t") + self.realDriverDate() + "\n"

		ImageVersion = _("Last upgrade:\t\t") + about.getImageVersionString()
		self["ImageVersion"] = StaticText(ImageVersion)
		AboutText += ImageVersion + "\n"
		AboutText += _("GStreamer:\t\t%s") % about.getGStreamerVersionString() + "\n"
		AboutText += _("Python version:\t\t") + about.getPythonVersionString() + "\n"
		AboutText += _("Network:\t")
		for x in about.GetIPsFromNetworkInterfaces():
			AboutText += "\t" + x[0] + ": " + x[1] + "\n"


		self["TunerHeader"] = StaticText(_("Detected NIMs:"))
		AboutText += "\n" + _("Detected NIMs:") + "\n"

		nims = nimmanager.nimList()
		for count in range(len(nims)):
			if count < 4:
				self["Tuner" + str(count)] = StaticText(nims[count])
			else:
				self["Tuner" + str(count)] = StaticText("")
			AboutText += nims[count] + "\n"

		self["HDDHeader"] = StaticText(_("Detected HDD:"))
		AboutText += "\n" + _("Detected HDD:") + "\n"

		hddlist = harddiskmanager.HDDList()
		hddinfo = ""
		if hddlist:
			for count in range(len(hddlist)):
				if hddinfo:
					hddinfo += "\n"
				hdd = hddlist[count][1]
				if int(hdd.free()) > 1024:
					hddinfo += "%s\n(%s, %d GB %s)" % (hdd.model(), hdd.capacity(), hdd.free()/1024, _("free"))
				else:
					hddinfo += "%s\n(%s, %d MB %s)" % (hdd.model(), hdd.capacity(), hdd.free(), _("free"))
		else:
			hddinfo = _("none")
		self["hddA"] = StaticText(hddinfo)
		AboutText += hddinfo

		self["AboutScrollLabel"] = ScrollLabel(AboutText)
		self["key_green"] = Button(_("Changelog"))
		self['key_red'] = Button(_('Close'))
		self["key_yellow"] = Button(_("Troubleshoot"))
		self['key_blue'] = Button(_('Team Info'))
		self["actions"] = ActionMap(["ColorActions", "SetupActions", "DirectionActions"],
			{
				"cancel": self.close,
				"ok": self.close,
				'red': self.close,
				"green": self.showChangelogInfo,
				"yellow": self.showTroubleshoot,
				"blue": self.showTeamInfo,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown
			})
	def realDriverDate(self):
		realdate = about.getDriverInstalledDate()
		try:
			y = popen('lsmod').read().strip()
			if 'dvb' in y:
				drivername='dvb'
				x = popen('modinfo '+ drivername +' |grep -i version')
				x = x.read().strip().split()
				date = x[1];date = date[:14];b=date
				YY=b[0:4];MM=b[4:6];DD=b[6:8];HO=b[8:10];MI=b[10:12];SE=b[12:14]
				realdate=str(DD + '.' + MM + '.' + YY + ' - ' + HO  + ':' + MI + ':' + SE)
		except:
			realdate = about.getDriverInstalledDate()
		return realdate

	def showChangelogInfo(self):
		# self.session.open(Console,_("Changelog"),["cat /etc/enigma2/changelog.txt"])
		from Screens.Console import Console
		self.session.open(Console, title = _("Changelog"), cmdlist = ["cat /etc/enigma2/changelog.txt"])
		
#Keep this active for now. Yeah i know if you press blue you will get BSOD. After we add pManager would be ok:
	def showTeamInfo(self):
		try:
			from Plugins.Extensions.pManager.about import PureE2AboutTeam
		except Exception, e:
			print e
			# return
			
		self.session.open(PureE2AboutTeam)

		
	def showTroubleshoot(self):
		self.session.open(Troubleshoot)


class Troubleshoot(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("Troubleshoot"))
		self["AboutScrollLabel"] = ScrollLabel(_("Please wait"))
		self["key_red"] = Button()
		self["key_green"] = Button()

		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "ColorActions"],
			{
				"cancel": self.close,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown,
				"left": self.left,
				"right": self.right,
				"red": self.red,
				"green": self.green,
			})

		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.appClosed)
		self.container.dataAvail.append(self.dataAvail)
		self.commandIndex = 0
		self.updateOptions()
		self.onLayoutFinish.append(self.run_console)

	def left(self):
		self.commandIndex = (self.commandIndex - 1) % len(self.commands)
		self.updateKeys()
		self.run_console()

	def right(self):
		self.commandIndex = (self.commandIndex + 1) % len(self.commands)
		self.updateKeys()
		self.run_console()

	def red(self):
		if self.commandIndex >= self.numberOfCommands:
			self.session.openWithCallback(self.removeAllLogfiles, MessageBox, _("Do you want to remove all the crahs logfiles"), default=False)
		else:
			self.close()

	def green(self):
		if self.commandIndex >= self.numberOfCommands:
			try:
				os.remove(self.commands[self.commandIndex][4:])
			except:
				pass
			self.updateOptions()
		self.run_console()

	def removeAllLogfiles(self, answer):
		if answer:
			for fileName in self.getLogFilesList():
				try:
					os.remove(fileName)
				except:
					pass
			self.updateOptions()
			self.run_console()

	def appClosed(self, retval):
		if retval:
			self["AboutScrollLabel"].setText(_("Some error occured - Please try later"))

	def dataAvail(self, data):
		self["AboutScrollLabel"].appendText(data)

	def run_console(self):
		self["AboutScrollLabel"].setText("")
		self.setTitle("%s - %s" % (_("Troubleshoot"), self.titles[self.commandIndex]))
		command = self.commands[self.commandIndex]
		if command.startswith("cat "):
			try:
				self["AboutScrollLabel"].setText(open(command[4:], "r").read())
			except:
				self["AboutScrollLabel"].setText(_("Logfile does not exist anymore"))
		else:
			try:
				if self.container.execute(command):
					raise Exception, "failed to execute: ", command
			except Exception, e:
				self["AboutScrollLabel"].setText("%s\n%s" % (_("Some error occured - Please try later"), e))

	def cancel(self):
		self.container.appClosed.remove(self.appClosed)
		self.container.dataAvail.remove(self.dataAvail)
		self.container = None
		self.close()

	def getLogFilesList(self):
		import glob
		return [x for x in sorted(glob.glob("/mnt/hdd/*.log"), key=lambda x: os.path.isfile(x) and os.path.getmtime(x))] + (os.path.isfile("/home/root/enigma2_crash.log") and ["/home/root/enigma2_crash.log"] or [])

	def updateOptions(self):
		self.titles = ["dmesg", "ifconfig", "df", "top", "ps"]
		self.commands = ["dmesg", "ifconfig", "df -h", "top -b -n 1", "ps"]
		self.numberOfCommands = len(self.commands)
		fileNames = self.getLogFilesList()
		if fileNames:
			totalNumberOfLogfiles = len(fileNames)
			logfileCounter = 1
			for fileName in reversed(fileNames):
				self.titles.append("logfile %s (%s/%s)" % (fileName, logfileCounter, totalNumberOfLogfiles))
				self.commands.append("cat %s" % (fileName))
				logfileCounter += 1
		self.commandIndex = min(len(self.commands) - 1, self.commandIndex)
		self.updateKeys()

	def updateKeys(self):
		self["key_red"].setText(_("Cancel") if self.commandIndex < self.numberOfCommands else _("Remove all logfiles"))
		self["key_green"].setText(_("Refresh") if self.commandIndex < self.numberOfCommands else _("Remove this logfile"))
