"""Module: ships.py
Overview: Specific types of ships that inherit from bodies.Player
Classes: BlueWing(bodies.Player), Triple(bodies.Player)"""
#The class Pulse is also currently here but will be moved later.

import math
import pygame as pg

from . import bodies
from .globs import *

class BlueWing(bodies.Player):
    def __init__(self,location,size,speed,angle):
        bodies.Player.__init__(self,location,size,speed,angle)
        self.initial = GFX["wing_blue"]
        self.make_image()

        self.prime_speed = 7.0

        self.max_life   = self.life   = 8
        self.max_energy = self.energy = 10
        self.accel = 0.05

        self.prim_cost   = 1
        self.second_cost = 0.0
        self.regen = 300

    def fire_prime(self,objects):
        objects.append(Pulse(self,self.location[:],self.rect.size,(self.vel_x,self.vel_y),-self.angle))

class Triple(bodies.Player):
    def __init__(self,location,size,speed,angle):
        bodies.Player.__init__(self,location,size,speed,angle)
        self.prime_speed = 3.0

        self.prim_cost   = 5
        self.second_cost = 0.0
        self.regen = 500

        self.initial = GFX["tripple"]
        self.make_image()

    def fire_prime(self,objects):
        Shot = Pulse(self,self.location[:],self.rect.size,(self.vel_x,self.vel_y),-self.angle)
        Shot.set_basics(300,5,3.0,GFXA["tri_pulse"])
        objects.append(Shot)

class Pulse(bodies.Body):
    def __init__(self,origin,location,size,speed,angle):
        bodies.Body.__init__(self,location,size,speed,angle)
        self.done = False
        self.start = location[:]
        self.range = 100
        self.damage = 1
        self.origin = origin
        self.hit_origin = False #Can your own shots hit you?
        self.hit_self   = False #Can your shots hit each other?

        self.mass = 0.0
        self.rad_speed = 3.0
        self.play_speed = speed

        self.set_speed()
        self.initial = GFXA["blue_pulse"]
        self.make_image()

##        #mess around with helix bullets
##        self.left = True
##        self.rot_speed = 15

    def set_basics(self,rnge,damage,speed,image):
        self.range = rnge
        self.damage = damage
        self.rad_speed = speed
        self.set_speed()
        self.initial = image
        self.make_image()

    def set_speed(self):
        ang = math.radians(self.calc_angle)
        self.vel_x = self.play_speed[0] + self.rad_speed*math.cos(ang)
        self.vel_y = self.play_speed[1] + self.rad_speed*math.sin(ang)
        self.speed = math.hypot(self.vel_x,self.vel_y)

    def get_distance(self):
        """Calculate distance projectile has travelled."""
        max_x = (max(self.start[0],self.location[0])
                -min(self.start[0],self.location[0]))
        max_y = (max(self.start[1],self.location[1])
                -min(self.start[1],self.location[1]))
        return math.hypot(max_x,max_y)

    def check_collissions(self,objects):
        for obj in objects:
            if obj is not self:
                offset = (-self.rect.x+obj.rect.x,-self.rect.y+obj.rect.y)
                if self.mask.overlap_area(obj.mask,offset) and self.valid_target(obj):
##                    print("Boom!")
                    if obj.life > 0:
                        obj.life -= self.damage
                    self.done = True

    def valid_target(self,obj):
        """Decides whether the object is a valid collission target."""
        #Not positive this is working as intended.
        hitit = True
        if self.origin is obj and not self.hit_origin:
            hitit = False
        elif obj.origin:
            if self.origin is obj.origin and not self.hit_self:
                hitit = False
        return hitit

    def update(self,maprect,extra,collide):
        bodies.Body.update(self,maprect,extra,collide)
        if self.get_distance() >= self.range:
            self.done = True