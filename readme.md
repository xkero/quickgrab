Quickgrab
=========

A simple GUI screenshot utility with direct access to [OCR](https://en.wikipedia.org/wiki/Optical_character_recognition) and QR code/barcode decoding.

![](https://github.com/user-attachments/assets/45c67274-b972-4287-a51d-4b08ef70da31 "Screenshot")

## Install

### Archlinux

Available on the AUR as `quickgrab-git` install via your prefered AUR helper, e.g. `pikaur -S quickgrab-git`

### Everyone else

As the program is just a python file (`main.py`) and a qml file (`ui.qml`), no compilation is needed. Just run `install.sh` as root to copy the files or do it manually.

Optional: If using Hyprland you may want to add these window rules:

    # Stop Quickgrab window being tiled and animated
    windowrulev2 = float, class:^python3$, title:^Quickgrab$
    windowrulev2 = noanim, class:^python3$, title:^Quickgrab$
    windowrulev2 = float, title:^(Save Image)$

## Dependencies

To run you'll need to install:
* Python v3: You most likely already have this installed :).
* [PySide6](https://pypi.org/project/PySide6/) & QtQuick: For GUI.

Quickgrab calls all of the following via command line so you don't need any language binding packages:
* [Grim](https://gitlab.freedesktop.org/emersion/grim): Used to take the actual screenshot.
* [Tesseract](https://github.com/tesseract-ocr/tesseract): Needed for the OCR function.
* [ZBar](https://github.com/mchehab/zbar): Needed for QR code decoding.

## Usage

Once installed you can then run quickgrab via the `quickgrab` command in a terminal or bind it to a key in your window manager/compositor.
Once run you can drag anywhere on the screen or click on a window to create a selection, underneath you'll see a row of buttons for functions to perform on it.

## Todo

Help welcome! Especially if you have experience with QtQuick.

Features that still need implementing:
  * Only currently supports Hyprland & Sway, but I want to add support for other Wayland compositors or systems.
  * Ability to upload selections to online services.
  * Ability to customise toolbar by adding custom tools, reordering, or removing others.

## Development

To assist with development I've written a script called `runonedit.sh` which as it's name implies runs a command and when certain files are edited kills that command and reruns it; this allows a very fast develop & test loop. I pair this by running a nested `sway` instance inside my host desktop (Hyprland) which keeps Quickgrab's fullscreen window from being disruptive when it restarts. After starting sway I then run the below command to restart Quickgrab whenever I save changes in my text editor: 

    SWAYSOCK=/run/user/"$UID"/sway-ipc."$UID".*.sock WAYLAND_DISPLAY='wayland-2' ./runonedit.sh main.py ui.qml -- ./main.py

Setting `SWAYSOCK` is needed so Quickgrab can communicate with sway (to get active monitor, scaling, window positions, etc). `WAYLAND_DISPLAY` is so it opens inside the nested desktop, you may need to change this depending on your setup.

## License

All code unless specified is GNU GPL version 3 or later
