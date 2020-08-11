from krita import *

DEFAULTCOLUMNRATIO = 0.33 #as part of the workspace width
MINIMALCOLUMNWIDTH = 100 #in pixels

#size of newly created window
DEFAULTFLOATERSIZE = 0.1 #0-1 value as the part of the workspace area
# DEFAULTFLOATERSIZE = 270000 #integer value as the area in pixels 
# DEFAULTFLOATERSIZE = (400,400) #fixed size in pixels (width, height)
# DEFAULTFLOATERSIZE = (500,0) #fixed width, height counted to fit the document ratio
# DEFAULTFLOATERSIZE = (0,500) #fixed height
# DEFAULTFLOATERSIZE = None #don't resize - default krita size

SNAPDISTANCE = 30 #snapping floaters to edge

SPLITMODERANGE = [0.3, 0.6] #will enter split mode if cursor on the left or right of workspace, and height between 30% and 60% of the canvas. Enter impossible range like [1,0] to fully disable splitting

SPLITBYDEFAULT = False #when True, every time a second window is open, it will appear in a split mode
REFPOSITION = "left" #side on which this window will appear (can be changed by manually placing window on other side) 

SOFTPROOFING = True #automatically set softproofing on, when opening the overview