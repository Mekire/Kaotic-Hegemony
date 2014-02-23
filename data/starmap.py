"""Module: starmap.py
Overview: The processing for the map scrolling and background.
Classes: StarMap"""

import math
import pygame as pg

from .globs import *

class StarMap:
    """Combat map for two players.  Controls zoom changes and scrolling
    background logic."""
    def __init__(self,background,Players):
        self.bg = background
        self.sector = None
        self.P1 = Players[0]
        self.P2 = Players[1]
        self.zoom = 4.0

        self.center = (0,0)
        self.max_x = 0
        self.max_y = 0

        self.rect = pg.Rect((0,0),PLAYSIZE)
        self.extra = 0,0

        self.collide_objects = [self.P1,self.P2] #list of objects on the map that can collide

    def get_distance(self):
        """component distance of the players"""
        self.max_x = (max(self.P1.location[0],self.P2.location[0])
                     -min(self.P1.location[0],self.P2.location[0]))
        self.max_y = (max(self.P1.location[1],self.P2.location[1])
                     -min(self.P1.location[1],self.P2.location[1]))

    def get_center(self):
        """Finds the point in the middle of the two players.  This will be the
        center of the screen unless one of the players is near an edge."""
        if not self.P1.dead and self.P2.dead_frame == 5:
            centerx,centery = self.P1.location
        elif self.P1.dead_frame == 5 and not self.P2.dead:
            centerx,centery = self.P2.location
        else:
            centerx = min(self.P1.location[0],self.P2.location[0])+self.max_x/2.0
            centery = min(self.P1.location[1],self.P2.location[1])+self.max_y/2.0
        if self.zoom == 1.0:
            if centerx < PLAYSIZE[0]/8: centerx = PLAYSIZE[0]/8
            elif centerx > PLAYSIZE[0]-PLAYSIZE[0]/8: centerx = PLAYSIZE[0]-PLAYSIZE[0]/8
            if centery < PLAYSIZE[1]/8: centery = PLAYSIZE[1]/8
            elif centery > PLAYSIZE[1]-PLAYSIZE[1]/8: centery = PLAYSIZE[1]-PLAYSIZE[1]/8
        elif self.zoom == 2.0:
            if centerx < PLAYSIZE[0]/4: centerx = PLAYSIZE[0]/4
            elif centerx > PLAYSIZE[0]-PLAYSIZE[0]/4: centerx = PLAYSIZE[0]-PLAYSIZE[0]/4
            if centery < PLAYSIZE[1]/4: centery = PLAYSIZE[1]/4
            elif centery > PLAYSIZE[1]-PLAYSIZE[1]/4: centery = PLAYSIZE[1]-PLAYSIZE[1]/4
        self.center = centerx,centery

    def get_zoom(self):
        """Finds the required zoom based on how far apart players are."""
        if self.max_x > PLAYSIZE[0]/2 or self.max_y > PLAYSIZE[1]/2:
            self.zoom = 4.0
        elif self.max_x > PLAYSIZE[0]/4 or self.max_y > PLAYSIZE[1]/4:
            self.zoom = 2.0
        else:
            self.zoom = 1.0
        if 5 in (self.P1.dead_frame,self.P2.dead_frame) and not (self.P1.dead,self.P2.dead) == (True,True):
            self.zoom = 1.0
        self.get_center()

    def get_extra(self):
        """Finds extra sliver offset if necessary. Hackish garbage."""
        if self.zoom == 1.0:
            self.extra = -int(math.modf(self.center[0])[0]*4),-int(math.modf(self.center[1])[0]*4)
        elif self.zoom == 2.0:
            self.extra = -int(math.modf(self.center[0])[0]*2),-int(math.modf(self.center[1])[0]*2)
        else:
            self.extra = (0,0)

    def get_bg_sector(self):
        """Finds the section of our background image to use."""
        if self.zoom == 4.0:
            self.rect = pg.Rect((0,0),PLAYSIZE)
        elif self.zoom == 2.0:
            self.rect = pg.Rect(self.center[0]-PLAYSIZE[0]/4,self.center[1]-PLAYSIZE[1]/4,
                                PLAYSIZE[0]/2,PLAYSIZE[1]/2)
        else:
            self.rect = pg.Rect(self.center[0]-PLAYSIZE[0]/8,self.center[1]-PLAYSIZE[1]/8,
                                PLAYSIZE[0]/4,PLAYSIZE[1]/4)
        self.sector = self.bg.subsurface(self.rect)

    def update(self):
        """Update function for the map called once per frame."""
        self.get_distance()
        self.get_zoom()
        self.get_bg_sector()
        self.get_extra()
        for thing in self.collide_objects:
            thing.change_zoom(self.zoom,self.rect,self.extra)

    def draw_bg(self):
        """Draws our map background to the surface; scaling when necessary."""
        #The business with the extra pixels and slivers is a bit hackish but fine for now I suppose.
        #This necessity is mandated by the fact that to scroll smoothly the background needs to move
        #fractions of pixels relative to the original zoomed out image.
        if self.zoom == 1.0:
            temp = pg.transform.scale(self.sector,PLAYSIZE)
            SURFACE.blit(temp,(OFFSET[0]+self.extra[0],OFFSET[1]+self.extra[1]))
            if self.extra[0]:
                try:
                    sliv_rect_v = (self.rect.x+PLAYSIZE[0]/4,self.rect.y,1,PLAYSIZE[1]/4+1)
                    sliverv = pg.transform.scale(self.bg.subsurface(sliv_rect_v),(4,PLAYSIZE[1]+4))
                except ValueError:
                    sliv_rect_v = (self.rect.x+PLAYSIZE[0]/4,self.rect.y,1,PLAYSIZE[1]/4)
                    sliverv = pg.transform.scale(self.bg.subsurface(sliv_rect_v),(4,PLAYSIZE[1]))
                SURFACE.blit(sliverv,(OFFSET[0]+PLAYSIZE[0]+self.extra[0],OFFSET[1]+self.extra[1]))
            if self.extra[1]:
                try:
                    sliv_rect_h = (self.rect.x,self.rect.y+PLAYSIZE[1]/4,PLAYSIZE[0]/4+1,1)
                    sliverh = pg.transform.scale(self.bg.subsurface(sliv_rect_h),(PLAYSIZE[0]+4,4))
                except ValueError:
                    sliv_rect_h = (self.rect.x,self.rect.y+PLAYSIZE[1]/4,PLAYSIZE[0]/4,1)
                    sliverh = pg.transform.scale(self.bg.subsurface(sliv_rect_h),(PLAYSIZE[0],4))
                SURFACE.blit(sliverh,(OFFSET[0]+self.extra[0],OFFSET[1]+PLAYSIZE[1]+self.extra[1]))
        elif self.zoom == 2.0:
            temp = pg.transform.scale(self.sector,PLAYSIZE)
            SURFACE.blit(temp,(OFFSET[0]+self.extra[0],OFFSET[1]+self.extra[1]))
            if self.extra[0]:
                try:
                    sliv_rect_v = (self.rect.x+PLAYSIZE[0]/2,self.rect.y,1,PLAYSIZE[1]/2+1)
                    sliverv = pg.transform.scale(self.bg.subsurface(sliv_rect_v),(2,PLAYSIZE[1]+2))
                except ValueError:
                    sliv_rect_v = (self.rect.x+PLAYSIZE[0]/2,self.rect.y,1,PLAYSIZE[1]/2)
                    sliverv = pg.transform.scale(self.bg.subsurface(sliv_rect_v),(2,PLAYSIZE[1]))
                SURFACE.blit(sliverv,(OFFSET[0]+PLAYSIZE[0]+self.extra[0],OFFSET[1]+self.extra[1]))
            if self.extra[1]:
                try:
                    sliv_rect_h = (self.rect.x,self.rect.y+PLAYSIZE[1]/2,PLAYSIZE[0]/2+1,1)
                    sliverh = pg.transform.scale(self.bg.subsurface(sliv_rect_h),(PLAYSIZE[0]+2,2))
                except ValueError:
                    sliv_rect_h = (self.rect.x,self.rect.y+PLAYSIZE[1]/2,PLAYSIZE[0]/2,1)
                    sliverh = pg.transform.scale(self.bg.subsurface(sliv_rect_h),(PLAYSIZE[0],2))
                SURFACE.blit(sliverh,(OFFSET[0]+self.extra[0],OFFSET[1]+PLAYSIZE[1]+self.extra[1]))
        else:
            SURFACE.blit(self.sector,OFFSET)