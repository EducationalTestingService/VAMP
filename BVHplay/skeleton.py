#!/opt/python/2.7/bin/python

# skeleton.py: various BVH and skeleton-related classes.
# Adapted from earlier work "bvhtest.py"

# AVOIDING OFF-BY-ONE ERRORS:
# Let N be the total number of keyframes in the BVH file.  Then:
# - bvh.keyframes[] is an array that runs from 0 to N-1
# - skeleton.keyframes[] is another reference to bvh.keyframes and similarly
#   runs from 0 to N-1
# - skeleton.edges{t} is a dict where t can run from 1 to N
# - joint.trtr{t} is a dict where t can run from 1 to N
# - joint.worldpos{t} is a dict where t can run from 1 to N
#
# So if you're talking about raw BVH keyframe rows from the file,
# you use an array and the values run from 0 to N-1.  This is an artifact
# of using .append to create bvh.keyframes.
# 
# By contrast, if you're talking about a non-keyframe data structure
# derived from the BVH keyframes, such as matrices or edges, it's a
# dictionary and the values run from 1 to N.

import sys
#sys.path.append('/home/speech/Research/MMI/bvhProcessing/cgkit/cgkit-2.0.0')

from math import radians, cos, sin
from cgkit.bvh import BVHReader
from geo import worldvert, screenvert, worldedge, screenedge
from numpy import array, dot
from copy import deepcopy

#cgkit# XAXIS = vec3(1,0,0)
#cgkit# YAXIS = vec3(0,1,0)
#cgkit# ZAXIS = vec3(0,0,1)
#cgkit# ORIGIN = vec4(0,0,0,1)


ZEROMAT = array([ [0.,0.,0.,0.],[0.,0.,0.,0.],[0.,0.,0.,0.],[0.,0.,0.,0.] ])
IDENTITY = array([ [1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.] ])


#######################################
# JOINT class (formerly BONE)
# A BVH "joint" is a single vertex with potentially MULTIPLE
# edges.  It's not accurate to call these "bones" because if
# you rotate the joint, you rotate ALL attached bones.

class joint:
  def __init__(self, name):
    self.name = name
    self.children = []
    self.channels = []  # Set later.  Ordered list of channels: each
        # list entry is one of [XYZ]position, [XYZ]rotation
    self.hasparent = 0  # flag
    self.parent = 0  # joint.addchild() sets this
#cgkit#    self.strans = vec3(0,0,0)  # static translation vector (x, y, z)
    self.strans = array([0.,0.,0.])  # I think I could just use   \
                                     # regular Python arrays

    # Transformation matrices:
    self.stransmat = array([ [0.,0.,0.,0.],[0.,0.,0.,0.],    \
                               [0.,0.,0.,0.],[0.,0.,0.,0.] ])

    self.trtr = {}
##    self.trtr = []       # self.trtr[time]  A premultiplied series of
                         # translation and rotation matrices
    self.worldpos = {}
##    self.worldpos = []  # Time-based worldspace xyz position of the
                        # joint's endpoint.  A list of vec4's

  def info(self):
    print "Joint name:", self.name
    print " %s is connected to " % self.name,
    if(len(self.children) == 0):
        print "nothing"
    else:
      for child in self.children:
        print "%s " % child.name,
      print
    for child in self.children:
      child.info()


  def __repr__(self):  # Recursively build up text info
    str2 = self.name + " at strans=" + str(self.strans) + " is connected to "
# Not sure how well self.strans will work now that self.strans is
# a numpy "array", no longer a cgkit vec3.
    if(len(self.children) == 0):
      str2 = str2 + "nothing\n"
    else: 
      for child in self.children:
        str2 = str2 + child.name + " "
      str2 = str2 + "\n"
    str3 = ""
    for child in self.children:
      str3 = str3 + child.__repr__()
    str1 = str2 + str3
    return (str1)

  def addchild(self, childjoint):
    self.children.append(childjoint)
    childjoint.hasparent = 1
    childjoint.parent = self

  # Called by skeleton.create_edges()
  def create_edges_recurse(self, edgelist, t, DEBUG=0):
    if DEBUG:
      print "create_edge_recurse starting for joint ", self.name
    if self.hasparent:
      temp1 = self.parent.worldpos[t]  # Faster than triple lookup below?
      temp2 = self.worldpos[t]
      v1 = worldvert(temp1[0], temp1[1], temp1[2], DEBUG=DEBUG, \
                    description=self.parent.name)
      v2 = worldvert(temp2[0], temp2[1], temp2[2], DEBUG=DEBUG, \
                    description=self.name)

      descr = self.parent.name + " to " + self.name
      myedge = worldedge(v1,v2, description=descr)
      edgelist.append(myedge)

    for child in self.children:
      if DEBUG:
        print " Recursing for child ", child.name
      child.create_edges_recurse(edgelist,t, DEBUG)

