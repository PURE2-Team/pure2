##05.05.2017 - Edit Franc: ask for extra confirmation if user choose to reboot into Recovery Mode [retvalue = 16] 
import os
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.config import config
from Components.AVSwitch import AVSwitch
from Components.Console import Console
from Components.SystemInfo import SystemInfo
from Components.Harddisk import harddiskmanager
from GlobalActions import globalActionMap
from enigma import eDVBVolumecontrol, eTimer, eDVBLocalTimeHandler, eServiceReference
from boxbranding import getMachineBrand, getMachineName, getBoxType, getBrandOEM
from Tools import Notifications
from time import localtime, time
import Screens.InfoBar
from gettext import dgettext
import Components.RecordingConfig
inStandby = None

def setLCDModeMinitTV(value):
    try:
        f = open('/proc/stb/lcd/mode', 'w')
        f.write(value)
        f.close()
    except:
        pass


class Standby2(Screen):

    def Power(self):
        print '[Standby] leave standby'
        if os.path.exists('/usr/script/StandbyLeave.sh'):
            Console().ePopen('/usr/script/StandbyLeave.sh &')
        if getBrandOEM() in 'fulan':
            open('/proc/stb/hdmi/output', 'w').write('on')
        self.avswitch.setInput('ENCODER')
        self.leaveMute()
        if SystemInfo['Display'] and SystemInfo['LCDMiniTV']:
            setLCDModeMinitTV(config.lcd.modeminitv.value)
        self.close(True)

    def Power_make(self):
        if config.usage.on_short_powerpress.value != 'standby_noTVshutdown':
            self.Power()

    def Power_long(self):
        if config.usage.on_short_powerpress.value == 'standby_noTVshutdown':
            self.TVoff()
            self.ignoreKeyBreakTimer.start(250, 1)

    def Power_repeat(self):
        if config.usage.on_short_powerpress.value == 'standby_noTVshutdown' and self.ignoreKeyBreakTimer.isActive():
            self.ignoreKeyBreakTimer.start(250, 1)

    def Power_break(self):
        if config.usage.on_short_powerpress.value == 'standby_noTVshutdown' and not self.ignoreKeyBreakTimer.isActive():
            self.Power()

    def TVoff(self):
        print '[Standby] TVoff'
        try:
            config.hdmicec.control_tv_standby_skipnow.setValue(False)
            config.hdmicec.TVoffCounter.value += 1
        except:
            pass

    def setMute(self):
        if eDVBVolumecontrol.getInstance().isMuted():
            self.wasMuted = 1
            print '[Standby] mute already active'
        else:
            self.wasMuted = 0
            eDVBVolumecontrol.getInstance().volumeToggleMute()

    def leaveMute(self):
        if self.wasMuted == 0:
            eDVBVolumecontrol.getInstance().volumeToggleMute()

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skinName = 'Standby'
        self.avswitch = AVSwitch()
        print '[Standby] enter standby'
        if os.path.exists('/usr/script/StandbyEnter.sh'):
            Console().ePopen('/usr/script/StandbyEnter.sh &')
        self['actions'] = ActionMap(['StandbyActions'], {'power': self.Power,
         'power_make': self.Power_make,
         'power_break': self.Power_break,
         'power_long': self.Power_long,
         'power_repeat': self.Power_repeat,
         'discrete_on': self.Power}, -1)
        globalActionMap.setEnabled(False)
        self.ignoreKeyBreakTimer = eTimer()
        self.standbyStopServiceTimer = eTimer()
        self.standbyStopServiceTimer.callback.append(self.stopService)
        self.timeHandler = None
        self.setMute()
        if SystemInfo['Display'] and SystemInfo['LCDMiniTV']:
            setLCDModeMinitTV('0')
        self.paused_service = None
        self.prev_running_service = None
        self.prev_running_service = self.session.nav.getCurrentlyPlayingServiceOrGroup()
        service = self.prev_running_service and self.prev_running_service.toString()
        if service:
            if service.startswith('1:') and service.rsplit(':', 1)[1].startswith('/'):
                self.paused_service = self.session.current_dialog
                self.paused_service.pauseService()
        if not self.paused_service:
            self.timeHandler = eDVBLocalTimeHandler.getInstance()
            if self.timeHandler.ready():
                if self.session.nav.getCurrentlyPlayingServiceOrGroup():
                    self.stopService()
                else:
                    self.standbyStopServiceTimer.startLongTimer(5)
                self.timeHandler = None
            else:
                self.timeHandler.m_timeUpdated.get().append(self.stopService)
        if self.session.pipshown:
            from Screens.InfoBar import InfoBar
            InfoBar.instance and hasattr(InfoBar.instance, 'showPiP') and InfoBar.instance.showPiP()
        if SystemInfo['ScartSwitch']:
            self.avswitch.setInput('SCART')
        else:
            self.avswitch.setInput('AUX')
        if getBrandOEM() in 'fulan':
            open('/proc/stb/hdmi/output', 'w').write('off')
        if int(config.usage.hdd_standby_in_standby.value) != -1:
            for hdd in harddiskmanager.HDDList():
                hdd[1].setIdleTime(int(config.usage.hdd_standby_in_standby.value))

        self.onFirstExecBegin.append(self.__onFirstExecBegin)
        self.onClose.append(self.__onClose)
        return

    def __onClose(self):
        global inStandby
        inStandby = None
        self.standbyStopServiceTimer.stop()
        self.timeHandler and self.timeHandler.m_timeUpdated.get().remove(self.stopService)
        if self.paused_service:
            self.paused_service.unPauseService()
        elif self.prev_running_service:
            service = self.prev_running_service.toString()
            if config.servicelist.startupservice_onstandby.value:
                self.session.nav.playService(eServiceReference(config.servicelist.startupservice.value))
                from Screens.InfoBar import InfoBar
                InfoBar.instance and InfoBar.instance.servicelist.correctChannelNumber()
            else:
                self.session.nav.playService(self.prev_running_service)
        self.session.screen['Standby'].boolean = False
        globalActionMap.setEnabled(True)
        for hdd in harddiskmanager.HDDList():
            hdd[1].setIdleTime(int(config.usage.hdd_standby.value))

        return

    def __onFirstExecBegin(self):
        global inStandby
        inStandby = self
        self.session.screen['Standby'].boolean = True
        config.misc.standbyCounter.value += 1

    def createSummary(self):
        return StandbySummary

    def stopService(self):
        self.prev_running_service = self.session.nav.getCurrentlyPlayingServiceOrGroup()
        self.session.nav.stopService()


