#

from numpy import array, dot


#########################################################
# WORLDVERT class
#########################################################

class worldvert:
    def __init__(self, x=0, y=0, z=0, description='', DEBUG=0):
      self.tr = array([x,y,z,1])  # tr = "translate position"
      self.descr = description
      self.DEBUG = DEBUG

    def __repr__(self):
        mystr = "worldvert " + self.descr + "\n tr: " + self.tr.__repr__()
        return mystr      


##################################################
# WORLDEDGE class
##################################################

class worldedge:
    def __init__(self, wv1, wv2, description='', DEBUG=0):
      self.wv1 = wv1
      self.wv2 = wv2
      self.descr = description
      self.DEBUG = DEBUG
    
    def __repr__(self):
        mystr = "Worldedge " + self.descr +" wv1:\n" + self.wv1.__repr__()   \
            + "\nworldedge " + self.descr + " wv2:\n" +     \
            self.wv2.__repr__() + "\n"
        return mystr


##########################################################
# SCREEENVERT class
##########################################################
# 9/1/08: Way too ugly to have screenvert contain or point to
# a worldvert, so I'm changing this to use a translate array just
# like worldvert.  If you want screenvert to have the values of
# a worldvert, you need to copy those values in by hand or pass
# them in at construction time, just like you would with a worldvert.

class screenvert:
    def __init__(self, x=0., y=0., z=0., description='', DEBUG=0):
        self.tr = array([x,y,z,1])  # tr = "translate position"
        self.camtr = array([0.,0.,0.,0.])  # Position in camera space
        self.screenx = 0
        self.screeny = 0
        self.descr = description
        self.DEBUG = DEBUG

    def __repr__(self):
        mystr = "screenvert " + self.descr + "\n tr: " + self.tr.__repr__()  \
        +  "\ncamspace: " + self.camtr.__repr__() +          \
          "\n screenspace: " + str(self.screenx) + ", " +   \
          str(self.screeny)
        return mystr

    def worldtocam(self, camera):
        # camera.worldtocam is a premultiplied set of conversion transforms
        # (trans then rot then invertz) maintained by the Camera object
        self.camtr = dot(camera.worldtocam, self.tr)
        if self.DEBUG:
            print "Converted vertex %s to camspace:" % (self.descr)
            print self




##################################################
# SCREENEDGE class
##################################################

class screenedge:
    def __init__(self, sv1, sv2, width=2, color='black', arrow='none', \
                 description='', circle=0, DEBUG=0):
      self.sv1 = sv1  # screenvert not worldvert
      self.sv2 = sv2
      self.width = width
      self.id = 0  # Tracks canvas ID for line
      self.cid = 0  # canvas ID of circle at joint end, if in use
      self.color = color
      self.arrow = arrow
      self.descr = description
      self.circle = circle  # Set to 1 to draw circle at end of edge
      self.drawme = 1  # Set to 0 to not attempt to draw on screen
      self.DEBUG = DEBUG

    def __repr__(self):
        mystr = "Screenedge " + self.descr +" sv1:\n" + self.sv1.__repr__()   \
            + "\nscreenedge " + self.descr + " sv2:\n" +     \
            self.sv2.__repr__() + "\n"
        return mystr

    def worldtocam(self,camera):
        self.sv1.worldtocam(camera)
        self.sv2.worldtocam(camera)


# 9/6/08: was in screenvert class, but needs to be in screenedge class
    def camtoscreen(self, camera, canvw, canvh):  # canvw = canvaswidth, \
                                            # canvh = canvasheight

