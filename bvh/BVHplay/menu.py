#
# from Tkinter import *

from Tkinter import Menu, Toplevel, Button, Label, BOTTOM, LEFT, W

########################################

class Menubar:
    def __init__(self, parentwin):
        # This code based on rat book pp. 500-501
        topmenu = Menu(parentwin)  # Create the Menu object
        parentwin.config(menu=topmenu)  # Tell the window to use the Menu
        self.parentwin = parentwin

        filemenu = Menu(topmenu, tearoff=0)
        self.filemenu = filemenu
        retval = filemenu.add_command(label='Open... (ctrl-o)')
        retval = filemenu.add_command(label='Quit', command = parentwin.quit)
        topmenu.add_cascade(label='File', menu=filemenu)  # Don't forget this

        settingsmenu = Menu(topmenu, tearoff=0)
        self.settingsmenu = settingsmenu
        retval = settingsmenu.add_command(label='Grid off')
        retval = settingsmenu.add_command(label='Axes off')
        retval = settingsmenu.add_command(label='Camera readout off')
        topmenu.add_cascade(label='Settings', menu=settingsmenu)
        self.grid = 1  # On by default
        self.axes = 1
        self.readout = 1
    
        helpmenu = Menu(topmenu, tearoff=0)
        self.helpmenu = helpmenu
        helpmenu.add_command(label='About BVHPlay', command=self.about)
        helpmenu.add_command(label='Command list', command=self.commandlist)
        topmenu.add_cascade(label='Help', menu=helpmenu)
# We don't pack() menus.

    def commandlist(self):
        win = Toplevel()  # Creates an independent window
        t1 = " Camera control:"
        t2 = " a -- move camera left (strafe left)"
        t3 = " d -- move camera right (strafe right)"
        t4 = " s -- move camera back"
        t5 = " w -- move camera forward"
        t6 = " q -- rotate camera left"
        t7 = " e -- rotate camera right"
        t8 = " r -- move camera up"
        t9 = " f -- move camera down"
        t9a = "Hold down a key to trigger autorepeat."

        t10 = " Slider:"
        t11 = " Drag the slider left and right to scrub through keyframes."
        t12 = " The first frame is always frame 1 (there is no frame 0)."
        t12a = " You can also use the camera controls while you drag the slider."

        t13 = " Transport buttons:"
        t14 = " From left to right, the meanings of the buttons are as follows: "
        t15 = " -- Go to first frame of BVH sequence"
        t16 = " -- Step back 1 frame"
        t17 = " -- Stop"
        t18 = " -- Play"
        t19 = " -- Step forward 1 frame"
        t20 = " -- Go to last frame"

        t21 = " Window resize:"
        t22 = " Yes!  You can resize the application window and the animation"
        t23 = " display area will resize appropriately.  You can even resize"
        t24 = " during BVH playback."

        text1 = "\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n\n%s\n\n"   \
            % (t1,t2,t3,t4,t5,t6,t7,t8,t9,t9a)
        text2 = "%s\n%s\n%s\n%s\n\n" % (t10,t11,t12,t12a)
        text3 = "%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n" \
            % (t13,t14,t15,t16,t17,t18,t19,t20)
        text4 = "\n%s\n%s\n%s\n%s\n" % (t21,t22,t23,t24)
        text = text1 + text2 + text3 + text4

        Button(win, text='Close', command=win.destroy).pack(side=BOTTOM)
        Label(win, text=text, anchor=W, justify=LEFT).pack(side=LEFT)

        # See snake book p. 440.  Takes over the universe
#        win.focus_set()
#        win.grab_set()
#        win.wait_window()



    def about(self):
      win = Toplevel()
      t1 = " Welcome to BVHplay, a free BVH player.  v1.00"

      t2 = " Home site for this program: www.cgspeed.com"
      t3 = " The source code is also available."

      t4 = " Copyright (c) 2008 Bruce Hahne\n"
      t5 = " Author's email address: hahne@io.com\n\n"

      t6 = " This program and its source code are usable by others"
      t7 = " under the terms of version 3 of the Gnu General Public"
      t8 = " license (dated June 29, 2007), which is available at "
      t9 = " www.gnu.org/licenses/gpl.html"

      t10 = " BVHplay uses portions of the Python Computer Graphics Kit (cgkit)"
      t11 = " and the numpy mathematics library.  See the associated README"
      t12 = " distributed with this program for information and licensing"
      t13 = " related to these libraries."

      t14 = " This program comes with no warranty.\n"


      text1 = "\n%s\n\n%s\n%s\n\n" % (t1, t2, t3)
      text2 = t4 + t5
      text3 = "%s\n%s\n%s\n%s\n\n" % (t6, t7, t8, t9)
      text4 = "%s\n%s\n%s\n%s\n\n" % (t10, t11, t12, t13)
      text5 = t14

      text = text1 + text2 + text3 + text4 + text5

      Button(win, text='Close', command=win.destroy).pack(side=BOTTOM)
      Label(win, text=text, anchor=W, justify=LEFT).pack(side=LEFT)
