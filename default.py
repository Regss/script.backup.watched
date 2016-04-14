# -*- coding: utf-8 -*-

import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import json
import os
import ntpath
import re
import datetime

__addon__               = xbmcaddon.Addon()
__addon_id__            = __addon__.getAddonInfo('id')
__addonname__           = __addon__.getAddonInfo('name')
__addonpath__           = xbmc.translatePath(__addon__.getAddonInfo('path'))
__datapath__            = xbmc.translatePath(os.path.join('special://profile/addon_data/', __addon_id__)).replace('\\', '/') + '/'
__icon__                = __addon__.getAddonInfo('icon')
__lang__                = __addon__.getLocalizedString
__path__                = os.path.join(__addonpath__, 'resources', 'lib' )
__path_img__            = os.path.join(__addonpath__, 'resources', 'media' )

sys.path.append(__path__)

import menuDialog
import backup
import restore

class Start:
    def __init__(self):
        self.start()
        
    def start(self):
        # check mode
        if (len(sys.argv) == 0 or len(sys.argv[0]) == 0):
            
        
            # menu
            ret = menuDialog.DIALOG().start(__lang__(32100), [__lang__(32101), __lang__(32102)])
            if ret == 0:
                backup.Backup()
            if ret == 1:
                restore.Restore()
            
        else:
            backup.Backup()
            
            
            
        


                

        

        
class Bar:
    def __init__(self):
        self.xbmc_version = int(xbmc.getInfoLabel('System.BuildVersion')[0:2])
        if self.xbmc_version > 12:
            self.b = xbmcgui.DialogProgressBG()
        else:
            self.b = xbmcgui.DialogProgress()
            
    def create(self, message, heading):
        self.b.create(heading, message)
            
    def update(self, percent, message):
        if self.xbmc_version > 12:
            self.b.update(percent, message=message)
        else:
            self.b.update(percent, line1=message)
                
    def close(self):
        self.b.close()
            


Start()
    