class Standby(Standby2):

    def __init__(self, session):
        if Screens.InfoBar.InfoBar and Screens.InfoBar.InfoBar.instance and Screens.InfoBar.InfoBar.ptsGetTimeshiftStatus(Screens.InfoBar.InfoBar.instance):
            self.skin = '<screen position="0,0" size="0,0"/>'
            Screen.__init__(self, session)
            self.onFirstExecBegin.append(self.showMessageBox)
            self.onHide.append(self.close)
        else:
            Standby2.__init__(self, session)
            self.skinName = 'Standby'

    def showMessageBox(self):
        Screens.InfoBar.InfoBar.checkTimeshiftRunning(Screens.InfoBar.InfoBar.instance, self.showMessageBoxcallback)

    def showMessageBoxcallback(self, answer):
        if answer:
            self.onClose.append(self.doStandby)

    def doStandby(self):
        Notifications.AddNotification(Screens.Standby.Standby2)


class StandbySummary(Screen):
    skin = '\n\t<screen position="0,0" size="132,64">\n\t\t<widget source="global.CurrentTime" render="Label" position="0,0" size="132,64" font="Regular;40" halign="center">\n\t\t\t<convert type="ClockToText" />\n\t\t</widget>\n\t\t<widget source="session.RecordState" render="FixedLabel" text=" " position="0,0" size="132,64" zPosition="1" >\n\t\t\t<convert type="ConfigEntryTest">config.usage.blinking_display_clock_during_recording,True,CheckSourceBoolean</convert>\n\t\t\t<convert type="ConditionalShowHide">Blink</convert>\n\t\t</widget>\n\t</screen>'


from enigma import quitMainloop, iRecordableService
from Screens.MessageBox import MessageBox
from time import time
from Components.Task import job_manager

class QuitMainloopScreen(Screen):

    def __init__(self, session, retvalue = 1):
        self.skin = '<screen name="QuitMainloopScreen" position="fill" flags="wfNoBorder">\n\t\t\t<ePixmap pixmap="icons/input_info.png" position="c-27,c-60" size="53,53" alphatest="on" />\n\t\t\t<widget name="text" position="center,c+5" size="720,100" font="Regular;22" halign="center" />\n\t\t</screen>'
        Screen.__init__(self, session)
        from Components.Label import Label
        text = {1: _('Your %s %s is shutting down') % (getMachineBrand(), getMachineName()),
         2: _('Your %s %s is rebooting') % (getMachineBrand(), getMachineName()),
         3: _('The user interface of your %s %s is restarting') % (getMachineBrand(), getMachineName()),
         4: _('Your frontprocessor will be upgraded\nPlease wait until your %s %s reboots\nThis may take a few minutes') % (getMachineBrand(), getMachineName()),
         5: _('The user interface of your %s %s is restarting\ndue to an error in mytest.py') % (getMachineBrand(), getMachineName()),
         16: _('Your %s %s is rebooting into Recovery Mode') % (getMachineBrand(), getMachineName()),
         42: _('Upgrade in progress\nPlease wait until your %s %s reboots\nThis may take a few minutes') % (getMachineBrand(), getMachineName()),
         43: _('Reflash in progress\nPlease wait until your %s %s reboots\nThis may take a few minutes') % (getMachineBrand(), getMachineName()),
         44: _('Your front panel will be upgraded\nThis may take a few minutes'),
         45: _('Your %s %s goes to WOL') % (getMachineBrand(), getMachineName())}.get(retvalue)
        self['text'] = Label(text)


