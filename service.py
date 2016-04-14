# -*- coding: utf-8 -*-

import xbmc
import xbmcaddon
import datetime
import os

__addon__               = xbmcaddon.Addon()
__addon_id__            = __addon__.getAddonInfo('id')
__addonname__           = __addon__.getAddonInfo('name')
__icon__                = __addon__.getAddonInfo('icon')
__addonpath__           = xbmc.translatePath(__addon__.getAddonInfo('path'))
__datapath__            = xbmc.translatePath(os.path.join('special://profile/addon_data/', __addon_id__)).replace('\\', '/') + '/'

class Player(xbmc.Player):

    def __init__(self):
        if 'true' in __addon__.getSetting('onKodiStart'):
            xbmc.executebuiltin('XBMC.RunScript(' + __addon_id__ + ', true)')
        xbmc.Player.__init__(self)
        
    def onPlayBackStopped(self):
        if 'true' in __addon__.getSetting('onPlayBackStopped'):
            onHour = int(__addon__.getSetting('onHour'))
            withDelta = int((datetime.datetime.now() - datetime.timedelta(hours=onHour)).strftime("%Y%m%d%H%M%S"))
            getLastTime = self.getTime()
            if withDelta > getLastTime:
                xbmc.executebuiltin('XBMC.RunScript(' + __addon_id__ + ', true)')
    
    def getTime(self):
        fileLastBackup = __datapath__ + 'lastBackup'
        try:
            file = open(fileLastBackup, 'r')
            t = int(file.read())
            file.close()
        except:
            t = 0
        return t
        
player = Player()

while(not xbmc.abortRequested):
    xbmc.sleep(100)
    