# End class joint


###############################
# SKELETON class
#
# This class is actually for a skeleton plus some time-related info
#   frames: number of frames in the animation
#   dt: delta-t in seconds per frame (default: 30fps i.e. 1/30)
class skeleton:
  def __init__(self, hips, keyframes, frames=0, dt=.033333333):
    self.hips = hips
# 9/1/08: we now transfer the large bvh.keyframes data structure to
# the skeleton because we need to keep this dataset around.
    self.keyframes = keyframes  
    self.frames = frames  # Number of frames (caller must set correctly)
    self.dt = dt
##    self.edges = []  # List of list of edges.  self.edges[time][edge#]
    self.edges = {}  # As of 9/1/08 this now runs from 1...N not 0...N-1

# Precompute hips min and max values in all 3 dimensions.
# First determine how far into a keyframe we need to look to find the 
# XYZ hip positions
    offset = 0
    for channel in self.hips.channels:
      if(channel == "Xposition"): xoffset = offset
      if(channel == "Yposition"): yoffset = offset
      if(channel == "Zposition"): zoffset = offset
      offset += 1
    self.minx = 999999999999
    self.miny = 999999999999
    self.minz = 999999999999
    self.maxx = -999999999999
    self.maxy = -999999999999
    self.maxz = -999999999999
# We can't just look at the keyframe values, we also have to correct
# by the static hips OFFSET value, since sometimes this can be quite
# large.  I feel it's bad BVH file form to have a non-zero HIPS offset
# position, but there are definitely files that do this.
    xcorrect = self.hips.strans[0]
    ycorrect = self.hips.strans[1]
    zcorrect = self.hips.strans[2]

#    self.strans = array([0.,0.,0.])  # I think I could just use   \
    for keyframe in self.keyframes:
      x = keyframe[xoffset] + xcorrect
      y = keyframe[yoffset] + ycorrect
      z = keyframe[zoffset] + zcorrect
      if x < self.minx: self.minx = x
      if x > self.maxx: self.maxx = x
      if y < self.miny: self.miny = y
      if y > self.maxy: self.maxy = y
      if z < self.minz: self.minz = z
      if z > self.maxz: self.maxz = z


  def __repr__(self):
    str1 = "frames = " + str(self.frames) + ", dt = " + str(self.dt) + "\n"
    str1 = str1 + self.hips.__repr__()
    return str1



####################
# MAKE_SKELSCREENEDGES: creates and returns an array of screenedge
# that has exactly as many elements as the joint count of skeleton.
#
  def make_skelscreenedges(self, arrow='none', circle=0, DEBUG=0):
    if DEBUG:
      print "make_sse starting"

# I need the number of joints in self.  We don't store this value
# in the class, but we can get it by looking at the length of any
# edge array self.edges[t] for any t.  So we make sure that self.edges[1]
# is set up, then we take its length.
    if not (self.edges.has_key(1)):
      self.create_edges_onet(1)

    jointcount = len(self.edges[1])
    if DEBUG:
      print "make_skelscreenedges: jointcount=",jointcount
    skelscreenedges = []

    for x in range(jointcount):
      sv1 = screenvert(0.,0.,0.,description='make_sse_sv1')
      sv2 = screenvert(0.,0.,0.,description='make_sse_sv2')
      se1 = screenedge(sv1, sv2, arrow=arrow, circle=circle, DEBUG=DEBUG, \
                           description='created_by_make_skelscreenedges' )
      skelscreenedges.append(se1)
    return skelscreenedges





#########################################
# CREATE_EDGES_ONET class function

  def create_edges_onet(self,t,DEBUG=0):
#    print "create_edges_onet starting for t=",t
    if DEBUG:
      print "create_edges_onet starting for t=",t

