# -*- coding: utf-8 -*-

import os
import sys
import xbmc
import xbmcvfs
import xbmcaddon
import xbmcgui
import traceback
import platform
import requests
import zipfile
import shutil
import urllib
import urllib2
from bs4 import BeautifulSoup as bs

addonid = 'script.module.webdriver'
logErorr = xbmc.LOGERROR

mhost = 'https://chromedriver.chromium.org/downloads'
dhost = 'https://chromedriver.storage.googleapis.com/'
dparam = 'index.html?path='
WFile = 'chromedriver_win32.zip'
LFile = 'chromedriver_linux64.zip'

class WDS:
    def __init__(self):
        try:
            self._addonid = addonid
            self._addon = xbmcaddon.Addon(self._addonid)
            self._addonName = self._addon.getAddonInfo('name')
            self._addonPath = self._addon.getAddonInfo('path')
            self._addonProfile = xbmc.translatePath(self._addon.getAddonInfo('profile'))
            if platform.system() == 'Windows':
                self._addonBin = xbmc.translatePath(os.path.join(os.path.join(os.path.join(self._addonPath, 'bin'), 'chromedriver'), 'win32'))
            if platform.system() == 'Linux':
                self._addonBin = xbmc.translatePath(os.path.join(os.path.join(os.path.join(self._addonPath, 'bin'), 'chromedriver'), 'linux64'))
            self._addonDownload = self._addonProfile + 'download'

            self._version = self._addon.getSetting('version')
            self._delfiles = self._addon.getSetting('delfiles')
            self._debug = self._addon.getSetting('debug')

            self.getParams()
            self.setAction()

        except Exception, e:
            self.addLog('WDS::__init__', 'ERROR: (' + repr(e) + ')', logErorr)

    def getLang(self, code):
        return self._addon.getLocalizedString(code)

    def addLog(self, source, text, level=xbmc.LOGNOTICE):
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
        except Exception, e:
            self.addLog('WDS::getParams', 'ERROR: (' + repr(e) + ')', logErorr)

    def setAction(self):
        try:
            self.addLog('WDS::setAction', 'enter_function')
            if self._action == 'selectdriver':
                self.selectDriver()
            self.addLog('WDS::setAction', 'exit_function')
        except Exception, e:
            self.addLog('WDS::setAction', 'ERROR: (' + repr(e) + ')', logErorr)

    def selectDriver(self):
        try:
            self.addLog('WDS::selectDriver', 'enter_function')
            self.getListDriver()
            self.addLog('WDS::selectDriver', 'exit_function')
        except Exception, e:
            self.addLog('WDS::selectDriver', 'ERROR: (' + repr(e) + ')', logErorr)

    def getListDriver(self):
        try:
            self.addLog('WDS::getListDriver', 'enter_function')
            xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
            ListDriver = {}
            html = self.loadUrl(mhost).strip().decode('utf-8')
            soup = bs(html, 'html.parser')
            self.addLog('WDS::getListDriver', 'soup')
            if soup:
                for item in soup.find_all('a', href=True):
                    if item:
                        url = str(item['href'])
                        title = str(item.text)
                        if title.startswith('ChromeDriver ') and url.startswith(dhost + dparam):
                            title = title.split(' ')[1]
                            if title not in ListDriver:
                                ListDriver[title] = url
                                self.addLog('WDS::getListDriver','Data: ' + title + ' -> ' + ListDriver[title])
            if len(ListDriver) > 0:
                sel_index = 0
                sel_source_name = 'none'
                dialog = xbmcgui.Dialog()
                sel_index = dialog.select(self.getLang(32002), sorted(ListDriver.keys(), reverse=True))
                self.addLog('WDS::getListDriver','SLECT URL INDEX: ' + str(sel_index))
                if sel_index >= 0:
                    sel_source_name = sorted(ListDriver.keys(), reverse=True)[sel_index]
                if sel_source_name != 'none':
                    sel_source_url = ListDriver[sel_source_name]
                    self.addLog('WDS::getListDriver','SEL URL: ' + sel_source_name + ' : ' + sel_source_url)
                    self.downloadDriver(sel_source_name)
            xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
            self.addLog('WDS::getListDriver', 'exit_function')
        except Exception, e:
            xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('List Driver', 'ERROR: ' + repr(e))
            self.addLog('WDS::getListDriver', 'ERROR: (' + repr(e) + ')', logErorr)

    def downloadDriver(self, version):
        try:
            self.addLog('WDS::downloadDriver', 'enter_function')
            nddir = os.path.join(self._addonDownload, version)
            if not os.path.exists(nddir):
                os.makedirs(nddir)

            if platform.system() == 'Windows':
                url = dhost + version + '/' + WFile
                ndfile = os.path.join(nddir, WFile)
            if platform.system() == 'Linux':
                url = dhost + version + '/' + LFile
                ndfile = os.path.join(nddir, LFile)

            self.addLog('WDS::downloadDriver', url)
            self.addLog('WDS::downloadDriver', ndfile)
            self.addLog('WDS::downloadDriver', self._addonBin)

            get_response = requests.get(url,stream=True)
            with open(ndfile, 'wb') as f:
                for chunk in get_response.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)

            with zipfile.ZipFile(ndfile,"r") as zip_ref:
                zip_ref.extractall(self._addonBin)

            dialog = xbmcgui.Dialog()
            dialog.ok(self.getLang(32002), version)

            self._version = version
            self._addon.setSetting('version', version)

            if self._delfiles == 'true':
                shutil.rmtree(self._addonDownload) 

            self.addLog('WDS::downloadDriver', 'exit_function')
        except Exception, e:
            self.addLog('WDS::downloadDriver', 'ERROR: (' + repr(e) + ')', logErorr)

    def loadUrl(self, url):
        try:
            self.addLog('WDS::loadUrl', 'enter_function')
            self.addLog('WDS::loadUrl','OPEN URL: ' + url)
            headers = {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3',
            'Content-Type': 'application/x-www-form-urlencoded'}
            connect = urllib2.urlopen(urllib2.Request(url, urllib.urlencode({}), headers))
            cont = connect.read()
            connect.close()
            self.addLog('WDS::loadUrl', 'exit_function')
            return cont
        except Exception, e:
            self.addLog('WDS::loadUrl(' + url + ')', 'ERROR: (' + repr(e) + ')', logErorr)
