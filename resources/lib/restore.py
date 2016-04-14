# -*- coding: utf-8 -*-

import xbmc
import xbmcaddon
import xbmcvfs
import xbmcgui
import json 
import os
import datetime
import re
import ntpath

__addon__               = xbmcaddon.Addon()
__addon_id__            = __addon__.getAddonInfo('id')
__addonname__           = __addon__.getAddonInfo('name')
__datapath__            = xbmc.translatePath(os.path.join('special://profile/addon_data/', __addon_id__)).replace('\\', '/') + '/'
__lang__                = __addon__.getLocalizedString

import debug
import menuDialog

class Restore():
    
    def __init__(self):   
        self.start()
    
    def start(self):
        # get avalible files
        files = []
        names = []
        dir = os.listdir(__datapath__)
        
        # append to list
        i = 1
        for file in dir:
            m = re.match('w_([0-9]{4})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})_([0-9]+).json', file)
            if m:
                files.append(file)
                names.append(str(i) + '. - ' + m.group(3) + '.' + m.group(2) + '.' + m.group(1) + ' ' + m.group(4) + ':' + m.group(5) + ':' + m.group(6) + ' - ' + m.group(7) + ' ' + __lang__(32105))
                i = i + 1
        
        debug.debug('[Backup files]: ' + str(files))
        if len(files) == 0:
            debug.notify(__lang__(32104))
            return
            
        ret = menuDialog.DIALOG().start(__lang__(32109), names)
        if ret is not None:
            self.restore(files[ret])
            
    def restore(self, file):
        
        # read watched status from file
        f = xbmcvfs.File(__datapath__ + file, 'r')
        result = f.read()
        f.close()
        json_data = json.loads(result)
        debug.debug('[Json backup file]: ' + str(json_data))
        
        toRestore = len(json_data['movies']) + len(json_data['episodes'])
        
        if toRestore == 0:
            xbmcgui.Dialog().ok(__addonname__, __lang__(32107))
            return
        
        # select restore method
        method = xbmcgui.Dialog().yesno(__addonname__, __lang__(32112), yeslabel=__lang__(32114).title(), nolabel=__lang__(32113).title())
        debug.debug('[Method]: ' + str(method))
        
        # prepare table from backup
        backup_data = { 'movies': {}, 'episodes': {} }
        for table in json_data.keys():
            for filename in json_data[table].keys():
                file = filename if method == 0 else ntpath.basename(filename)
                backup_data[table][file] = json_data[table][filename]
        debug.debug('[backup_data]: ' + str(backup_data))
    
        # prepare table from KODI
        xbmc_data = { 'movies': {}, 'episodes': {} }
        for t in xbmc_data.keys():
            jsonGetWatched = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.Get' +  t.title() + '", "params": {"properties": ["title", "file"]}, "id": 1}')
            jsonGetWatched = unicode(jsonGetWatched, 'utf-8')
            jsonGetWatched = json.loads(jsonGetWatched)
            
            if 'result' in jsonGetWatched and t in jsonGetWatched['result']:
                for m in jsonGetWatched['result'][t]:
                    file = m['file'] if method == 0 else ntpath.basename(m['file'])
                    xbmc_data[t][file] = {
                        'id': m[t[:-1] + 'id'],
                        'title': m['title']
                    }
        debug.debug('[xbmc_data]: ' + str(xbmc_data))
        
        finded_data = { 'movies': {}, 'episodes': {} }
        for table in backup_data.keys():
            finded_data[table] = set(backup_data[table].keys()) & set(xbmc_data[table].keys())
        debug.debug('[finded_data]: ' + str(finded_data))
        
        # confirm
        yesno = xbmcgui.Dialog().yesno(__addonname__, __lang__(32117) + ':[CR]' + __lang__(32115) + ': ' + str(len(backup_data['movies'])) + ' ' + __lang__(32116) + ': ' + str(len(backup_data['episodes'])) + '[CR]' + __lang__(32118) + ':[CR]' +  __lang__(32115) + ': ' + str(len(finded_data['movies'])) + ' ' + __lang__(32116) + ': ' + str(len(finded_data['episodes'])), yeslabel=__lang__(32111).title(), nolabel=__lang__(32108).title())
        if yesno == 0:
            return False
        
        prog = xbmcgui.DialogProgress()
        prog.create(__lang__(32201), __addonname__ + ', ' + __lang__(32200))
        
        toRestore = len(finded_data['movies']) + len(finded_data['episodes'])
        restored = 0
        for table, item_list in finded_data.items():
            
            for filename in item_list:
                restored += 1
                p = int((float(100) / float(toRestore)) * float(restored))
                prog.update(p, str(restored) + ' / ' + str(toRestore) + ' - ' + xbmc_data[table][filename]['title'])
                jsonGet = '{"jsonrpc": "2.0", "method": "VideoLibrary.Set' + table.title()[:-1] + 'Details", "params": {"playcount": ' + str(backup_data[table][filename]['playcount']) + ', "lastplayed": "' + backup_data[table][filename]['lastplayed'] + '", "' + table[:-1] + 'id": ' + str(xbmc_data[table][filename]['id']) + '}, "id": 1}'
                jsonGet = xbmc.executeJSONRPC(jsonGet)
                debug.debug('[Json updated]:' + str(jsonGet))
                
        prog.close()
        
        debug.notify(__lang__(32106) + ' - ' + str(restored) + ' ' + __lang__(32105))
