#!/usr/bin/env python

from Tkinter import Tk, IntVar, mainloop, Toplevel, BOTTOM, LEFT, W, \
    Button, Label
from tkFileDialog import askopenfilename
from transport import Transport, Playbar, Viewport
from camera import Camera
from menu import Menubar
from geo import worldvert, screenvert, worldedge, screenedge, grid_setup
from skeleton import skeleton, process_bvhfile
import profile
import sys

CANVAS_MINSIZE = 500


###########################################
# KEYBOARD CALLBACKS
###########################################
# Unfortunately I need to define functions here for the move keys 
# because the Camera object (in camera.py) can't call the redraw routine
# (in test4.py)

def MoveL(event):
    global mycamera
    global myviewport
    global mymenu
    global redraw_grid
    global redraw_axes
    redraw_grid = 1
    redraw_axes = 1
    mycamera.MoveL()
    if mymenu.readout:
      myviewport.draw_readout(mycamera)
    redraw()

def MoveR(event):
    global mycamera
    global myviewport
    global mymenu
    global redraw_grid
    global redraw_axes
    redraw_grid = 1
    redraw_axes = 1
    mycamera.MoveR()
    if mymenu.readout:
      myviewport.draw_readout(mycamera)
    redraw()

def MoveUp(event):
    global mycamera
    global myviewport
    global mymenu
    global redraw_grid
    global redraw_axes
    redraw_grid = 1
    redraw_axes = 1
    mycamera.MoveUp()
    if mymenu.readout:
      myviewport.draw_readout(mycamera)
    redraw()

def MoveDown(event):
    global mycamera
    global myviewport
    global mymenu
    global redraw_grid
    global redraw_axes
    redraw_grid = 1
    redraw_axes = 1
    mycamera.MoveDown()
    if mymenu.readout:
      myviewport.draw_readout(mycamera)
    redraw()

def MoveFd(event):
    global mycamera
    global myviewport
    global mymenu
    global redraw_grid
    global redraw_axes
    redraw_grid = 1
    redraw_axes = 1
    mycamera.MoveFd()
    if mymenu.readout:
      myviewport.draw_readout(mycamera)
    redraw()    

def MoveBack(event):
    global mycamera
    global myviewport
    global mymenu
    global redraw_grid
    global redraw_axes
    redraw_grid = 1
    redraw_axes = 1
    mycamera.MoveBack()
    if mymenu.readout:
      myviewport.draw_readout(mycamera)
    redraw()

def RotL(event):
    global mycamera
    global myviewport
    global mymenu
    global redraw_grid
    global redraw_axes
    redraw_grid = 1
    redraw_axes = 1
    mycamera.RotL()
    if mymenu.readout:
      myviewport.draw_readout(mycamera)
    redraw()

def RotR(event):
    global mycamera
    global myviewport
    global mymenu
    global redraw_grid
    global redraw_axes
    redraw_grid = 1
    redraw_axes = 1
    mycamera.RotR()
    if mymenu.readout:
      myviewport.draw_readout(mycamera)
    redraw()


#############################################
# RESIZE CALLBACK
#############################################
# This callback is triggered by the <Config> event for the Viewport
# frame, which contains our canvas.
def canvas_frame_change(event):
  global myviewport
  global mycamera
  global redraw_grid
  global redraw_axes
  DEBUG = 0
  if DEBUG:
    print "Got configure for event ", event
    print " widget = %s, width = %d, height = %d" % \
            (event.widget, event.width, event.height)

# The first time Tk calls this callback will be during initial window
# setup.  The Viewport() constructor initializes xframesize (and
# yframesize) to -1, so if xframesize is -1, this callback knows that
# we don't actually need to do anything to the canvas, rather we just
# record the actual frame width and height.
  if myviewport.framewidth == -1:
        myviewport.framewidth = event.width
        myviewport.frameheight = event.height
  elif ( (myviewport.framewidth != event.width) or \
                  (myviewport.frameheight != event.height)):
    if DEBUG:
      print "canvas_frame_change: time to resize the canvas!"
    myviewport.framewidth = event.width
    myviewport.frameheight = event.height