# cf[xy] defines a camera rectangle, with origin at the center, that
#  spans from (x,y)=(-cfx, -cfy) to (cfx, cfy)
# 
# canv[wh] defines a Tk canvas rectange, with origin in upper left
# and "down" meaning "y positive", that spans from
# (0,0) to (canvh,canvw)
# 
# PARALLEL PROJECTION (PP) camera:
# We can ignore the camera Z value in this case.
# So this function just has to map camera (x,y) onto Tk's canvas
# (x,y), taking the sign reversal of the y axis into account.
#
# PERSPECTIVE PROJECTION camera:
# First we have to correct vertex x and y using a fudge factor
# that incorporates the vertex's z distance away from the camera,
# and the projection plane distance.
# After that the math is the same as the PP case.

      cfx = camera.cfx  # "Camera frame size", width
      cfy = camera.cfy  # "Camera frame size", height
      ppdist = camera.ppdist
      x1 = self.sv1.camtr[0]
      y1 = self.sv1.camtr[1]
      z1 = self.sv1.camtr[2]

      x2 = self.sv2.camtr[0]
      y2 = self.sv2.camtr[1]
      z2 = self.sv2.camtr[2]

      if camera.parallel:
        self.sv1.screenx = (canvw/2)*(1 + (x1/cfx))
        self.sv1.screeny = (canvh/2)*(1 - (y1/cfy))
        self.sv2.screenx = (canvw/2)*(1 + (x2/cfx))
        self.sv2.screeny = (canvh/2)*(1 - (y2/cfy))

      else:  # perspective camera
        if z1 > 0.1 and z2 > 0.1:
          self.drawme = 1
          xproj1 = x1 * ppdist / z1
          yproj1 = y1 * ppdist / z1
          self.sv1.screenx = (canvw/2)*(1 + (xproj1/cfx))
          self.sv1.screeny = (canvh/2)*(1 - (yproj1/cfy))

          xproj2 = x2 * ppdist / z2
          yproj2 = y2 * ppdist / z2
          self.sv2.screenx = (canvw/2)*(1 + (xproj2/cfx))
          self.sv2.screeny = (canvh/2)*(1 - (yproj2/cfy))

        elif z1 <= 0.1 and z2 <= 0.1:
          self.drawme = 0  # Both verts are behind the camera -- stop now

        elif z1 > 0.1 and z2 <= 0.1:
          # First vert is in front of camera, second vert is not
#          print "se.camtoscreen case 3 starting for (%s)" % self.descr
#          print "  verts are (%s,%s,%s) (%s,%s,%s)" %   \
#              (x1,y1,z1,x2,y2,z2)
          self.drawme = 1
          xproj1 = x1 * ppdist / z1
          yproj1 = y1 * ppdist / z1
          self.sv1.screenx = (canvw/2)*(1 + (xproj1/cfx))
          self.sv1.screeny = (canvh/2)*(1 - (yproj1/cfy))
#          print "  sv1 maps to (%s,%s)" % (self.sv1.screenx, \
#                                               self.sv1.screeny)

          t = (0.1-z1)/(z2-z1)
          x3 = t*(x2-x1) + x1
          y3 = t*(y2-y1) + y1
          z3 = 0.1
#          print "  Computed alternate point (%s,%s,%s)" % (x3,y3,z3)
          xproj3 = x3 * ppdist / z3
          yproj3 = y3 * ppdist / z3
          self.sv2.screenx = (canvw/2)*(1 + (xproj3/cfx))
          self.sv2.screeny = (canvh/2)*(1 - (yproj3/cfy))
#          print "  Alternate point maps to (%s,%s)" % (self.sv2.screenx, \
#                                               self.sv2.screeny)

        else:
          # First vert is behind the camera, second vert is not
#          print "se.camtoscreen case 4 starting for (%s)", self.descr
          self.drawme = 1
          xproj2 = x2 * ppdist / z2
          yproj2 = y2 * ppdist / z2
          self.sv2.screenx = (canvw/2)*(1 + (xproj2/cfx))
          self.sv2.screeny = (canvh/2)*(1 - (yproj2/cfy))

          t = (0.1-z2)/(z1-z2)
          x3 = t*(x1-x2) + x2
          y3 = t*(y1-y2) + y2
          z3 = 0.1
          xproj3 = x3 * ppdist / z3
          yproj3 = y3 * ppdist / z3
          self.sv1.screenx = (canvw/2)*(1 + (xproj3/cfx))
          self.sv1.screeny = (canvh/2)*(1 - (yproj3/cfy))