# Before we can compute edge positions, we need to have called
# process_bvhkeyframe for time t, which computes trtr and worldpos
# for the joint hierarchy at time t.  Since we no longer precompute
# this information when we read the BVH file, here's where we do it.
# This is on-demand computation of trtr and worldpos.
    if not (self.hips.worldpos.has_key(t)):
      if DEBUG:
        print "create_edges_onet: about to call process_bvhkeyframe for t=",t
      process_bvhkeyframe(self.keyframes[t-1], self.hips, t, DEBUG=DEBUG)

    if not (self.edges.has_key(t)):
      if DEBUG:
        print "create_edges_onet: creating edges for t=",t
      edgelist = []
      self.hips.create_edges_recurse(edgelist, t, DEBUG=DEBUG)
      self.edges[t] = edgelist  # dictionary entry      

    if DEBUG:
      print "create_edges edge list at timestep %d:" %(t)
      print edgelist


#################################
# POPULATE_SKELSCREENEDGES
# Given a time t and a precreated array of screenedge, copies values
# from skeleton.edges[] into the screenedge array.
#
# Use this routine whenever slidert (time position on slider) changes.
# This routine is how you get your edge data somewhere that redraw()
# will make use of it.

  def populate_skelscreenedges(self, sse, t, DEBUG=0):
    if DEBUG:
      print "populate_sse starting for t=",t
# First we have to make sure that self.edges exists for slidert=t
    if not (self.edges.has_key(t)):
      if DEBUG:
        print "populate_skelscreenedges: about to call create_edges_onet(%d)" \
                             % (t)
      self.create_edges_onet(t, DEBUG=DEBUG)
    counter = 0
    for wldedge in self.edges[t]:
      # Yes, we copy in the xyz values manually.  This keeps us sane.
      sse[counter].sv1.tr[0] = wldedge.wv1.tr[0]
      sse[counter].sv1.tr[1] = wldedge.wv1.tr[1]
      sse[counter].sv1.tr[2] = wldedge.wv1.tr[2]
      sse[counter].sv2.tr[0] = wldedge.wv2.tr[0]
      sse[counter].sv2.tr[1] = wldedge.wv2.tr[1]
      sse[counter].sv2.tr[2] = wldedge.wv2.tr[2]
      # Also copy in the name
      sse[counter].descr = wldedge.descr
      counter +=1
    if DEBUG:
      print "populate_skelscreenedges: copied %d edges from skeleton to sse" \
          % (counter)



#######################################
# READBVH class
#
# Per the BVHReader documentation, we need to subclass BVHReader
# and set up functions onHierarchy, onMotion, and onFrame to parse
# the BVH file.
#
class readbvh(BVHReader):
  def onHierarchy(self, root):
    print "readbvh: onHierarchy invoked"
    self.root = root  # Save root for later use
    self.keyframes = []  # Used later in onFrame

  def onMotion(self, frames, dt):
    print "readbvh: onMotion invoked.  frames = %s, dt = %s" % (frames,dt)
    self.frames = frames
    self.dt = dt

  def onFrame(self, values):
    print "readbvh: onFrame invoked, values =", values
    self.keyframes.append(values)  # Hopefully this gives us a list of lists


#######################################
# NON-CLASS FUNCTIONS START HERE
#######################################

#######################################
# PROCESS_BVHNODE function
#
# Recursively process a BVHReader node object and return the root joint
# of a bone hierarchy.  This routine creates a new joint hierarchy.
# It isn't a Skeleton yet since we haven't read any keyframes or
# created a Skeleton class yet.
#
# Steps:
# 1. Create a new joint
# 2. Copy the info from Node to the new joint
# 3. For each Node child, recursively call myself
# 4. Return the new joint as retval
#
# We have to pass in the parent name because this routine
# needs to be able to name the leaves "parentnameEnd" instead
# of "End Site"

def process_bvhnode(node, parentname='hips'):
  name = node.name
  if (name == "End Site") or (name == "end site"):
    name = parentname + "End"
  # print "process_bvhnode: name is ", name
  b1 = joint(name)
  b1.channels = node.channels
#cgkit#  b1.strans.x = node.offset[0]
#cgkit#  b1.strans.y = node.offset[1]
#cgkit#  b1.strans.z = node.offset[2]
  b1.strans[0] = node.offset[0]
  b1.strans[1] = node.offset[1]
  b1.strans[2] = node.offset[2]

# Compute static translation matrix from vec3 b1.strans
#cgkit#  b1.stransmat = b1.stransmat.translation(b1.strans)
##  b1.stransmat = deepcopy(IDENTITY)
  b1.stransmat = array([ [1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.] ])

  b1.stransmat[0,3] = b1.strans[0]
  b1.stransmat[1,3] = b1.strans[1]
  b1.stransmat[2,3] = b1.strans[2]

  for child in node.children:
    b2 = process_bvhnode(child, name)  # Creates a child joint "b2"
    b1.addchild(b2)
  return b1


