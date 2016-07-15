
from math import cos, sin, degrees, radians, pi
from numpy import array, dot
from copy import deepcopy

ZEROMAT = array([ [0.,0.,0.,0.],[0.,0.,0.,0.],[0.,0.,0.,0.],[0.,0.,0.,0.] ])
IDENTITY = array([ [1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.] ])


####################
# This camera can be either perspective or parallel-projection.
# Default is perspective.
#
# PARALLEL PROJECTION (PP) CAMERA:
# The camera can see objects that have an (xyz), within the
# camera's coordinate system, of (-cfx to cfx, -cfy to cfy, ANY) where
# the z value is irrelevant.
#
#
# For the PP camera, "move forward" function doesn't actually change
# the camera position, rather it reduces cfx and cfy thus giving a
# "zoom in" effect.  Similarly the "move back" function increases cfx
# and cfy, giving a "zoom out" effect.
#
#
# PERSPECTIVE CAMERA:
# A perspective camera requires a Center of Projection, which is the
# camera location itself, and a projection plane.  In camera space
# (which is LH space not RH), the projection plane is perp to the
# z axis and the camera is looking directly down the z axis at the plane.
#
# "ppdist" is the distance from the camera to the projection plane.
#
# cfx and cfy represents the size of camera-space rectangle on the projection
# plane that maps onto the Tk canvas.  This is the
# same meaning as for the PP camera.  For the perspective camera, cf[xy]
# are fixed at camera-creation time.  To make a large object fit into
# the display, instead of increasing cf[xy] (as we would with the PP
# camera), you have to move the camera backwards, which makes more
# vertices map into the view rectangle on the projection plane.

# WATCH OUT: The aspect ratio specified by cf[xy] needs to match the
# aspect ratio of the Tk canvas that displays your graphics.  
# However there's nothing intrinsic to Tk that makes this happen.
# What this means is that when the user resizes the application window,
# that event needs to trigger both a camera aspect ratio change
# (a change to cf[xy]) as well as a canvas widget resize.

# The math for the perspective camera is very close to the math for
# the PP camera.  The difference is that for the perspective camera,
# we first have to correct a vertex's x and y to represent the process
# of projecting the vertex onto the screen.  Once we've done that,
# we can follow the PP algorithm that simply ignores z entirely.
# The difference in math doesn't show up here -- see the vertex class
# in geo.py for where the difference takes place.


class Camera:  # Defaults based pretty much on trial and error
    def __init__(self, x=0, y=0, z=-10, DEBUG=0, parallel=0, \
                 ppdist=30, cfx=30):
        self.parallel = parallel  # Set to 1 for PP camera

# Initial camera view window must be a square (because I say so),
# so we set self.cfy = cfx initially.
        self.cfx = cfx  # Camera projection window width
        self.cfy = cfx  # Camera projection window height
# Permanently store the initial values for future use
        self.basecfx = self.cfx  
        self.basecfy = self.cfy
        self.ppdist = ppdist # Projection plane distance from camera.
                             # Used only for perspective camera.
        self.debug = DEBUG
#cgkit#        self.t = vec4(x,y,z,1)
        self.t = array([x,y,z,1.])

# The camera uses a left-handed coordinate system, however [xyz]rot
# are in world coordinates, which is right-handed.
# The default, zero-rotation position of the camera is with the
# camera/eye pointed along the NEGATIVE Z world axis.
        self.xrot = 0  # Not presently used
        self.yrot = radians(0)
        self.zrot = 0  # Not presently used
        self.trans_inc = 5  # Camera move increment when move function called
        self.rot_inc = radians(5)  # Camera rotation increment when 
                                   # rot function called
#cgkit#        self.transmat = mat4()
#cgkit#        self.rotmat = mat4() 
        self.transmat = deepcopy(ZEROMAT)
        self.rotmat = deepcopy(ZEROMAT)

        # To convert from worldspace to camera space, the final step
        # is to invert the z coordinate of a vertex, since this is how
        # you convert from RH worldspace to LH camspace.
#cgkit#        self.invertz = mat4(1.0)  # Identity
        self.invertz = deepcopy(IDENTITY)
        self.invertz[2,2] = -1
        self.Recompute()


    def __repr__(self):  # allows print to use Camera semi-normally
        str1 = "xyzw yrot cfx cfy ppdist: %s %s %s %s %s\n" % (self.t, 
                degrees(self.yrot), self.cfx, self.cfy, self.ppdist)
        str2 = " transmat = " + self.transmat.__repr__()
        str3 = "\n rotmat = " + self.rotmat.__repr__()
        str4 = "\n invertz = " + self.invertz.__repr__()
        str5 = "\n worldtocam = " + self.worldtocam.__repr__()
        return (str1 + str2 + str3 + str4 + str5)

    def Recompute(self):
