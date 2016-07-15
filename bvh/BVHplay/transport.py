
from Tkinter import Frame, BOTTOM, LEFT, S, NW, X, BitmapImage, Button, \
    Scale, YES, BOTH, Canvas
from math import log10, pow, floor, degrees

#####################
# TRANSPORT BUTTONS

DATA_BITMAP_BEGIN = """
#define Xbitmap_width 20
#define Xbitmap_height 21
static unsigned char Xbitmap_bits[] = {
        0x00, 0x00, 0xf0, 0x0c, 0x60, 0xf0, 0x0c, 0x70, 0xf0, 
        0x0c, 0x78, 0xf0, 0x0c, 0x7c, 0xf0, 0x0c, 0x7e, 0xf0, 
        0x0c, 0x7f, 0xf0, 0x8c, 0x7f, 0xf0, 0xcc, 0x7f, 0xf0, 
        0xec, 0x7f, 0xf0, 0xfc, 0x7f, 0xf0, 0xec, 0x7f, 0xf0, 
        0xcc, 0x7f, 0xf0, 0x8c, 0x7f, 0xf0, 0x0c, 0x7f, 0xf0, 
        0x0c, 0x7e, 0xf0, 0x0c, 0x7c, 0xf0, 0x0c, 0x78, 0xf0, 
        0x0c, 0x70, 0xf0, 0x0c, 0x60, 0xf0, 0x00, 0x00, 0xf0, 
      };
"""

DATA_BITMAP_END = """
#define Xbitmap_width 20
#define Xbitmap_height 21
static unsigned char Xbitmap_bits[] = {
        0x00, 0x00, 0xf0, 0x60, 0x00, 0xf3, 0xe0, 0x00, 0xf3, 
        0xe0, 0x01, 0xf3, 0xe0, 0x03, 0xf3, 0xe0, 0x07, 0xf3, 
        0xe0, 0x0f, 0xf3, 0xe0, 0x1f, 0xf3, 0xe0, 0x3f, 0xf3, 
        0xe0, 0x7f, 0xf3, 0xe0, 0xff, 0xf3, 0xe0, 0x7f, 0xf3, 
        0xe0, 0x3f, 0xf3, 0xe0, 0x1f, 0xf3, 0xe0, 0x0f, 0xf3, 
        0xe0, 0x07, 0xf3, 0xe0, 0x03, 0xf3, 0xe0, 0x01, 0xf3, 
        0xe0, 0x00, 0xf3, 0x60, 0x00, 0xf3, 0x00, 0x00, 0xf0, 
      };
"""

DATA_BITMAP_STOP = """
#define Xbitmap_width 20
#define Xbitmap_height 21
static unsigned char Xbitmap_bits[] = {
        0x00, 0x00, 0xf0, 0x00, 0x00, 0xf0, 0x00, 0x00, 0xf0, 
        0x00, 0x00, 0xf0, 0xf8, 0xff, 0xf1, 0xf8, 0xff, 0xf1, 
        0xf8, 0xff, 0xf1, 0xf8, 0xff, 0xf1, 0xf8, 0xff, 0xf1, 
        0xf8, 0xff, 0xf1, 0xf8, 0xff, 0xf1, 0xf8, 0xff, 0xf1, 
        0xf8, 0xff, 0xf1, 0xf8, 0xff, 0xf1, 0xf8, 0xff, 0xf1, 
        0xf8, 0xff, 0xf1, 0xf8, 0xff, 0xf1, 0x00, 0x00, 0xf0, 
        0x00, 0x00, 0xf0, 0x00, 0x00, 0xf0, 0x00, 0x00, 0xf0, 
      };
"""

DATA_BITMAP_PLAY = """
#define Xbitmap_width 20
#define Xbitmap_height 21
static unsigned char Xbitmap_bits[] = {
        0x30, 0x00, 0xf0, 0x70, 0x00, 0xf0, 0xf0, 0x00, 0xf0, 
        0xf0, 0x01, 0xf0, 0xf0, 0x03, 0xf0, 0xf0, 0x07, 0xf0, 
        0xf0, 0x0f, 0xf0, 0xf0, 0x1f, 0xf0, 0xf0, 0x3f, 0xf0, 
        0xf0, 0x7f, 0xf0, 0xf0, 0xff, 0xf0, 0xf0, 0x7f, 0xf0, 
        0xf0, 0x3f, 0xf0, 0xf0, 0x1f, 0xf0, 0xf0, 0x0f, 0xf0, 
        0xf0, 0x07, 0xf0, 0xf0, 0x03, 0xf0, 0xf0, 0x01, 0xf0, 
        0xf0, 0x00, 0xf0, 0x70, 0x00, 0xf0, 0x30, 0x00, 0xf0, 
      };
"""

DATA_BITMAP_STEPBACK = """
#define Xbitmap_width 20
#define Xbitmap_height 21
static unsigned char Xbitmap_bits[] = {
        0x00, 0x00, 0xf0, 0x00, 0x98, 0xf1, 0x00, 0x9c, 0xf1, 
        0x00, 0x9e, 0xf1, 0x00, 0x9f, 0xf1, 0x80, 0x9f, 0xf1, 
        0xc0, 0x9f, 0xf1, 0xe0, 0x9f, 0xf1, 0xf0, 0x9f, 0xf1, 
        0xf8, 0x9f, 0xf1, 0xfc, 0x9f, 0xf1, 0xf8, 0x9f, 0xf1, 
        0xf0, 0x9f, 0xf1, 0xe0, 0x9f, 0xf1, 0xc0, 0x9f, 0xf1, 
        0x80, 0x9f, 0xf1, 0x00, 0x9f, 0xf1, 0x00, 0x9e, 0xf1, 
        0x00, 0x9c, 0xf1, 0x00, 0x98, 0xf1, 0x00, 0x00, 0xf0, 
      };
"""

