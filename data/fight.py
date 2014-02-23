"""Module: fight.py
Overview: Control flow for the game while in the FIGHT state.
Classes: Fight"""

import pygame as pg

from . import ships,starmap,status
from .globs import *

class Fight:
    def __init__(self):
        #Players, Statbars, and Starmap
        self.P1 = None
        self.P2 = None
        self.P1stat = None
        self.P2stat = None
        self.Players = (self.P1,self.P2)
        self.Starmap = None

        #flags and timers
        self.ready = False
        self.done  = False
        self.victory = None #Which player one the fight
        self.count = 0.0 #Counts time elapsed after a victory condition
        self.blink = False
        self.blink_timer = 0.0
        self.message = None #Message to display afteer victory condition met.
        self.nekey = False #Any key to continue.

    def set_up(self):
        """Creates the players and map when a fight begins.
        When ship selection is added the choices will be processed here."""
        self.P1 = ships.BlueWing([300,100],(50,50),(5,3),135)
        self.P2 = ships.Triple([450,200],(50,50),(5,3),-45)
        self.P2.keys = PLAYER2_DEFAULT
        self.P1stat = status.Statbar(self.P1)
        self.P2stat = status.Statbar(self.P2)
        self.Players = (self.P1,self.P2)
        self.Starmap = starmap.StarMap(GFX["myneb1"],(self.P1,self.P2))
        self.ready = True

    def fight_event(self,event):
        """An event loop for non player specific events during FIGHT state."""
        if self.nekey:
            """Press any key to continue."""
            if event.type == pg.KEYDOWN:
                self.done = True

    def process_collissions(self):
        """Updates all map objects and then based on their new locations, calculates
        all collissions that have taken place.  Any object that is found to collide with
        another is reset to its starting position that frame with newly calculated
        trajectory vector."""
        for thing in self.Starmap.collide_objects:
            #Update all objects before checking for collissions
            thing.update(self.Starmap.rect,self.Starmap.extra,self.Starmap.collide_objects)
        for thing in self.Starmap.collide_objects:
            #Check collissions on all objects
            thing.check_collissions(self.Starmap.collide_objects)
        for thing in self.Starmap.collide_objects:
            #If an object collided with another body, reset its position and change its vector
            if thing.collissions:
                thing.location = thing.old_loc[:]
                thing.vel_x = sum([item[0] for item in thing.collissions])
                thing.vel_y = sum([item[1] for item in thing.collissions])
                thing.collissions = []

    def add_remove(self,Surf):
        """Add and remove objects from the map as needed based on weapons fire,
        destruction of objects, and other events.  Then finally draw all items
        that still exist."""
        for thing in self.Starmap.collide_objects[:]:
            #Add and remove objects from map as necessary (weapons fire)
            if thing.is_ship and thing.go_prime:
                thing.primary(self.Starmap.collide_objects)
            if thing.is_ship and thing.go_second:
                thing.secondary(self.Starmap.collide_objects)
            if thing.done:
                self.Starmap.collide_objects.remove(thing)
            thing.draw(Surf,self.Starmap.rect,self.Starmap.extra)

    def show_stats(self):
        """Update stat bars and draw them."""
        self.P1stat.update()
        self.P2stat.update()
        SURFACE.blit(self.P1stat.image,(900,0))
        SURFACE.blit(pg.transform.flip(self.P2stat.image,True,False),(0,0))

    def check_victory(self):
        """Check if a player has been killed each frame."""
        if self.P1.dead_frame == 5 and not self.P2.dead:
            self.P2.sleep = True
            self.victory = "TWO"
            self.message = fixedsys.render("Player 2 is victorious!",1,(255,255,0))
            self.count = pg.time.get_ticks()
        elif self.P2.dead_frame == 5 and not self.P1.dead:
            self.P1.sleep = True
            self.victory = "ONE"
            self.message = fixedsys.render("Player 1 is victorious!",1,(255,255,0))
            self.count = pg.time.get_ticks()
        elif self.P2.dead_frame == 5 and self.P1.dead_frame == 5:
            self.victory = "BOTH"
            self.message = fixedsys.render("Mutually Assured Destruction!",1,(255,255,0))
            self.count = pg.time.get_ticks()

    def final_word(self):
        """Display victory message after a player is defeated."""
        if pg.time.get_ticks() - self.blink_timer > 1000/5.0:
            self.blink = False if self.blink else True
            self.blink_timer = pg.time.get_ticks()
        if pg.time.get_ticks() - self.count > 500:
            msg_rect = self.message.get_rect()
            msg_rect.center = SURFACE.get_rect().centerx,150
            SURFACE.blit(self.message,msg_rect)
            if pg.time.get_ticks() - self.count > 2000:
                if self.blink:
                    anymsg = fixedsys.render("-PRESS ANY KEY-",1,(255,255,0))
                    anymsg_rect = anymsg.get_rect()
                    anymsg_rect.center = SURFACE.get_rect().centerx,400
                    SURFACE.blit(anymsg,anymsg_rect)
                self.nekey = True

    def update(self,Surf):
        """Updater for screen during a FIGHT."""
        #If the fight has just begun, initialize first.
        if not self.ready:
            #Prepare players and map
            self.set_up()
        self.process_collissions()
        #Update and draw map.
        self.Starmap.update()
        self.Starmap.draw_bg()
        self.add_remove(Surf)
        self.show_stats()
        #Check victory conditions and blit messages as needed.
        if not self.victory:
            self.check_victory()
        else:
            self.final_word()