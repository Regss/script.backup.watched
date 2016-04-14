# -*- coding: utf-8 -*-

import xbmcaddon
import xbmcgui
import xbmc
import os

__addon__               = xbmcaddon.Addon()
__addon_id__            = __addon__.getAddonInfo('id')
__addonpath__           = xbmc.translatePath(__addon__.getAddonInfo('path'))
__lang__                = __addon__.getLocalizedString
__path_img__            = os.path.join(__addonpath__, 'resources', 'media' )

ACTION_PREVIOUS_MENU        = 10
ACTION_STEP_BACK            = 21
ACTION_NAV_BACK             = 92
ACTION_MOUSE_RIGHT_CLICK    = 101
ACTION_BACKSPACE            = 110
KEY_BUTTON_BACK             = 275
BACK_GROUP = [ACTION_PREVIOUS_MENU, ACTION_STEP_BACK, ACTION_NAV_BACK, ACTION_MOUSE_RIGHT_CLICK, ACTION_BACKSPACE, KEY_BUTTON_BACK]

ACTION_MOVE_UP              = 3
ACTION_MOVE_DOWN            = 4

class DIALOG:
    def start(self, title, buttons):
        returned = None
        display = SHOW(title, buttons, returned)
        display.doModal()
        returned = display.returned
        del display
        return returned
        
class SHOW(xbmcgui.WindowDialog):
    
    def __init__(self, title, buttons, returned):
        # set window property to true
        xbmcgui.Window(10000).setProperty(__addon_id__ + '_running', 'True')
        
        # set vars
        self.returned = returned
        self.start = 0
        self.buttonName = buttons
        self.button = []
        
        # create window
        bgResW = 460
        bgResH = (50 * len(self.buttonName)) + 70
        bgPosX = (1280 - bgResW) / 2
        bgPosY = (720 - bgResH) / 2
        self.bg = xbmcgui.ControlImage(bgPosX, bgPosY, bgResW, bgResH, __path_img__+'//bg.png')
        self.addControl(self.bg)
        self.labelTitle = xbmcgui.ControlLabel(bgPosX+20, bgPosY+22, bgResW-40, bgResH-40, '[B]' + title + '[/B]', 'font14', '0xFFE60000',  alignment=2)
        self.addControl(self.labelTitle)
        
        # create button list
        self.starLeft = bgPosX+40
        self.starTop = bgPosY+60
        for i in range(len(self.buttonName)):
            self.button.append(xbmcgui.ControlButton(self.starLeft, self.starTop+(i*50), bgResW-80, 40, self.buttonName[i], alignment=6))
            self.addControl(self.button[i])
        self.setFocus(self.button[0])
        
    def onAction(self, action):
        if action in BACK_GROUP:
            self.close()
            
        if action == ACTION_MOVE_UP:
            if self.start > 0:
                self.start = self.start - 1
            self.setFocus(self.button[self.start])
            
        if action == ACTION_MOVE_DOWN:
            if self.start < len(self.buttonName) - 1:
                self.start = self.start + 1
            self.setFocus(self.button[self.start])
            
    def onControl(self, control):
        for i in range(len(self.buttonName)):
            if control == self.button[i]:
                self.close()
                self.returned = i
                