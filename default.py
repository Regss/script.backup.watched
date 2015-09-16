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
__path_img__            = __addonpath__ + '/images/'
__lang__                = __addon__.getLocalizedString

ACTION_PREVIOUS_MENU = 10
ACTION_SELECT_ITEM = 7
ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ACTION_MOVE_UP = 3
ACTION_MOVE_DOWN = 4
ACTION_STEP_BACK = 21
ACTION_NAV_BACK = 92
ACTION_MOUSE_RIGHT_CLICK = 101
ACTION_MOUSE_MOVE = 107
ACTION_BACKSPACE = 110
KEY_BUTTON_BACK = 275

class Start:
    def __init__(self):
        # check mode
        try:
            mode = str(sys.argv[1])
        except:
            mode = False

        if mode is False:
            gui = GUI()
            gui.doModal()
            del gui
        else:
            Backup()

# GUI
class GUI(xbmcgui.WindowDialog):

    def __init__(self):
        self.button = {}
        bgResW = 520
        bgResH = 150
        bgPosX = (1280 - bgResW) / 2
        bgPosY = (720 - bgResH) / 2
        self.start = 1
        
        # add controls
        self.bg = xbmcgui.ControlImage(bgPosX, bgPosY, bgResW, bgResH, __path_img__ + 'bg.png')
        self.addControl(self.bg)
        
        self.strActionInfo = xbmcgui.ControlLabel(bgPosX, bgPosY+20, 520, 200, __lang__(32100), 'font14', '0xFFFFFFFF', alignment=2)
        self.addControl(self.strActionInfo)
        
        self.button[1] = xbmcgui.ControlButton(bgPosX+30, bgPosY+80, 220, 50, __lang__(32101), alignment=6, font='font13')
        self.addControl(self.button[1])
        self.setFocus(self.button[1])
        
        self.button[2] = xbmcgui.ControlButton(bgPosX+270, bgPosY+80, 220, 50, __lang__(32102), alignment=6, font='font13')
        self.addControl(self.button[2])
        
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU or action == ACTION_STEP_BACK or action == ACTION_BACKSPACE or action == ACTION_NAV_BACK or action == KEY_BUTTON_BACK or action == ACTION_MOUSE_RIGHT_CLICK:
            self.close()
        if action == ACTION_MOVE_LEFT:
            if self.start > 1:
                self.start = self.start - 1
            self.setFocus(self.button[self.start])
        if action == ACTION_MOVE_RIGHT:
            if self.start < 2:
                self.start = self.start + 1
            self.setFocus(self.button[self.start])
            
    def onControl(self, control):
        if control == self.button[1]:
            self.close()
            Backup()
            
        if control == self.button[2]:
            self.close()
            
            # get avalible files
            files = []
            dir = os.listdir(__datapath__)
            # append to list
            for file in dir:
                find = re.search('(w_[0-9]{14}_[0-9]+.json)', file)
                if find:
                    files.append(file)
            print files
            if len(files) > 0:
                restore = Restore(files)
                restore.doModal(files)
                del restore
            else:
                Debug().notify(__lang__(32104))
                
class Backup:
    # backup all watched status and save to file
    def __init__(self):
        table = { 'movies': {}, 'episodes': {} }
        movies = []
        
        for t in table.keys():
            jsonGetWatched = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.Get' +  t.title() + '", "params": {"filter": {"field": "playcount", "operator": "greaterthan", "value": "0"}, "properties": ["playcount", "lastplayed", "file"]}, "id": 1}')
            jsonGetWatched = unicode(jsonGetWatched, 'utf-8')
            jsonGetWatched = json.loads(jsonGetWatched)
            
            if 'result' in jsonGetWatched and t in jsonGetWatched['result']:
                for m in jsonGetWatched['result'][t]:
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
        
        for r in r_files[:-int(amountBackups)]:
            os.remove(__datapath__ + r)
        
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
        Debug().notify(__lang__(32103) + ' - ' + str(len(table['movies']) + len(table['episodes'])) + ' ' + __lang__(32105))
        
    def saveTime(self):
        if not xbmcvfs.exists(__datapath__):
            xbmcvfs.mkdir(__datapath__)
        fileLastBackup = __datapath__ + 'lastBackup'
        t = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file = open(fileLastBackup, 'w')
        file.write(t)
        file.close()
        
