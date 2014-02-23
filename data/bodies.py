"""Module: bodies.py
Overview: Prototype classes for general bodies in space including ships.
Classes: _Collission, Body(_Collission), Player(Body)
Functions: shrink_tri(adj,op,size)"""

import math
import pygame as pg

from .globs import *

class _Collission:
    """Seperated this into its own class for purposes of organization.  Other objects
    will inherit from this class if they need these functions.  Do not create
    an instance of this class."""
    def check_collissions(self,objects):
        """This function together with get_normal and get_components calculate
        collissions between major screen objects and calculate rebound trajectories.
        Theoretically momentum and energy are conserved but outcomes are still twitchy
        at times."""
        for obj in objects:
            if obj is not self:
                offset = (-self.rect.x+obj.rect.x,-self.rect.y+obj.rect.y)
                if self.mask.overlap_area(obj.mask,offset):
                    if obj.mass:
                        if self.wrapped or obj.wrapped:
##                            print("wrapped collission")
                            self.collissions.append(self.abnormal_collission(obj))
                        else:
##                            print("normal collission")
                            unit_norm,unit_tang = self.get_normal(obj,offset)
                            newspeed = self.get_components(obj,unit_norm,unit_tang)
                            self.collissions.append(newspeed)

    def get_normal(self,other,offset):
        """Calculate the normal vector between our object and other.
        In general this gives the most realistic collissions, but depending on
        the shapes of the colliding objects, it can also return problematic
        results."""
        #Create a double check function that reverts to simple collissions if
        #the trajectory given by this function fails to avoid collission with
        #the same object next frame.
        dx = (self.mask.overlap_area(other.mask,(offset[0]+1,offset[1]))
             -self.mask.overlap_area(other.mask,(offset[0]-1,offset[1])))
        dy = (self.mask.overlap_area(other.mask,(offset[0],offset[1]+1))
             -self.mask.overlap_area(other.mask,(offset[0],offset[1]-1)))
        mag = float(math.hypot(dx,dy))
        unit_normal = (dx/mag,dy/mag)
        unit_tang   = (-dy/mag,dx/mag)
        return unit_normal,unit_tang

    def get_components(self,obj,normal,tangent):
        """Find new normal component of velocity.  Tangential component remains
        unchanged."""
        perp = sum([a*b for a,b in zip((self.vel_x,self.vel_y),normal)])
        perp_other = sum([a*b for a,b in zip((obj.vel_x,obj.vel_y),normal)])
        prll = sum([a*b for a,b in zip((self.vel_x,self.vel_y),tangent)])
        newperp = (perp*(self.mass-obj.mass)+2*obj.mass*perp_other)/(self.mass+obj.mass)
        vect = newperp*normal[0]+prll*tangent[0],newperp*normal[1]+prll*tangent[1]
        return vect

    def abnormal_collission(self,obj):
        """Assume all velocity is normal to collission if collission occurs from
        a body wrapping the map.  If it proves to be an issue, all collissions
        could be handled this way."""
        newx = (self.vel_x*(self.mass-obj.mass)+2*obj.mass*obj.vel_x)/(self.mass+obj.mass)
        newy = (self.vel_y*(self.mass-obj.mass)+2*obj.mass*obj.vel_y)/(self.mass+obj.mass)
        return (newx,newy)