###############################
# PROCESS_BVHKEYFRAME
# Recursively extract (occasionally) translation and (mostly) rotation
# values from a sequence of floats and assign to joints.
#
# Takes a keyframe (a list of floats) and returns a new keyframe that
# contains the not-yet-processed (not-yet-eaten) floats of the original
# sequence of floats.  Also assigns the eaten floats to the appropriate
# class variables of the appropriate Joint object.
#
# This function could technically be a class function within the Joint
# class, but to maintain similarity with process_bvhnode I won't do that.
#
# 9/1/08: rewritten to process only one keyframe

def process_bvhkeyframe(keyframe, joint, t, DEBUG=0):

  counter = 0
  dotrans = 0
  dorot = 0

# We have to build up drotmat one rotation value at a time so that
# we get the matrix multiplication order correct.
  drotmat = array([ [1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.] ])

  if DEBUG:
    print " process_bvhkeyframe: doing joint %s, t=%d" %  (joint.name, t)
    print " keyframe has %d elements in it." % (len(keyframe))

  # Suck in as many values off the front of "keyframe" as we need
  # to populate this joint's channels.  The meanings of the keyvals
  # aren't given in the keyframe itself; their meaning is specified
  # by the channel names.
  for channel in joint.channels:
    keyval = keyframe[counter]
    if(channel == "Xposition"):
      dotrans = 1
      xpos = keyval
    elif(channel == "Yposition"):
      dotrans = 1
      ypos = keyval
    elif(channel == "Zposition"):
      dotrans = 1
      zpos = keyval
    elif(channel == "Xrotation"):
      dorot = 1
      xrot = keyval
#cgkit#      drotmat2 = drotmat2.rotation(radians(xrot), XAXIS)
#cgkit#      drotmat = drotmat * drotmat2  # Build up the full rotation matrix
      theta = radians(xrot)
      mycos = cos(theta)
      mysin = sin(theta)
##      drotmat2 = deepcopy(IDENTITY)
      drotmat2 = array([ [1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],    \
                           [0.,0.,0.,1.] ])
      drotmat2[1,1] = mycos
      drotmat2[1,2] = -mysin
      drotmat2[2,1] = mysin
      drotmat2[2,2] = mycos
      drotmat = dot(drotmat, drotmat2)

    elif(channel == "Yrotation"):
      dorot = 1
      yrot = keyval
#cgkit#      drotmat2 = drotmat2.rotation(radians(yrot), YAXIS)
#cgkit#      drotmat = drotmat * drotmat2
      theta = radians(yrot)
      mycos = cos(theta)
      mysin = sin(theta)
##      drotmat2 = deepcopy(IDENTITY)
      drotmat2 = array([ [1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],    \
                           [0.,0.,0.,1.] ])
      drotmat2[0,0] = mycos
      drotmat2[0,2] = mysin
      drotmat2[2,0] = -mysin
      drotmat2[2,2] = mycos
      drotmat = dot(drotmat, drotmat2)

    elif(channel == "Zrotation"):
      dorot = 1
      zrot = keyval
      theta = radians(zrot)
      mycos = cos(theta)
      mysin = sin(theta)
##      drotmat2 = deepcopy(IDENTITY)
      drotmat2 = array([ [1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],     \
                           [0.,0.,0.,1.] ])
      drotmat2[0,0] = mycos
      drotmat2[0,1] = -mysin
      drotmat2[1,0] = mysin
      drotmat2[1,1] = mycos
      drotmat = dot(drotmat, drotmat2)
    else:
      print "Fatal error in process_bvhkeyframe: illegal channel name ", \
                                                               channel
      return(0)
