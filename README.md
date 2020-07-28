# Subwindow organizer for krita
Krita plugin that helps keep order of subwindows.

## Requirement:
'subwindow' mode is enabled, instead of the default 'tabs'.\
Can be configured in *Settings > Configure Krita... > General > Window > Multiple Document Mode.*

## Installation:
-get the krita resources folder location: *"Settings > Manage Resources > Open Resource Folder".*\
-in 'pykrita' folder, put downloaded 'pykrita' contents.\
-in 'actions' folder, put downloaded 'actions' contents.\
-restart krita.\
-activate the addon: *Settings > Configure Krita... > Python Plugin Manager > Subwindow Organizer (ON).*\
-restart krita again.\
-new actions are on the bottom of "View" menu. Keyboard shortcuts can be changed in settings.

## Features:
**-responsive subwindows:** never get larger than workspace. Adjusts to krita window resize, dockers resize, togglign fullscreen and canvas-only modes.\
**-automatic maximize:** always toggled when amount of subwindows changes to one.\
**-open as floating windows:** all newly created subwindows open as 'always on top' and hover over the canvas.\
**-"split screen" mode** (default): second subwindow (main reference image) adjusts its size to fit in the space remained by the first one (painting canvas).\
**-"one window" mode:** all views are floaters but the canvas.\
**-snap floaters to borders:** floaters can't go out of the workspace borders, which would cause it to create sliders.\
**-true maximize:** can maximize one window, without "always on top" windows appearing.

## User actions:
**-Toggle split screen:** *"View > Split screen"* (ctrl+alt+n)\
Switches between two modes.\
*turn ON:* the active subwindow is being taken as a reference image (random when main canvas selected).\
*turn OFF:* reference image becomes a floating window.

**-Organizing action:** *"View > Pick subwindow"* (ctrl+alt+m)\
Gives the ability to switch subwindows with each other. Uses active subwindow.\
-"split screen" mode:\
    -when the 'floater' is activated, make it a 'main reference'. (switching between multiple reference images)\
    -when the 'canvas' or the 'main reference' is activated, they take each others place. (gives the ability to change the main drawing canvas).\
-"one window" mode:\
    -when the 'floater' is activated, open it in main canvas (which becomes a floater)\
    -when the 'canvas' is activated, the tool is idle.
 
**-maximize** (override): when one window is maximized by the user, all the rest are not visible, even when the "always on top" is toggled.\
**-minimize** (override): only floating windows can get minimized.

## Known issues:
-pressing minimize on maximized window makes it impossible to demaximize (such document have to be saved and closed)\
-after going from maximize to normal, split screen looses minimal width for both windows (one can take whole space if krita window is shrinked a lot)\
-not working in "tabs" mode - currently won't install in this case and will put a message box, but still this mode can be turned on during add-on work.\
-will not work very well with the default 'tile' and 'cascade' organizers.
-minimized window won't be automatically put in the background, if the background one gets closed.

## To be done:
-remove title bar for the background windows and replacing them with a custom widget (maximize and close) as the minimize is idle, and they can't be moved apart from resizing width.\
-ability to toggle the whole add-on without closing krita - will solve the tabs mode issue.\
-allow to swap floater and background window by drag-and-dropping the latter to the floater.

**-Main task:** integrate my "reference tracking canvas" script. When this mode is enabled, panning, rotating and mirroring the canvas, would cause the reference image to do the same. Current script don't apply pan and runs on keyboard action, but the canvas could be continuously tracked.
