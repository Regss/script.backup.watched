# -*- coding: utf-8 -*-

import xbmc
import xbmcaddon
import xbmcvfs
import json 
import os
import datetime
import re

__addon__               = xbmcaddon.Addon()
__addon_id__            = __addon__.getAddonInfo('id')
__datapath__            = xbmc.translatePath(os.path.join('special://profile/addon_data/', __addon_id__)).replace('\\', '/') + '/'
__lang__                = __addon__.getLocalizedString

import debug

class Backup:
    def __init__(self):
        self.start()
        
    def start(self):
        table = { 'movies': {}, 'episodes': {} }
        movies = []
        
        for t in table.keys():
            jsonGet = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.Get' +  t.title() + '", "params": {"filter": {"field": "playcount", "operator": "greaterthan", "value": "0"}, "properties": ["playcount", "lastplayed", "file"]}, "id": 1}')
            jsonGet = json.loads(unicode(jsonGet, 'utf-8'))
            
            if 'result' in jsonGet and t in jsonGet['result']:
                for m in jsonGet['result'][t]:
                    table[t][m['file']] = {
                        'playcount': m['playcount'],
                        'lastplayed': m['lastplayed']
                    }
                
        # create dir in addon data if not exist
        if not xbmcvfs.exists(__datapath__):
            xbmcvfs.mkdir(__datapath__)
        
        # remove old files
        amountBackups = __addon__.getSetting('amountBackups')
        b_files = os.listdir(__datapath__)
        r_files = []
        for file in b_files:
            if re.search('w_([0-9]{14}_[0-9]+).json', file):
                r_files.append(file)
        
        for r in r_files[:-(int(amountBackups)-1)]:
            xbmcvfs.delete(__datapath__ + r)
        
        # create new file with data
        # prevent lock import module - python bug
        while(1):
            try:
                a_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                break;
            except:
                pass
        countTables = len(table['movies']) + len(table['episodes'])
        f = xbmcvfs.File(__datapath__ + 'w_' + a_time + '_' + str(countTables) + '.json', 'w')
        f.write(json.dumps(table))
        f.close()
        self.saveTime()
        debug.notify(__lang__(32103) + ' - ' + str(len(table['movies']) + len(table['episodes'])) + ' ' + __lang__(32105))
        
    def saveTime(self):
        if not xbmcvfs.exists(__datapath__):
            xbmcvfs.mkdir(__datapath__)
        fileLastBackup = __datapath__ + 'lastBackup'
        t = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file = xbmcvfs.File(fileLastBackup, 'w')
        file.write(t)
        file.close()
        