#cgkit#        self.transmat = self.transmat.translation(self.transvec)
#cgkit#        self.rotmat = self.rotmat.rotation(-self.yrot, YAXIS)
#cgkit#        self.worldtocam = self.invertz * self.rotmat * self.transmat

        self.transmat = deepcopy(IDENTITY)
        self.transmat[0,3] = -self.t[0]
        self.transmat[1,3] = -self.t[1]
        self.transmat[2,3] = -self.t[2]

        self.rotmat = deepcopy(IDENTITY)
        theta = -self.yrot
        self.rotmat[0,0] = cos(theta)
        self.rotmat[0,2] = sin(theta)
        self.rotmat[2,0] = -sin(theta)
        self.rotmat[2,2] = cos(theta)
        self.worldtocam = dot(dot(self.invertz, self.rotmat),self.transmat)

    def RecomputeRot(self):
#cgkit#        self.rotmat = self.rotmat.rotation(-self.yrot, YAXIS)
#cgkit#        self.worldtocam = self.invertz * self.rotmat * self.transmat
        self.rotmat = deepcopy(IDENTITY)
        theta = -self.yrot
        self.rotmat[0,0] = cos(theta)
        self.rotmat[0,2] = sin(theta)
        self.rotmat[2,0] = -sin(theta)
        self.rotmat[2,2] = cos(theta)
        self.worldtocam = dot(dot(self.invertz, self.rotmat),self.transmat)


    def RecomputeTrans(self):
#cgkit#        self.transmat = self.transmat.translation(self.transvec)
#cgkit#        self.worldtocam = self.invertz * self.rotmat * self.transmat
        self.transmat = deepcopy(IDENTITY)
        self.transmat[0,3] = -self.t[0]
        self.transmat[1,3] = -self.t[1]
        self.transmat[2,3] = -self.t[2]
        self.worldtocam = dot(dot(self.invertz, self.rotmat),self.transmat)

    def MoveR(self, event=None):
#cgkit#        self.t.x += (self.trans_inc * cos(self.yrot))
#cgkit#        self.t.z -= (self.trans_inc * sin(self.yrot))
        self.t[0] += (self.trans_inc * cos(self.yrot))
        self.t[2] -= (self.trans_inc * sin(self.yrot))
        self.RecomputeTrans()
        if self.debug: 
            print "Camera move right"
            print self

    def MoveL(self, event=None):
#cgkit#        self.t.x -= (self.trans_inc * cos(self.yrot))
#cgkit#        self.t.z += (self.trans_inc * sin(self.yrot))
        self.t[0] -= (self.trans_inc * cos(self.yrot))
        self.t[2] += (self.trans_inc * sin(self.yrot))
        self.RecomputeTrans()
        if self.debug: 
            print "Camera move left"
            print self

    def MoveUp(self, event=None):
        # This camera isn't allowed to tilt up/down or L/R, so "move up"
        # is always a true upward move in the world coordinate system.
#cgkit#        self.t.y += self.trans_inc
        self.t[1] += self.trans_inc
        self.RecomputeTrans()
        if self.debug: 
            print "Camera move up"
            print self

    def MoveDown(self, event=None):
#cgkit#        self.t.y -= self.trans_inc
        self.t[1] -= self.trans_inc
        self.RecomputeTrans()
        if self.debug: 
            print "Camera move down"
            print self

    def MoveFd(self, event=None):
        if self.parallel:
          self.cfx -= 5
          self.cfy -= 5
          if((self.cfx <=0) or (self.cfy <=0)): 
             self.cfx += 5  # Back out the change
             self.cfy += 5  
          # No Recompute needed since camera isn't actually moving even
          # though the user perceives it as such.
        else: # Perspective camera actually does move physically fd + back
#cgkit#          self.t.x -= (self.trans_inc * sin(self.yrot))
#cgkit#          self.t.z -= (self.trans_inc * cos(self.yrot))
          self.t[0] -= (self.trans_inc * sin(self.yrot))
          self.t[2] -= (self.trans_inc * cos(self.yrot))
          self.RecomputeTrans()
        if self.debug:
            print "Camera move forward"
            print self

    def MoveBack(self, event=None):
        if self.parallel:
          self.cfx += 5
          self.cfy += 5
          # No Recompute needed
        else:  # Perspective camera
#cgkit#          self.t.x += (self.trans_inc * sin(self.yrot))
#cgkit#          self.t.z += (self.trans_inc * cos(self.yrot))
          self.t[0] += (self.trans_inc * sin(self.yrot))
          self.t[2] += (self.trans_inc * cos(self.yrot))
          self.RecomputeTrans()
        if self.debug:
            print "Camera move back"
            print self

    def RotR(self, event=None):
        self.yrot -= self.rot_inc
        if (self.yrot < 0):
            self.yrot += 2*pi
        self.RecomputeRot()
        if self.debug:
            print "Camera rotate right"
            print self

    def RotL(self, event=None):
        self.yrot += self.rot_inc
        if (self.yrot >= 2*pi):
            self.yrot -= 2*pi
        self.RecomputeRot()
        if self.debug:
            print "Camera rotate left"
            print self