DATA_BITMAP_STEPFD = """
#define Xbitmap_width 20
#define Xbitmap_height 21
static unsigned char Xbitmap_bits[] = {
        0x00, 0x00, 0xf0, 0x98, 0x01, 0xf0, 0x98, 0x03, 0xf0, 
        0x98, 0x07, 0xf0, 0x98, 0x0f, 0xf0, 0x98, 0x1f, 0xf0, 
        0x98, 0x3f, 0xf0, 0x98, 0x7f, 0xf0, 0x98, 0xff, 0xf0, 
        0x98, 0xff, 0xf1, 0x98, 0xff, 0xf3, 0x98, 0xff, 0xf1, 
        0x98, 0xff, 0xf0, 0x98, 0x7f, 0xf0, 0x98, 0x3f, 0xf0, 
        0x98, 0x1f, 0xf0, 0x98, 0x0f, 0xf0, 0x98, 0x07, 0xf0, 
        0x98, 0x03, 0xf0, 0x98, 0x01, 0xf0, 0x00, 0x00, 0xf0, 
      };
"""

#########
# TRANSPORT class
#
# Contains the transport button set (play, stop, etc.)
# Does not contain the slider.
#
# Don't create one of these until AFTER you do "root = Tk()"
# otherwise you might get the "too early to create bitmap" error.
class Transport(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.pack(side=BOTTOM, anchor=S)
        # These must go AFTER root = Tk()
        self.bitmap_begin =  BitmapImage(data=DATA_BITMAP_BEGIN)
        self.bitmap_end = BitmapImage(data=DATA_BITMAP_END)
        self.bitmap_stop =  BitmapImage(data=DATA_BITMAP_STOP)
        self.bitmap_play =  BitmapImage(data=DATA_BITMAP_PLAY)
        self.bitmap_stepback =  BitmapImage(data=DATA_BITMAP_STEPBACK)
        self.bitmap_stepfd =  BitmapImage(data=DATA_BITMAP_STEPFD)        

# Depcrecated: we no longer set up the COMMANDs here.
#        self.btn_begin = Button(self, image=self.bitmap_begin, 
#                                command = self.onBegin)

        self.btn_begin = Button(self, image=self.bitmap_begin) 
        self.btn_end = Button(self, image=self.bitmap_end)
        self.btn_stop = Button(self, image=self.bitmap_stop)
        self.btn_play = Button(self, image=self.bitmap_play)
        self.btn_stepback = Button(self, image=self.bitmap_stepback) 
        self.btn_stepfd = Button(self, image=self.bitmap_stepfd) 

        self.btn_begin.pack(side=LEFT)
        self.btn_stepback.pack(side=LEFT)
        self.btn_stop.pack(side=LEFT)
        self.btn_play.pack(side=LEFT)
        self.btn_stepfd.pack(side=LEFT)
        self.btn_end.pack(side=LEFT)

        self.playing = 0  # Set to 1 when user presses play, 0 on stop

##################
# VIEWPORT class
# This holds a Tk canvas object in a frame
# The "size" argument to the constructor is the initial heigh and
# width of the canvas widget, not of the frame (which is very slightly
# larger).

class Viewport(Frame):
    def __init__(self, parent=None, canvassize=500):
        Frame.__init__(self, parent)

# Incredibly, it's a pain to extract the canvas width,height directly
# from the canvas widget itself, so we store these here and push them
# down to the actual canvas widget whenever they change.
        self.canvaswidth = canvassize
        self.canvasheight = canvassize

# The flag for whether we display the camera or not is in menu.py
# as part the of menubar class.
        self.readoutid = 0

        self.framewidth = -1  # Will be set elsewhere
        self.frameheight = -1
        self.pack(side=BOTTOM, anchor=S, expand=YES, fill=BOTH)
        self.canvas = Canvas(self, width=canvassize, \
                  height=canvassize, bg='white')
        self.canvas.pack()


###########################
# DRAW_READOUT class function:
# - Build the text strings for the camera readout display
# - If a readout is already on the screen, remove it
# - Draw the new readout
# This routine does NOT check the menu.py variable that determines
# whether or not we should actually draw the readout.  It's the
# caller's responsibility to do that.
#
    def draw_readout(self, camera):
        text1 = 'Camera:'
        text2 = "x=%d y=%d z=%d" % (round(camera.t[0]), \
                          round(camera.t[1]), round(camera.t[2]))
        text3 = "Rotation = %d" % (round(degrees(camera.yrot)))
        text4 = "%s\n%s\n%s" % (text1, text2, text3)

        if self.readoutid:
          self.canvas.delete(self.readoutid)
        self.readoutid = self.canvas.create_text(5,5, text=text4, \
                                         anchor=NW)


    def undraw_readout(self):
      if self.readoutid:
        self.canvas.delete(self.readoutid)
        self.readoutid = 0


##################

class Playbar(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.pack(side=BOTTOM, anchor=S, fill=X)
        self.scale = Scale(self, from_=0, to=1, sliderlength = 10,
                showvalue=YES, tickinterval=10,
                orient='horizontal')
        self.scale.pack(fill=X)
        # We don't set the initial value of the scale here because
        # that's done by tying it to the global variable "slidert"

# Resetscale: takes a frame count and resets scale parms appropriately
    def resetscale(self, frames):
        temp = floor(log10(frames))
        tickinterval = int(pow(10,temp))
        if(tickinterval<1): tickinterval = 1
        self.scale.config(to=frames, tickinterval=tickinterval)