# First we set the new canvas size based on the new frame size,
# then we scale the camera aspect ratio to match the canvas aspect
# ratio.  The initial (constructor-time) values of the camera's cfx,cfy
# act as the base value against which we scale up.
    myviewport.canvaswidth = max(myviewport.framewidth-2, CANVAS_MINSIZE)
    myviewport.canvasheight = max(myviewport.frameheight-2, CANVAS_MINSIZE)

    mycamera.cfx = mycamera.basecfx * myviewport.canvaswidth / CANVAS_MINSIZE
    mycamera.cfy = mycamera.basecfy * myviewport.canvasheight / CANVAS_MINSIZE

# Now resize the actual canvas
    myviewport.canvas.config(width=myviewport.canvaswidth, \
                                 height=myviewport.canvasheight)

    if DEBUG:
        print " Resized canvas and camera aspect ratio."
        print " New canvas w,h: (%d, %d)" % (myviewport.canvaswidth,   \
                                                myviewport.canvasheight)
        print " New camera cfx,cfy: (%d, %d)" % (mycamera.cfx, mycamera.cfy)
    redraw_grid = 1
    redraw_axes = 1
    redraw()
        



###############################################
# TRANSPORT BUTTON CALLBACKS
###############################################
# We define these here because these callbacks need access to global
# variables, which they can't get if these functions are in transport.py
#
# And since the class constructor doesn't set up the callbacks, we have to
# do so ourselves after creating the Transport -- see the main code where
# we call Transport()

def onBegin():
    global slidert
    global myskeleton
    global skelscreenedges
#    print "begin button clicked"
    if not myskeleton: return  # Get out if myskeleton doesn't yet exist
    slidert.set(1)
    myskeleton.populate_skelscreenedges(skelscreenedges, slidert.get(), \
                                        DEBUG=0)
    redraw()


def onEnd():
#    print "end button clicked"
    global slidert
    global myskeleton
    global skelscreenedges
    if not myskeleton: return  # Get out if myskeleton doesn't yet exist
    slidert.set(myskeleton.frames)
    myskeleton.populate_skelscreenedges(skelscreenedges, slidert.get(), \
                                        DEBUG=0)
    redraw()


######
# PLAY
# When the user clicks play, we don't immediately step forward
# a frame.  Instead we just set mytransport.playing and set up
# PlayScheduler for a callback.
def onPlay():
    global mytransport
    global myskeleton
#    print "play button clicked"
    if not myskeleton: return  # Get out if myskeleton doesn't yet exist
    # if mytransport.playing is already 1, no need to do anything
    if not mytransport.playing:
      mytransport.playing = 1
      msec = int(myskeleton.dt * 1000)
      if(msec < 8): msec = 8  # Preserve speed sanity, max 125fps
      mytransport.after(msec, PlayScheduler)

##########
# PlayScheduler: called indirectly via Tk's after() function
# Every time we call this function, we should advance one slidert
# position unless we're at the end.

def PlayScheduler():
#    DEBUG = 0 
    global mytransport
    global slidert
    global myskeleton
    global skelscreenedges

    t = slidert.get()
#    if DEBUG:
#        print "PlayScheduler starting, t=",t
    if (t == myskeleton.frames):
        mytransport.playing = 0  # Stop when we run out of frames
        return()  # Just to be clear that we exit here

    else:  # This is now similar to onStepfd()
      msec = int(myskeleton.dt * 1000)
      if(msec < 8): msec = 8   # Preserve speed sanity, max 125fps

# Testing shows that frame rates above 30fps can be a problem --
# playback fails because this callback routine is being called faster
# than the display update code can run.  So if the frame rate is 30fps
# (30fps is 33msec per frame, thus the >30 test), THEN we can 
# reschedule this routine PRIOR to doing the math and display work.
# But if the frame rate is faster than 30fps, we'll call mytransport.after
# later.
      if mytransport.playing and msec >30:
        # DO NOT use "PlayScheduler()" -- you must write it as "PlayScheduler"
        mytransport.after(msec, PlayScheduler)  

      slidert.set(t+1)
#      if DEBUG:
#        print " PlayScheduler set t to %d, calling populate_sse" %     \
#                         (slidert.get())
      myskeleton.populate_skelscreenedges(skelscreenedges, slidert.get(), \
                                        DEBUG=0)
      redraw()