class Restore(xbmcgui.WindowDialog):
    
    def __init__(self, fi):    
        btW = 500
        btH = 50
        btPosX = (1280 - btW) / 2
        btPosY = 160
             
        # sort and transform to dict
        fi.reverse()
        self.files = {}
        c = 0
        for  f in fi:
            self.files[c] = f
            c += 1
        lenFiles = len(self.files)
        
        # background
        bgW = btW + 40
        if lenFiles < 5:
            bgH = (btH*(lenFiles+1)) + 40
        else:
            bgH = btH*6 + 40
        bgPosX = btPosX - 20
        bgPosY = btPosY - 20
        
        self.bg = xbmcgui.ControlImage(bgPosX, bgPosY-btH, bgW, bgH, __path_img__ + 'bg.png')
        self.addControl(self.bg)
        
        # label
        self.label = xbmcgui.ControlLabel(btPosX, btPosY-btH-10, btW, btH, __lang__(32109), 'font13_title', '0xFF2D84CC', alignment=2)
        self.addControl(self.label)
        
        # label
        self.label = xbmcgui.ControlLabel(btPosX, btPosY-btH+20, btW, btH, str(lenFiles) + ' ' + __lang__(32110), 'font10_title', '0xFFFFFFFF', alignment=2)
        self.addControl(self.label)
        
        # list
        self.list = xbmcgui.ControlList(btPosX, btPosY, btW, btH*5+21, 'font13', '', '', 'button-focus.png', '', 0, 0, 20, 0, btH, 0)
        self.addControl(self.list)

        start = 0
        for file in self.files.values():
            start += 1
            m = re.match('w_([0-9]{4})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})_([0-9]+).json', file)
            l_date = str(start) + '. - ' + m.group(3) + '.' + m.group(2) + '.' + m.group(1) + ' ' + m.group(4) + ':' + m.group(5) + ':' + m.group(6) + ' - ' + m.group(7) + ' ' + __lang__(32105)
            self.list.addItem(l_date)
        self.setFocus(self.list)
            
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU or action == ACTION_STEP_BACK or action == ACTION_BACKSPACE or action == ACTION_NAV_BACK or action == KEY_BUTTON_BACK or action == ACTION_MOUSE_RIGHT_CLICK:
            self.close()
            
    def onControl(self, control):
        self.close()
        self.restore(self.list.getSelectedPosition())
            
    def restore(self, file):
        # get settings
        self.setMethod      = __addon__.getSetting('method')
        
        # read watched status from file
        f = xbmcvfs.File(__datapath__ + self.files[file], 'r')
        result = f.read()
        f.close()
        jsonRead = json.loads(result)
        
        toRestore = len(jsonRead['movies']) + len(jsonRead['episodes'])
        
        # confirm
        yesno = xbmcgui.Dialog().yesno(__addonname__, __lang__(32102) + ' ' + str(toRestore) + ' ' + __lang__(32105) + '?', nolabel=__lang__(32108).title(), yeslabel=__lang__(32111).title())
        if yesno == 0:
            return False
        
        if toRestore > 0:
            prog = Bar()
            prog.create(__lang__(32201), __addonname__ + ', ' + __lang__(32200))
        
            table = { 'movies': {}, 'episodes': {} }
            
            for t in table.keys():
                jsonGetWatched = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.Get' +  t.title() + '", "params": {"properties": ["title", "file"]}, "id": 1}')
                jsonGetWatched = unicode(jsonGetWatched, 'utf-8')
                jsonGetWatched = json.loads(jsonGetWatched)
                
                if 'result' in jsonGetWatched and t in jsonGetWatched['result']:
                    for m in jsonGetWatched['result'][t]:
                        table[t][m['file']] = {
                            'id': m[t[:-1] + 'id'],
                            'title': m['title']
                        }
            
            start = 0
            restored = 0
            for tab, val in jsonRead.items():
                for r, v in val.items():
                
                    start += 1
                    p = int((float(100) / float(toRestore)) * float(start))
                    
                    for a, b in table[tab].items():
                        
                        # by path
                        if '0' in self.setMethod and r == a:
                            prog.update(p, str(start) + ' / ' + str(toRestore) + ' - ' + b['title'])
                            xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.Set' + tab.title()[:-1] + 'Details", "params": {"playcount": ' + str(v['playcount']) + ', "lastplayed": "' + v['lastplayed'] + '", "' + tab[:-1] + 'id": ' + str(b['id']) + '}, "id": 1}')
                            restored += 1
                        
                        # by filename
                        if '1' in self.setMethod and ntpath.basename(r) == ntpath.basename(a):
                            prog.update(p, str(start) + ' / ' + str(toRestore) + ' - ' + b['title'])
                            xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.Set' + tab.title()[:-1] + 'Details", "params": {"playcount": ' + str(v['playcount']) + ', "lastplayed": "' + v['lastplayed'] + '", "' + tab[:-1] + 'id": ' + str(b['id']) + '}, "id": 1}')
                            restored += 1
                            
            prog.close()
            
            Debug().notify(__lang__(32106) + ' - ' + str(restored) + ' ' + __lang__(32105))
        else:
            Debug().notify(__lang__(32107))
        
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
            
class Debug:
    def debug(self, msg):
        if 'true' in __addon__.getSetting('debug'):
            xbmc.log('>>>> ' + __addonname__ + ' <<<< ' + msg)
    
    def notify(self, msg):
        if 'true' in __addon__.getSetting('notify'):
            xbmc.executebuiltin('Notification(' + __addonname__ + ', ' + msg.encode('utf-8') + ', 4000, ' + __icon__ + ')')

Start()
    