##      sys.exit()
    counter += 1
  # End "for channel..."

  if dotrans:  # If we are the hips...
    # Build a translation matrix for this keyframe
    dtransmat = array([ [1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],    \
                          [0.,0.,0.,1.] ])
    dtransmat[0,3] = xpos
    dtransmat[1,3] = ypos
    dtransmat[2,3] = zpos

    if DEBUG:
      print "  Joint %s: xpos ypos zpos is %s %s %s" % (joint.name, \
                                                   xpos, ypos, zpos)
    # End of IF dotrans

    if DEBUG:
      print "  Joint %s: xrot yrot zrot is %s %s %s" %     \
               (joint.name, xrot, yrot, zrot)

  # At this point we should have computed:
  #  stransmat  (computed previously in process_bvhnode subroutine)
  #  dtransmat (only if we're the hips)
  #  drotmat
  # We now have enough to compute joint.trtr and also to convert
  # the position of this joint (vertex) to worldspace.
  # 
  # For the non-hips case, we assume that our parent joint has already
  # had its trtr matrix appended to the end of self.trtr[]
  # and that the appropriate matrix from the parent is the LAST item
  # in the parent's trtr[] matrix list.
  # 
  # Worldpos of the current joint is localtoworld = TRTR...T*[0,0,0,1]
  #   which equals parent_trtr * T*[0,0,0,1]
  # In other words, the rotation value of a joint has no impact on
  # that joint's position in space, so drotmat doesn't get used to
  # compute worldpos in this routine.
  # 
  # However we don't pass localtoworld down to our child -- what
  # our child needs is trtr = TRTRTR...TR
  # 
  # The code below attempts to optimize the computations so that we
  # compute localtoworld first, then trtr.

  if joint.hasparent:  # Not hips
##    parent_trtr = joint.parent.trtr[-1]  # Last entry from parent
    parent_trtr = joint.parent.trtr[t]  # Dictionary-based rewrite

# 8/31/2008: dtransmat now excluded from non-hips computation since
# it's just identity anyway.
##    localtoworld = dot(parent_trtr,dot(joint.stransmat,dtransmat))
    localtoworld = dot(parent_trtr,joint.stransmat)

  else:  # Hips
#cgkit#    localtoworld = joint.stransmat * dtransmat
    localtoworld = dot(joint.stransmat,dtransmat)

#cgkit#  trtr = localtoworld * drotmat
  trtr = dot(localtoworld,drotmat)

##  joint.trtr.append(trtr)  # Whew
  joint.trtr[t] = trtr  # New dictionary-based approach    


#cgkit#  worldpos = localtoworld * ORIGIN  # worldpos should be a vec4
#
# numpy conversion: eliminate the matrix multiplication entirely,
# since all we're doing is extracting the last column of worldpos.
  worldpos = array([ localtoworld[0,3],localtoworld[1,3],        \
                      localtoworld[2,3], localtoworld[3,3] ])
##  joint.worldpos.append(worldpos)
  joint.worldpos[t] = worldpos  # Dictionary-based approach

  if DEBUG:
    print "  Joint %s: here are some matrices" % (joint.name)
    print "   stransmat:"
    print joint.stransmat
    if not (joint.hasparent):  # if hips
      print "   dtransmat:"
      print dtransmat
    print "   drotmat:"
    print drotmat
    print "   localtoworld:"
    print localtoworld
    print "   trtr:"
    print trtr
    print "  worldpos:", worldpos
    print

  newkeyframe = keyframe[counter:]  # Slices from counter+1 to end
  for child in joint.children:
    # Here's the recursion call.  Each time we call process_bvhkeyframe,
    # the returned value "newkeyframe" should shrink due to the slicing
    # process
    newkeyframe = process_bvhkeyframe(newkeyframe, child, t, DEBUG=DEBUG)
    if(newkeyframe == 0):  # If retval = 0
      print "Passing up fatal error in process_bvhkeyframe"
      return(0)
  return newkeyframe



###############################
# PROCESS_BVHFILE function

def process_bvhfile(filename, DEBUG=0):

# 9/11/08: the caller of this routine should cover possible exceptions.
# Here are two possible errors:
#  IOError: [Errno 2] No such file or directory: 'fizzball'
#  raise SyntaxError, "Syntax error in line %d: 'HIERARCHY' expected, \
#    got '%s' instead"%(self.linenr, tok)

# Here's some information about the two mybvh calls:
#
# mybvh.read() returns a readbvh instance:
#  retval from readbvh() is  <skeleton.readbvh instance at 0x176dcb0>
# So this isn't useful for error-checking.
#
# mybvh.read() returns None on success and throws an exception on failure.

  print "Reading BVH file...",
  #print "hello1";
  mybvh = readbvh(filename)  # Doesn't actually read the file, just creates
                         # a readbvh object and sets up the file for
                         # reading in the next line.
  
  retval = mybvh.read()  # Reads and parses the file.
  #print "hello2";
  hips = process_bvhnode(mybvh.root)  # Create joint hierarchy
  print "done"

  print "Building skeleton...",
  myskeleton = skeleton(hips, keyframes = mybvh.keyframes,    \
                          frames=mybvh.frames, dt=mybvh.dt)
  print "done"
  if DEBUG:
    print "skeleton is: ", myskeleton
  return(myskeleton)