#      if DEBUG:
#          print "PlayScheduler: mytransport.playing =", mytransport.playing

# Rescheduling for high-frame-rate animations
      if mytransport.playing and msec <=30:
        mytransport.after(msec, PlayScheduler)  


def onStop():
    global mytransport
#    print "stop button clicked"
    mytransport.playing = 0

def onStepback():
    global slidert
    global myskeleton
    global skelscreenedges
    if not myskeleton: return  # Get out if myskeleton doesn't yet exist
    x = slidert.get()
    if x>1:
        slidert.set(x-1)
#    print "stepback button clicked, slidert=", slidert.get()
    myskeleton.populate_skelscreenedges(skelscreenedges, slidert.get(), \
                                        DEBUG=0)
    redraw()

def onStepfd():
    global slidert
    global myskeleton
    global skelscreenedges
    if not myskeleton: return  # Get out if myskeleton doesn't yet exist
    x = slidert.get()
    if (x < myskeleton.frames - 1):
      slidert.set(x+1)
#    print "stepfd button clicked, slidert=",slidert.get()
    myskeleton.populate_skelscreenedges(skelscreenedges, slidert.get(), \
                                        DEBUG=0)
    redraw()


# The slider's "command" option is unlike most other widget callbacks
# in that it passes us an argument containing the slider's current position.
def onSlider(value):
    global slidert
    if slidert.get() == 0:
        slidert.set(1)  # 0 not allowed
#     print "slider was slid, position = ", value

    if myskeleton:  # myskeleton = 0 on initial program run
      myskeleton.populate_skelscreenedges(skelscreenedges, slidert.get(), \
                                        DEBUG=0)
      redraw()

# End Transport button callbacks
#####################################




#################################################
# MENU CALLBACKS
#################################################

def open_file():      # read_file file_read load_file
  global root  # Root window
  global myskeleton
  global skelscreenedges
  global gridedges
  global slidert
  global myviewport
  global mycamera
  global mymenu
  global mytransport
  global redraw_grid
  global redraw_axes
  global file_prefix

# No, you aren't allowed to try to load a new BVH in the middle of playing
# back the current BVH... nice try.
  mytransport.playing = 0

  mycanvas = myviewport.canvas
  if file_prefix == 'NONE':
    filename = askopenfilename(title = 'Open BVH file', parent=root, \
               filetypes =[ ('BVH files', '*.bvh'), ('All files', '*')]     )
  else:
    filename = askopenfilename(title = 'Open BVH file', parent=root, \
               initialdir = file_prefix,                             \
               filetypes =[ ('BVH files', '*.bvh'), ('All files', '*')]     )

  print "filename = ",filename  # Remove this line later
  index = filename.rfind('/')  # Unix
  index2 = filename.rfind('\\') # Windows
  if index != -1:
    file_prefix = filename[0:index+1]
    print "File prefix is ", file_prefix
  elif index2 != -1:      
    file_prefix = filename[0:index2+1]
    print "File prefix is ", file_prefix      

  # askopenfilename also allows: initialdir = ''
  # "filename" will have length 0 if user cancels the open.
  if len(filename) > 0:
      try:
        myskeleton2 = process_bvhfile(filename,DEBUG=1)
     ## myskeleton2 = profile.run('process_bvhfile(FILE,DEBUG=0)')
      except IOError:
        string = "IO Error while attempting to read file."
        print string
        error_popup(string)
        return
      except SyntaxError:
        string = "Parse error in BVH file."
        print string
        error_popup(string)
        return
      except:
        string = "Unknown error while attempting to read file."
        print string
        error_popup(string)
        return

  # If we make it here then we've successfully read and parsed the BVH file,
  # and created myskeleton2

  # Undraw all grid edges
      for edge in gridedges:
          edge.undraw(mycanvas)
  # Undraw all skeleton edges
      for edge in skelscreenedges:
          edge.undraw(mycanvas)
  # Don't need to undraw axes - leave as-is

  # Reset slider to 1
      slidert.set(1)

# Say farewell to previous skeleton
      myskeleton = myskeleton2  