# If the vertex has z=0, it's "in the camera's blind spot" - it's like
# having something right above your head or next to one of your ears.
# The visual result is that you can't see it.  But you can still see
# the edge that connects to the vertex, if the other end of the edge
# is within the viewport.
#
# If the vertex has z<0, it will project onto the projection plane
# incorrectly, somewhat as if the object is behind you and you're
# holding a spoon in front of you and seeing the object reflected.
# The x and y projection points end up flipping from the z>0 case.
# This isn't what we want -- it's very disorienting and doesn't
# correspond to what an actual viewer would see.
# The approach used here is to compute a replacement point (x3,y3,z3)
# which is in front of the camera.  Here the math sets z3=0.1 and
# computes x3 and y3 using a parameterized representation of
# the line segment sv1--sv2
#
# This approach to vertices with z<=0 also means that for the perspective
# camera, we don't see objects that are behind us.  For the parallel
# camera this presently isn't true - the parallel camera renders points
# no matter what (camera z) is.



#    def camtoscreen(self,camera, canvw, canvh):
#        self.sv1.camtoscreen(camera, canvw, canvh)
#        self.sv2.camtoscreen(camera, canvw, canvh)

    def draw(self, canvas):
        self.undraw(canvas)
        if self.drawme:
          x1 = self.sv1.screenx
          y1 = self.sv1.screeny
          x2 = self.sv2.screenx
          y2 = self.sv2.screeny
          if self.DEBUG:
            print "About to call create_line with (%d, %d, %d, %d)"    \
                        % (x1,y1,x2,y2)
          self.id = canvas.create_line(x1,y1,x2,y2, fill=self.color, \
                                       width=self.width, arrow=self.arrow)
          if self.circle:
            self.cid = canvas.create_oval(x2-3,y2-3,x2+3,y2+3, \
                                              fill=self.color)

    def undraw(self, canvas):
        if self.id:
            canvas.delete(self.id)
        self.id = 0
        if self.cid:
            canvas.delete(self.cid)
        self.cid = 0




#############################
# BEGIN NON-CLASS FUNCTIONS
#############################

####################################
# DELETE_SCREEN_LINES
# Use this function to delete all displayed skeleton edges (bones)
# from display on a canvas
#
def undraw_screen_lines(screenedgelist, canvas):
  count = len(screenedgelist)
  for x in range(count):
      screenedgelist[x].undraw(canvas)


##################################
# GRID_SETUP
# Creates and returns a populated array of screenedge
# Don't call this until you've set up your skeleton and can
# extract minx, miny, maxx, maxy from it.
#
def grid_setup(minx, minz, maxx, maxz, DEBUG=0):

    if DEBUG:
        print "grid_setup: minx=%s, minz=%s, maxx=%s, maxz=%s" % \
            (minx, minz, maxx, maxz)

    # The input values define a rectangle.  Round them to nearest 10.
    minx2 = 10*int(minx/10) - 10
    maxx2 = 10*int(maxx/10) + 10
    minz2 = 10*int(minz/10) - 10
    maxz2 = 10*int(maxz/10) + 10

    gridedges = []
# Range() won't give us the topmost value of the range, so we have to
# use maxz2+1 as the top of the range.
    for z in range(minz2, maxz2+1, 10):
      sv1 = screenvert(minx2, 0., z)
      sv2 = screenvert(maxx2, 0., z)
      se = screenedge(sv1, sv2, width=1, color='grey', DEBUG=0)
      if DEBUG:
          print "grid_setup: adding screenedge from (%d,%d) to (%d,%d)" \
              % (minx2, z, maxx2, z)
      gridedges.append(se)

    for x in range(minx2, maxx2+1, 10):
      sv1 = screenvert(x, 0., minz2)
      sv2 = screenvert(x, 0., maxz2)
      se = screenedge(sv1, sv2, width=1, color='grey', DEBUG=0)
      if DEBUG:
          print "grid_setup: adding screenedge from (%d,%d) to (%d,%d)" \
              % (x, minz2, x, maxz2)
      gridedges.append(se)

    return gridedges
