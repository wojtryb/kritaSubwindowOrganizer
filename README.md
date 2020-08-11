# Subwindow organizer for krita
Krita plugin that helps keep order of subwindows.

## What's new in 1.2.0:
- tabs support and toggling the plugin - the plugin can be switched on and off, and switching between tabs and subwindows in krita settings, will not break it.
- reworked split screen - now by default there is only one background window. Dragging the floater to the right or left side places it in a split screen. To go out the split screen, any background window has to be moved down.
- move floater to bottom of the screen to minimize it, and move minimized window up to deminimize.
- all new floaters are opened in windows with the ratio of the document inside. Newly opened window always takes 10% of workspace area to support different resolutions. This relative size can be configured in config.py file. Other modes can be picked there too.
- added the "open overview" action that opens the main drawing window in another view with soft proofing enabled. Desired to be used as the grayscale overview, but it has to be manually picked in Settings > Configure krita... > Color Management > Soft Proofing > Model > grayscale
- preventing the user from breaking actions: manually unsetting "always on top" mode, tile and cascade options when the plugin is on.
- floaters will resize down, when krita window is made too small to prevent them from being bigger than workspace.

## Requirement:
'subwindow' mode is enabled, instead of the default 'tabs'.\
Can be configured in *Settings > Configure Krita... > General > Window > Multiple Document Mode.*\
There will be no difference visible after script installation, when tabs are on.

## Installation:
- on github, click the green button 'code' and pick 'download zip'. Do not extract it.
- go to *Tools > Scripts > Import Python Plugin* and pick the downloaded .zip file
- restart krita.
- activate the addon: *Settings > Configure Krita... > Python Plugin Manager > Subwindow Organizer (ON).*
- restart krita again.
- new actions are on the bottom of "View" menu. Keyboard shortcuts can be changed in settings.

## Features:
- **responsive subwindows:** never get larger than workspace. Adjusts to krita window resize, dockers resize, togglign fullscreen and canvas-only modes.
- **open as floating windows:** all newly created subwindows open as 'always on top' and hover over the canvas.
- **"split screen" mode**: move a floater to the right or left side of the screen to pin it as a background, reference window. Move window down to leave this mode
- **drag and drop**: allows to swap windows moving background ones on other ones, entering and leaving the split screen mode, moving floaters to the bottom to minimize them and leaving minimization dragging them up.
- **snap floaters to borders:** floaters can't go out of the workspace borders, which would cause it to create sliders.

## User actions:
- **Toggle split screen:**

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
- **minimize** (override): only floating windows can get minimized. Minimization can be done with drag and drop.