# Set camera position to something that will hopefully put the skeleton
# in view.  For Z we want something large so that we're set back from
# the skeleton.
      mycamera.t[0] = int((myskeleton.minx + myskeleton.maxx)/2)
      mycamera.t[1] = int((myskeleton.miny + myskeleton.maxy)/2)
      if (mycamera.t[1] < 10): mycamera.t[1] = 10
      mycamera.t[2] = myskeleton.maxz + 100
      mycamera.yrot = 0
      mycamera.Recompute()
      if mymenu.readout:
          myviewport.draw_readout(mycamera)

# Create skelscreenedges[] with sufficient space to handle one
# screenedge per skeleton edge.
      skelscreenedges = myskeleton.make_skelscreenedges(DEBUG=0, arrow='none',
                                                  circle=1)
# Give us some screen edges to display.
      myskeleton.populate_skelscreenedges(skelscreenedges, slidert.get(),  \
                                              DEBUG=0)
# print "skelscreenedges after population is:"
# print skelscreenedges

      myplaybar.resetscale(myskeleton.frames)
      gridedges = grid_setup(myskeleton.minx, myskeleton.minz, \
                   myskeleton.maxx, myskeleton.maxz, DEBUG=0)
      redraw_grid = 1
      redraw_axes = 1
      redraw()

################################################



#####
# Alternate version of open_file called by a ctrl-o, which passes
# an event in as an arg that we need to strip out.
def open_file2(event):
    open_file()



def error_popup(text):
  win = Toplevel()
  Button(win, text='OK', command=win.destroy).pack(side=BOTTOM)
  Label(win, text=text, anchor=W, justify=LEFT).pack(side=LEFT)
# Refuse to let the user do anything until window is dismissed
  win.focus_set()
  win.grab_set()
  win.wait_window()




def toggle_grid():
  global mymenu
  global gridedges
  global myviewport
  global redraw_grid
  mycanvas = myviewport.canvas
  if mymenu.grid:
      mymenu.grid = 0
      mymenu.settingsmenu.entryconfig(0, label='Grid on')
      for edge in gridedges:
# redraw() won't remove lines already drawn even if we set edge.drawme.
# So we have to undraw the grid lines here, then set edge.drawme to 0
# to block future draw attempts.
          edge.undraw(mycanvas)
          edge.drawme = 0
  else:
      mymenu.grid = 1
      mymenu.settingsmenu.entryconfig(0, label='Grid off')
      redraw_grid = 1  # redraw() won't draw the grid without this
      for edge in gridedges:
          edge.drawme = 1
  redraw()

      

def toggle_axes():
  global mymenu
  global axisedges
  global myviewport
  global redraw_axes
  mycanvas = myviewport.canvas  
  if mymenu.axes:
      mymenu.axes = 0
      mymenu.settingsmenu.entryconfig(1, label='Axes on')
      for edge in axisedges:
          edge.undraw(mycanvas)
          edge.drawme = 0
  else:
      mymenu.axes = 1
      mymenu.settingsmenu.entryconfig(1, label='Axes off')
      redraw_axes = 1
      for edge in axisedges:
          edge.drawme = 1
  redraw()



def toggle_readout():  # Camera xyz display
  global mymenu
  global myviewport
  global mycamera
  if mymenu.readout:
      mymenu.readout = 0
      myviewport.undraw_readout()
      mymenu.settingsmenu.entryconfig(2, label='Camera readout on')
  else:
      mymenu.readout = 1
      myviewport.draw_readout(mycamera)
      mymenu.settingsmenu.entryconfig(2, label='Camera readout off')




#####################################
# REDRAW
# Recomputes camspace and canvas-space coordinates of all edges and
# redraws them.
#
def redraw():
    global axisedges
    global skelscreenedges
    global gridedges
    global slidert
    global mycamera
    global myviewport
    global mymenu
    global redraw_grid  # flag
    global redraw_axes  # flag

    mycanvas = myviewport.canvas
    canvaswidth = myviewport.canvaswidth
    canvasheight = myviewport.canvasheight

    if mymenu.grid and redraw_grid:
      for edge in gridedges:
        edge.worldtocam(mycamera)
        edge.camtoscreen(mycamera, canvaswidth, canvasheight)
        edge.draw(mycanvas)
      redraw_grid = 0

    if mymenu.axes and redraw_axes:
      for edge in axisedges:
        edge.worldtocam(mycamera)  # Update cam coords
        edge.camtoscreen(mycamera, canvaswidth, canvasheight)
        edge.draw(mycanvas)
      redraw_axes = 0
      
    for screenedge in skelscreenedges:
