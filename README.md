# Subwindow organizer for krita
Krita plugin that helps keep order of subwindows.

## What's new in 1.1.0:
# Features
- drag and drop backgrounder into floater or another backgrounder to swap them
- go into split-mode by dragging a floater to left or right border of the screen
- go into one-window mode by dragging reference window download
- reference can be displayed on the left or right part of the screen

# Bugfixes

- pressing minimize on maximized window makes it impossible to demaximize (such document have to be saved and closed)
- minimized window won't be automatically put in the background, if the background one gets closed.
- opening new window don't work when background window is maximized (split mode)

## Requirement:
'subwindow' mode is enabled, instead of the default 'tabs'.\
Can be configured in *Settings > Configure Krita... > General > Window > Multiple Document Mode.*

## Installation:
- on github, click the green button 'code' and pick 'download zip'. Do not extract it.
- go to *Tools > Scripts > Import Python Plugin* and pick the downloaded .zip file
- restart krita.
- activate the addon: *Settings > Configure Krita... > Python Plugin Manager > Subwindow Organizer (ON).*
- restart krita again.
- new actions are on the bottom of "View" menu. Keyboard shortcuts can be changed in settings.

## Features:
- **responsive subwindows:** never get larger than workspace. Adjusts to krita window resize, dockers resize, togglign fullscreen and canvas-only modes.
- **automatic maximize:** always toggled when amount of subwindows changes to one.
- **open as floating windows:** all newly created subwindows open as 'always on top' and hover over the canvas.
- **"split screen" mode** (default): second subwindow (main reference image) adjusts its size to fit in the space remained by the first one (painting canvas).
- **"one window" mode:** all views are floaters but the canvas.
- **drag and drop**: gesture actions to easily swap windows and modes.
- **snap floaters to borders:** floaters can't go out of the workspace borders, which would cause it to create sliders.
- **true maximize:** can maximize one window, without "always on top" windows appearing.

## User actions:
- **Toggle split screen:** *"View > Split screen"* (ctrl+alt+n)\
Switches between two modes.\
*turn ON:* the active subwindow is being taken as a reference image (random when main canvas selected).\
*turn OFF:* reference image becomes a floating window.

go into split-mode by dragging a floater to left or right border of the screen
go into one-window mode by dragging reference window download

- **Organizing action:** *"View > Pick subwindow"* (ctrl+alt+m)\
Gives the ability to switch subwindows with each other. Uses active subwindow.
- "split screen" mode:\
    -when the 'floater' is activated, make it a 'main reference'. (switching between multiple reference images)\
    -when the 'canvas' or the 'main reference' is activated, they take each others place. (gives the ability to change the main drawing canvas).\
- "one window" mode:\
    -when the 'floater' is activated, open it in main canvas (which becomes a floater)\
    -when the 'canvas' is activated, the tool is idle.
 
drag and drop backgrounder into floater or another backgrounder to swap them
 
- **maximize** (override): when one window is maximized by the user, all the rest are not visible, even when the "always on top" is toggled.
- **minimize** (override): only floating windows can get minimized.

## Known issues:

- after going from maximize to normal, split screen looses minimal width for both windows (one can take whole space if krita window is shrinked a lot)
- not working in "tabs" mode - currently won't install in this case and will put a message box, but still this mode can be turned on during add-on work.
- will not work very well with the default 'tile' and 'cascade' organizers.
- still possible for the script to crash on drag and drop action, but it is rare and hard to reproduce. It will not make you lose your artwork.

## To be done:
- ability to toggle the whole add-on without closing krita - will solve the tabs mode issue.

- **Main task:** integrate my "reference tracking canvas" script. When this mode is enabled, panning, rotating and mirroring the canvas, would cause the reference image to do the same. Current script don't apply pan and runs on keyboard action, but the canvas could be continuously tracked.
