"""Module: title.py
Overview: Control flow for the game while in the TITLE state.
Classes: Title"""

import math,random
import pygame as pg

from . import bodies,starmap
from .globs import *

class Title:
    def __init__(self):
        self.offset = (-250,-150)
        self.choord = [0,0]
        self.back = pg.transform.scale(GFX["myneb1"],(1500,900))
        self.fore = GFXA["titlepic"]
        self.circ = 0.0
        self.timer = 0.0
        self.blink = False
        self.done = False
        self.image = pg.Surface((1000,600)).convert_alpha()

        self.Shipu = None
        self.Shipb = None

    def title_event(self,event):
        """Press any key to continue."""
        if event.type == pg.KEYDOWN:
            self.done = True

    def update(self,Surf):
        """Draw everything in its time in its place."""
        self.get_choords()
        self.fly_by()
        targ = (self.offset[0]+self.choord[0],self.offset[1]+self.choord[1])
        self.image.blit(self.back,targ)
        self.image.blit(self.fore,(0,0))
        if self.Shipu:
            self.image.blit(self.Shipu.image,self.Shipu.location)
        if self.Shipb:
            self.image.blit(self.Shipb.image,self.Shipb.location)
        if pg.time.get_ticks() - self.timer > 1000/5.0:
            self.blink = False if self.blink else True
            self.timer = pg.time.get_ticks()
        if self.blink:
            self.image.blit(fixedsys.render("-PRESS ANY KEY-",1,(255,255,0)),(475,485))
        Surf.blit(self.image,(0,0))

    def get_choords(self):
        """Get coordinates for the starscape in the background."""
        radius = 150
        self.choord[0] = radius*math.cos(math.radians(self.circ))
        self.choord[1] = radius*math.sin(math.radians(self.circ))
        self.circ += 2 if self.circ < 358 else -self.circ

    def fly_by(self):
        """Animates the ships flying on the title screen."""
        if not self.Shipu:
            self.Shipu = bodies.Player([-100,150],(50,50),(5,3),90+math.degrees(math.atan2(-30,90)))
            self.Shipu.initial = GFX[random.choice(SHIPS)]
            self.Shipu.zoom = 0.5
            self.Shipu.make_image()
            self.Shipu.vel_x,self.Shipu.vel_y = 6,-2
            self.Shipu.speed = math.hypot(self.Shipu.vel_x,self.Shipu.vel_y)
        self.Shipu.translate()
        self.Shipu.move_it()
        if self.Shipu.location[1] < -self.Shipu.rect.height:
            self.Shipu = None
        if not self.Shipb:
            self.Shipb = bodies.Player([1000,200],(50,50),(5,3),90+math.degrees(math.atan2(30,-90)))
            self.Shipb.initial = GFX[random.choice(SHIPS)]
            self.Shipb.zoom = 0.5
            self.Shipb.make_image()
            self.Shipb.vel_x,self.Shipb.vel_y = -6,2
            self.Shipb.speed = math.hypot(self.Shipb.vel_x,self.Shipb.vel_y)
        self.Shipb.translate()
        self.Shipb.move_it()
        if self.Shipb.location[1] > 600:
            self.Shipb = None


