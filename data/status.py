"""Module: status.py
Overview: Controls the updating of the stat bar during fights.
Classes: Statbar"""

import pygame as pg

from .globs import *

GREEN  = (0,255,0)
YELLOW = (255,255,0)
ORANGE = (255,150,0)
RED    = (255,0,0)
BLUE   = (0,100,255)

COLORS = (GREEN,YELLOW,ORANGE,RED,BLUE)

class Statbar:
    def __init__(self,Player):
        self.myplay = Player
        self.image = pg.Surface((100,600)).convert()
        self.l_color = GREEN
        self.e_color = GREEN
        l_height = 4+self.myplay.max_life*4
        e_height = 4+self.myplay.max_energy*4
        self.L_rect = pg.Rect(13,101-l_height,34,l_height)
        self.E_rect = pg.Rect(53,101-e_height,34,e_height)
        self.blink = False
        self.blink_time = 0.0

    def update(self):
        """Update statbar image."""
        self.l_color = self.get_color(self.myplay.life,self.myplay.max_life)
        self.e_color = self.get_color(self.myplay.energy,self.myplay.max_energy)
        self.blink_it()
        energy = self.paint_stat(self.E_rect,self.myplay.energy,BLUE)
        life   = self.paint_stat(self.L_rect,self.myplay.life,self.l_color)
        self.image.blit(GFX["statbar"],(0,0))
        self.image.blit(energy,self.E_rect)
        self.image.blit(life,self.L_rect)
        self.ind_lights()

    def paint_stat(self,rect,stat,color):
        """Prepare the stat display (life/energy)."""
        surf = pg.Surface(rect.size)
        surf.fill((0))
        for point in range(int(stat)):
            surf.fill(color,(4,rect.height-5-4*point,26,2))
        return surf

    def get_color(self,stat,maxy):
        """Change color based on percent of max stat."""
        if   stat > maxy*0.75:
            color = GREEN
        elif stat > maxy*0.5:
            color = YELLOW
        elif stat > maxy*0.25:
            color = ORANGE
        else:
            color = RED
        return color

    def blink_it(self):
        """Timer for indicator lights."""
        if pg.time.get_ticks() - self.blink_time > 1000/3.0:
            self.blink = False if self.blink else True
            self.blink_time = pg.time.get_ticks()

    def ind_lights(self):
        """Flashing indicator lights."""
        self.blink_it()
        l_ind = COLORS.index(self.l_color)
        e_ind = COLORS.index(self.e_color)
        if e_ind == 0: e_ind = 4
        self.image.blit(GFXA["indicators"],(16,9),(0,21*l_ind,28,21))
        self.image.blit(GFXA["indicators"],(56,9),(0,21*e_ind,28,21))
        if self.blink:
            self.image.blit(GFXA["indicators"],(16,9),(0,21*l_ind,28,21))
            self.image.blit(GFXA["indicators"],(56,9),(0,21*e_ind,28,21))





