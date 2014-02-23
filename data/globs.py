"""Module: globs.py
Overview: Display initialization, global constants, and graphic/font loading.
Functions: getgraphics(directory,alpha=False)"""

import os
import pygame as pg

os.environ['SDL_VIDEO_CENTERED'] = '1'

FPS = 64.0              #Global frames per second (desired)
SCREENSIZE = (1000,600) #Global screen size
PLAYSIZE   = (800,600)  #Global size of play area
OFFSET     = (100,0)    #Global location of play area within screen
SURFACE = pg.display.set_mode(SCREENSIZE)
pg.init()

#Fonts
basicFont = pg.font.Font(os.path.join('graphics','ArialNb.TTF'),48)
fixedsys  = pg.font.Font(os.path.join('graphics','Fixedsys500c.ttf'),60)

#Player one controls
PLAYER1_DEFAULT = {"thrust" :pg.K_UP,
                   "reverse":pg.K_DOWN,
                   "right"  :pg.K_RIGHT,
                   "left"   :pg.K_LEFT,
                   "prime"  :pg.K_p,
                   "second" :pg.K_o}
#Player two controls
PLAYER2_DEFAULT = {"thrust" :pg.K_w,
                   "reverse":pg.K_s,
                   "right"  :pg.K_d,
                   "left"   :pg.K_a,
                   "prime"  :pg.K_SPACE,
                   "second" :pg.K_LSHIFT}

def getgraphics(directory,alpha=False):
    """Returns a dictionary of all the image files in a directory.
    Dictionary keys are image names minus their file extensions."""
    dirlist = os.listdir(directory)
    graphic = {}
    for graf in dirlist:
        if graf[-3:] in ("png","jpg"):
            if not alpha:
                graphic[graf[:-4]] = pg.image.load(os.path.join(directory,graf)).convert()
                graphic[graf[:-4]].set_colorkey((255,0,255))
            else:
                graphic[graf[:-4]] = pg.image.load(os.path.join(directory,graf)).convert_alpha()
    return graphic

GFX  = getgraphics("graphics")
GFXA = getgraphics("graphalpha",True)

SHIPS = ("intrepid_alt","wing_blue","tripple","ship_blue","ship_red","ship_up")###