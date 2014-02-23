"""Module: main.py
Overview: Primary control flow for entire game.
Classes: Control"""

import os,sys #used for os.environ and sys.exit

import pygame as pg #lazy but better than destroying namespace

from . import fight,title
from .globs import *

class Control:
    def __init__(self):
        self.showfps = False
        self.myclock = pg.time.Clock()
        self.state = "TITLE"

        self.Titler  = title.Title()
        self.Fighter = fight.Fight()

    def quit_game(self):
        """Call this anytime the program needs to close cleanly."""
        pg.quit();sys.exit()

    def control_events(self):
        """Our event loop goes here."""
        keys = pg.key.get_pressed() ##
        for event in pg.event.get():
            keys = pg.key.get_pressed()
            if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
                 self.quit_game()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_F5:
                    self.showfps = True if not self.showfps else False
            elif event.type == pg.KEYUP:  pass

            if self.state == "TITLE":
                self.Titler.title_event(event)
            elif self.state == "FIGHT":
                self.Fighter.fight_event(event)
                try: #exception probably won't be necessary eventually
                    for Player in self.Fighter.Players:
                        Player.events(keys)
                except AttributeError:
##                    print("Ships not initialized yet.")
                    pass

    def main(self):
        """Control flow for everything"""
        while 1:
            self.control_events()
            if self.state == "TITLE":
                self.Titler.update(SURFACE)
                if self.Titler.done:
                    self.state = "FIGHT"
            elif self.state == "FIGHT":
                self.Fighter.update(SURFACE)
                if self.Fighter.done:
                    self.state = "TITLE"
                    self.__init__()###

            if self.showfps:
                SURFACE.blit(basicFont.render(str(self.myclock.get_fps()),1,(255,255,255)),(900,550))
            self.myclock.tick(FPS)
            pg.display.update()