class Body(_Collission):
    """This class will represent any solid body in space.
    Arguments are location [x,y], size (x_size,y_size),
    the max speed (radial,angular) in (pixels/frame,degrees/frame), and
    starting angle (measured clockwise with 0 pointing straight up)."""
    def __init__(self,location,size,max_speed,angle):
        self.location = location
        self.old_loc  = location
        self.rect = pg.Rect((location,size))
        #speed is of the form (max radial velocity,angular velocity)
        self.speed = max_speed[0]/4.0
        self.accel = 0.025
        self.mass = 5.0
        self.rot_speed = max_speed[1]

        self.zoom = 4.0
        self.done = False    #Are we finished doing whatever we were created for?
        self.origin = None   #Where did I come from?
        self.is_ship = False #Does this body represent a ship?

        self.dead = False #No, I'm not dead yet.
        self.dead_frame = 0
        self.dead_timer = 0.0

        #angle stuff
        self.angle = -angle
        self.calc_angle = -90 - self.angle
        self.old_rot = (self.angle,self.calc_angle)

        #flags for key inputs
        self.left    = False
        self.right   = False
        self.thrust  = False
        self.reverse = False

        #velocities
        self.vel_x,self.vel_y = 0,0
        self.collissions = [] #List of velocity vectors from collissions.
        self.wrapped = False #Did the player wrap the map this frame?

        #set up the image
        self.initial = GFX["ship_up"] #This will change
        self.make_image()

        self.life = 1.0

    def make_image(self):
        """Takes our initial image and rotates it to the correct angle.
        Rotation can be a destructive process so always rotate the
        initial image to avoid cumulative damage.
        The size of the image rect will change after rotating, so set
        the new image rect to have the same center as the original."""
        #I should probably change to pre-rendered sprite rotations both for
        #purposes of image quality and processing.
        mycenter = self.rect.center
        self.image = pg.transform.scale(self.initial,(int(self.initial.get_rect().width//self.zoom),
                                                      int(self.initial.get_rect().height//self.zoom)))
        self.image = pg.transform.rotate(self.image,self.angle)
        self.rect = self.image.get_rect(center=mycenter)
        self.mask = pg.mask.from_surface(self.image)

    def change_zoom(self,zoom,maprect,extra):
        """Changes the zoom and remakes images and masks."""
        if self.zoom != zoom:
            self.zoom = zoom
            self.make_image()
            self.position(maprect,extra)

    def rotate(self):
        """Applies rotations. Note that the pygame rotation function
        rotates in the oposite direction we need for our trig functions.
        Fun."""
        self.old_rot = (self.angle,self.calc_angle)
        if self.left:
            self.angle += self.rot_speed
            self.calc_angle -= self.rot_speed
        if self.right:
            self.angle -= self.rot_speed
            self.calc_angle += self.rot_speed

    def translate(self):
        """Controls changes in thrust.  The maximum speed is limited using the
        shrink_tri function."""
        ang = math.radians(self.calc_angle)
        pol_x = self.speed*math.cos(ang)
        pol_y = self.speed*math.sin(ang)
        if self.thrust:
            self.vel_x+=pol_x*self.accel
            self.vel_y+=pol_y*self.accel
        elif self.reverse:
            self.vel_x-=pol_x*(self.accel/2.0)
            self.vel_y-=pol_y*(self.accel/2.0)
        self.vel_x,self.vel_y = shrink_tri(self.vel_x,self.vel_y,self.speed)

    def wrap_map(self):
        """A pseudo double mobius strip."""
        #This presents issues with collissions when wrapping dictates that
        #an object appear somewhere already occupied by an object.
        if self.location[0] < 0:
            if self.location[1] < 0:
                self.location = [PLAYSIZE[0],PLAYSIZE[1]]
            elif self.location[1] > PLAYSIZE[1]:
                self.location = [PLAYSIZE[0],0]
            else:
                self.location = [PLAYSIZE[0],PLAYSIZE[1]-self.location[1]]
            self.wrapped = True
        elif self.location[0] > PLAYSIZE[0]:
            if self.location[1] > PLAYSIZE[1]:
                self.location = [0,0]
            elif self.location[1] < 0:
                self.location = [0,PLAYSIZE[1]]
            else:
                self.location = [0,PLAYSIZE[1]-self.location[1]]
            self.wrapped = True
        if self.location[1] < 0:
            self.location = [PLAYSIZE[0]-self.location[0],PLAYSIZE[1]]
            self.wrapped = True
        elif self.location[1] > PLAYSIZE[1]:
            self.location = [PLAYSIZE[0]-self.location[0],0]
            self.wrapped = True

    def move_it(self):
        """Updates location based on current velocity.  This location is to
        scale with the exact location at the furthest out zoom"""
        self.old_loc = self.location[:]
        self.location[0] += self.vel_x
        self.location[1] += self.vel_y

    def update(self,maprect,extra,collide):
        """update function called every frame"""
        if self.life <= 0:
            self.dead = True
            self.mask.clear()
        if not self.dead:
            if self.right or self.left:
                self.rotate()
                self.make_image()
                for obj in collide:
                    if obj is not self:
                        offset = (-self.rect.x+obj.rect.x,-self.rect.y+obj.rect.y)
                        if self.mask.overlap_area(obj.mask,offset):
                            self.angle,self.calc_angle = self.old_rot
                            self.make_image()
            if self.thrust or self.reverse:
                self.translate()
            self.move_it()
            self.wrap_map()
            self.position(maprect,extra)
        else:
            self.dying()

    def draw(self,Surface,maprect,extra):
        """Calculates the ships location on the screen with respect to zoom and
        draws it to the screen."""
        self.wrap_map()
        self.position(maprect,extra)
        Surface.blit(self.image,(OFFSET[0]+self.rect.x,OFFSET[1]+self.rect.y))
        self.wrapped = False #Where else, where else.
    def position(self,maprect,extra):
        """Calculate the relativistic position in the current map sector."""
        if self.zoom == 4.0:
            self.rect.center = self.location
        elif self.zoom == 2.0:
            self.rect.center = ((self.location[0]-maprect.x)*2+extra[0],(self.location[1]-maprect.y)*2+extra[1])
        elif self.zoom == 1.0:
            self.rect.center = ((self.location[0]-maprect.x)*4+extra[0],(self.location[1]-maprect.y)*4+extra[1])

    def dying(self):
        print("Blargh!! Dead.")
        pass

class Player(Body):
    """This class will represent our user controlled characters."""
    def __init__(self,location,size,speed,angle):
        Body.__init__(self,location,size,speed,angle)
        #player keys (default set for player-one)
        self.keys = PLAYER1_DEFAULT
        self.ai = False
        self.sleep = False
        self.is_ship = True

        self.max_life   = self.life   = 16
        self.max_energy = self.energy = 16

        #ability energy cost
        self.prim_cost   = 0
        self.second_cost = 0
        #energy regen speed (milliseconds per regen)
        self.regen   = 300
        self.regen_timer = 0.0
        #rate of fire and timer
        self.prime_speed = 7.0
        self.prime_time  = 0.0
        self.second_speed = 3.0
        self.second_time  = 0.0
        #flags for primary and secondary activation
        self.go_prime  = False
        self.go_second = False

    def events(self,keys):
        """The effect of user keys defined here."""
        if not self.sleep:
            #rotations
            self.right = True if keys[self.keys["right"]] else False
            self.left  = True if keys[self.keys["left"]]  else False
            #thrust and reverse
            self.thrust  = True if keys[self.keys["thrust"]]  else False
            self.reverse = True if keys[self.keys["reverse"]] else False
            #Using primary and secondary abilities
            self.go_prime  = True if keys[self.keys["prime"]]  else False
            self.go_second = True if keys[self.keys["second"]]  else False

    def update(self,maprect,extra,collide):
        Body.update(self,maprect,extra,collide)
        self.regen_energy()

    def primary(self,arg):
        """Check if primary can be used and if so update timers and energy accordingly."""
        if self.energy - self.prim_cost >= 0:
            if pg.time.get_ticks() - self.prime_time >= 1000/self.prime_speed:
                self.fire_prime(arg)
                self.prime_time = pg.time.get_ticks()
                self.energy -= self.prim_cost
    def fire_prime(self,arg):
        """Place holder for primary ability function."""
        print("Firing my laser.")

    def secondary(self,arg):
        """Check if secondary can be used and if so update timers and energy accordingly."""
        if self.energy - self.second_cost >= 0:
            if pg.time.get_ticks() - self.second_time >= 1000/self.second_speed:
                self.fire_second(arg)
                self.second_time = pg.time.get_ticks()
                self.energy -= self.second_cost
    def fire_second(self,arg):
        """Place holder for secondary ability function."""
        print("Doing something incredibly unique.")

    def regen_energy(self):
        """Regenerates ship's energy at prescribed speed."""
        if self.energy < self.max_energy and not (self.go_prime or self.go_second):
            if pg.time.get_ticks() - self.regen_timer >= self.regen:
                self.energy += 1
                self.regen_timer = pg.time.get_ticks()

    def dying(self):
        """Animates the player exploding on death.
        Explosion animation will be improved later; placeholder for now."""
        if pg.time.get_ticks() - self.dead_timer > 1000/7.0 and self.dead_frame != 5:
            if self.dead_frame < 4:
                a,b = self.initial.get_rect().center
                sub = pg.transform.scale(GFX["boom"].subsurface((50*self.dead_frame,0,50,50)),(80,80))
                self.initial = self.initial.copy()
                self.initial.blit(sub,(a-40,b-40))
                self.make_image()
                self.dead_frame += 1
                self.dead_timer = pg.time.get_ticks()
            else:
                self.initial.fill((255,0,255))
                self.image.fill((255,0,255))
                self.dead_frame = 5

################################################################################
def shrink_tri(adj,op,size):
    """When given the sides of a right-triangle, adj and op,
    this function will scale the triangle so that the hypotenus
    is reduced to size.  If the hypotenus is already smaller
    than size it will remain unchanged. Return values are the
    new components of the triangle, signs and angle remain the same."""
    if adj**2 + op**2 > size**2:
        angle = math.atan2(op,adj)
        adj = size*math.cos(angle)
        op  = size*math.sin(angle)
    return (adj,op)