inTryQuitMainloop = False
quitMainloopCode = 1

class TryQuitMainloop(MessageBox):

    def __init__(self, session, retvalue = 1, timeout = -1, default_yes = True):
        self.retval = retvalue
        self.ptsmainloopvalue = retvalue
        recordings = session.nav.getRecordings(False, Components.RecordingConfig.recType(config.recording.warn_box_restart_rec_types.getValue()))
        jobs = len(job_manager.getPendingJobs())
        inTimeshift = Screens.InfoBar.InfoBar and Screens.InfoBar.InfoBar.instance and Screens.InfoBar.InfoBar.ptsGetTimeshiftStatus(Screens.InfoBar.InfoBar.instance)
        self.connected = False
        reason = ''
        next_rec_time = -1
        if not recordings:
            next_rec_time = session.nav.RecordTimer.getNextRecordingTime()
        if inTimeshift:
            reason = _('You seem to be in timeshift!') + '\n'
            default_yes = True
            timeout = 30
        if recordings or next_rec_time > 0 and next_rec_time - time() < 360:
            default_yes = False
            reason = _('Recording(s) are in progress or coming up in few seconds!') + '\n'

        #/////////////////////////////////////////////////////////////////////////////////
        #Check for Recovery Mode and ask for extra confirmation. Nasty, but ok for now.
        if retvalue == 16:
            reason = _(" ")
        #/////////////////////////////////////////////////////////////////////////////////

        if reason and inStandby:
            session.nav.record_event.append(self.getRecordEvent)
            self.skinName = ''
        elif reason and not inStandby:
            text = {1: _('Really shutdown now?'),
             2: _('Really reboot now?'),
             3: _('Really restart now?'),
             4: _('Really upgrade the frontprocessor and reboot now?'),
             16: _('Really reboot into Recovery Mode?'),
             42: _('Really upgrade your %s %s and reboot now?') % (getMachineBrand(), getMachineName()),
             43: _('Really reflash your %s %s and reboot now?') % (getMachineBrand(), getMachineName()),
             44: _('Really upgrade the front panel and reboot now?'),
             45: _('Really WOL now?')}.get(retvalue)
            if text:
                MessageBox.__init__(self, session, reason + text, type=MessageBox.TYPE_YESNO, timeout=timeout, default=default_yes)
                self.skinName = 'MessageBoxSimple'
                session.nav.record_event.append(self.getRecordEvent)
                self.connected = True
                self.onShow.append(self.__onShow)
                self.onHide.append(self.__onHide)
                return
        self.skin = '<screen position="1310,0" size="0,0"/>'
        Screen.__init__(self, session)
        self.close(True)

    def getRecordEvent(self, recservice, event):
        if event == iRecordableService.evEnd and config.timeshift.isRecording.value:
            return
        if event == iRecordableService.evEnd:
            recordings = self.session.nav.getRecordings(False, Components.RecordingConfig.recType(config.recording.warn_box_restart_rec_types.getValue()))
            if not recordings:
                rec_time = self.session.nav.RecordTimer.getNextRecordingTime()
                if rec_time > 0 and rec_time - time() < 360:
                    self.initTimeout(360)
                    self.startTimer()
                else:
                    self.close(True)
        elif event == iRecordableService.evStart:
            self.stopTimer()

    def close(self, value):
        global quitMainloopCode
        if self.connected:
            self.connected = False
            self.session.nav.record_event.remove(self.getRecordEvent)
        if value:
            self.hide()
            if self.retval == 1:
                config.misc.DeepStandby.value = True
            self.session.nav.stopService()
            self.quitScreen = self.session.instantiateDialog(QuitMainloopScreen, retvalue=self.retval)
            self.quitScreen.show()
            print '[Standby] quitMainloop #1'
            quitMainloopCode = self.retval
            if SystemInfo["Display"] and SystemInfo["LCDMiniTV"]:
                # set LCDminiTV off / fix a deep-standby-crash on some boxes / gb4k 
                print "[Standby] LCDminiTV off"
                setLCDModeMinitTV("0")
            if getBoxType() == 'vusolo4k':
                open('/proc/stb/fp/oled_brightness', 'w').write('0')
            quitMainloop(self.retval)
        else:
            MessageBox.close(self, True)

    def __onShow(self):
        global inTryQuitMainloop
        inTryQuitMainloop = True

    def __onHide(self):
        global inTryQuitMainloop
        inTryQuitMainloop = False