##      print "Calling worldtocam for screenedge ", screenedge.descr
      screenedge.worldtocam(mycamera)
      screenedge.camtoscreen(mycamera, canvaswidth, canvasheight)        
##      print "PRINTOUT OF SCREENEDGE ", screenedge.descr
##      print screenedge
##      print
      screenedge.draw(mycanvas)



############################################
# MAIN PROGRAM STARTS HERE
############################################

root = Tk()
root.title('BVHPlay')

mymenu = Menubar(root)

mymenu.filemenu.entryconfig(0, command = open_file)
root.bind('<Control-Key-o>', open_file2)
mymenu.settingsmenu.entryconfig(0, command = toggle_grid)
mymenu.settingsmenu.entryconfig(1, command = toggle_axes)
mymenu.settingsmenu.entryconfig(2, command = toggle_readout)


mytransport = Transport()  # Create and pack a frame of transport buttons
mytransport.btn_begin.config(command = onBegin)
mytransport.btn_end.config(command = onEnd)
mytransport.btn_stop.config(command = onStop)
mytransport.btn_play.config(command = onPlay)
mytransport.btn_stepback.config(command = onStepback)
mytransport.btn_stepfd.config(command = onStepfd)

myplaybar = Playbar()
slidert = IntVar()  # Special magic integer that allows me to tie it
                     # to a Tk widget "variable" option, in this case
                     # for our slider
myplaybar.scale.config(variable = slidert)
slidert.set(1)  # DO NOT use "slidert = __"
myplaybar.scale.config(command = onSlider)

myviewport = Viewport(root, canvassize=CANVAS_MINSIZE)

mycamera = Camera(x=0, y=15, z=35, cfx=20, parallel=0,   \
                  ppdist=30, DEBUG=0)  # cfy not needed or allowed
## mycamera = Camera(x=10, y=15, z=10, parallel=1)
## print "MYCAMERA: ", mycamera

root.bind('<KeyPress-a>', MoveL)
root.bind('<KeyPress-d>', MoveR)
root.bind('<KeyPress-r>', MoveUp)
root.bind('<KeyPress-f>', MoveDown)
root.bind('<KeyPress-w>', MoveFd)
root.bind('<KeyPress-s>', MoveBack)
root.bind('<KeyPress-q>', RotL)
root.bind('<KeyPress-e>', RotR)


# Call Config() when CANVAS FRAME is resized.  We don't want to
# do this as root.bind() because then we get callback calls for every
# widget and frame on the screen whenever we resize the window.  We
# just want a callback for the frame that holds the canvas.
myviewport.bind('<Configure>', canvas_frame_change)  

# Must init myskeleton to 0.  At least one routine uses this as a test
# for whether a skeleton exists or not.
myskeleton = 0  
skelscreenedges = []
axisedges = []

# X axis
sv1 = screenvert(0.,0.,0.)
sv2 = screenvert(10.,0.,0.)
se1 = screenedge(sv1, sv2, color='red', description='red x axis')
axisedges.append(se1)


# Y axis
sv1 = screenvert(0.,0.,0.)
sv2 = screenvert(0.,10.,0.)
se1 = screenedge(sv1, sv2, color='green', description='green y axis')
axisedges.append(se1)


# Z axis
sv1 = screenvert(0.,0.,0.)
sv2 = screenvert(0.,0.,10.)
se1 = screenedge(sv1, sv2, color='blue', description='blue z axis')
axisedges.append(se1)
redraw_axes = 1


# Default grid prior to a skeleton load.
gridedges = grid_setup(-50, -50, 50, 50, DEBUG=0)
redraw_grid = 1  # Global flag - set to 1 when you move the camera please

file_prefix = 'NONE'

# redraw() only redraws edges, not the camera readout, because the
# camera readout only changes when the camera moves, not when the
# skeleton animates.  If I were to have redraw() call draw_readout,
# we'd erase and redraw the readout every timestep, which is a waste.
if mymenu.readout:
    myviewport.draw_readout(mycamera)

redraw()
mainloop()
