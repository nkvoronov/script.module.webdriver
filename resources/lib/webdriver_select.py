# -*- coding: utf-8 -*-

import os
import sys
import xbmc
import xbmcvfs
import xbmcaddon
import xbmcgui
import traceback

addonid = 'script.module.webdriver'
logErorr = xbmc.LOGERROR

mhost = 'https://chromedriver.chromium.org/downloads'
dhost = 'https://chromedriver.storage.googleapis.com/index.html'
dparam = 'path'
WFile = 'chromedriver_win32.zip'
LFile = 'chromedriver_linux64.zip'

#Select
#Download
#Extract

class WDS(object):
    def __init__(self):
        try:
            self._addonid = addonid
            self._addon = xbmcaddon.Addon(self._addonid)
            self._addonName = self._addon.getAddonInfo('name')
            self._addonPath = self._addon.getAddonInfo('path')
            self._addonMedia = xbmcvfs.translatePath(os.path.join(os.path.join(os.path.join(os.path.join(self._addonPath, 'resources'), 'skins'), 'default'), 'media'))

            self._debug = self._addon.getSetting('debug')
            self._version = self._addon.getSetting('version')

            self.getParams()
            self.setAction()

        except Exception as e:
            self.addLog('WDS::__init__', 'ERROR: (' + repr(e) + ')', logErorr)

    def getLang(self, code):
        return self._addon.getLocalizedString(code)

    def addLog(self, source, text, level=xbmc.LOGINFO):
        if self._debug == 'false':
            return
        xbmc.log('## ' + self._addonName + ' ## ' + source + ' ## ' + text, level)
        xbmc.log(traceback.format_exc())

    def getParams(self):
        try:
            self.addLog('WDS::getParams', 'enter_function')
            if len(sys.argv) > 1:
                params = dict(arg.split("=") for arg in sys.argv[ 1 ].split("&"))
            else:
                params = {}
            self.addLog('WDS::getParams', 'params: %s' % params, logErorr)
            self._action = params.get('action', '')
            self.addLog('WDS::getParams', 'exit_function')
        except Exception as e:
            self.addLog('WDS::getParams', 'ERROR: (' + repr(e) + ')', logErorr)

    def setAction(self):
        try:
            self.addLog('WDS::setAction', 'enter_function')
            if self._action == 'selectdriver':
                self.selectDriver()
            self.addLog('WDS::setAction', 'exit_function')
        except Exception as e:
            self.addLog('WDS::setAction', 'ERROR: (' + repr(e) + ')', logErorr)

    def selectDriver(self):
        try:
            self.addLog('WDS::selectDriver', 'enter_function')
            self.getListDriver()
            self.addLog('WDS::selectDriver', 'exit_function')
        except Exception as e:
            self.addLog('WDS::selectDriver', 'ERROR: (' + repr(e) + ')', logErorr)

    def getListDriver(self):
        try:
            self.addLog('WDS::getListDriver', 'enter_function')
            dialog = xbmcgui.Dialog()
            dialog.ok('SELECT', 'SELECT')
            self.addLog('WDS::getListDriver', 'exit_function')
        except Exception as e:
            self.addLog('WDS::getListDriver', 'ERROR: (' + repr(e) + ')', logErorr)
            