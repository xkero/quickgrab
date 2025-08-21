Quickshot
=========

A simple screenshot utility with OCR (**O**ptical **C**haracter **R**ecognition via [Tesseract](https://github.com/tesseract-ocr/tesseract)) and QR code decoding (via [ZBar](https://github.com/mchehab/zbar))

![](https://github.com/user-attachments/assets/45c67274-b972-4287-a51d-4b08ef70da31 "Screenshot")

## Install

As the program is just a python file (`main.py`) and a qml file (`ui.qml`), no compilation is needed. Just run `install.sh` as root to copy the files or do it manually.

## Dependencies

To run you'll need to install:
* Python v3: You most likely already have this installed :).
* [PySide6](https://pypi.org/project/PySide6/) & QtQuick: For GUI.

Quickshot calls all of the following via command line so you don't need any language binding packages:
* [Grim](https://gitlab.freedesktop.org/emersion/grim): Used to take the actual screenshot.
* [hyprctl](https://github.com/hyprwm/Hyprland): Needed for Hyprland support, specifically to get the active monitor.
* [Tesseract](https://github.com/tesseract-ocr/tesseract): Needed for the OCR function.
* [ZBar](https://github.com/mchehab/zbar): Needed for QR code decoding.

## Usage

Once installed you can then run quickshot via the `quickshot` command in a terminal or bind it to a key in your window manager/compositor.
Once run you can drag anywhere on the screen to create a selection, underneath you'll see a row of buttons for functions to perform on it.

## Todo

Help welcome! Especially if you have experience with QtQuick.

Features that still need implementing:
  * Only currently supports Hyprland, but I want to add support for other Wayland compositors or systems.
  * Clicking a window to have the selection fit it automatically.
  * Resize and movement handles to alter an existing selection.
  * Ability to upload selections to online services.

## License

All code unless specified is GNU GPL version 3 or later
