#!/usr/bin/env python3

# Load just enough to take screenshot as quick as possible
import subprocess
import json

json = json.loads(subprocess.run(['hyprctl', 'monitors', 'all', '-j'], capture_output=True, text=True, check=True).stdout)
MONITOR = next((item['name'] for item in json if item.get('focused')), None) # get name of focused monitor
# Take screenshot with grim, set format to ppm (more memory, but faster) and read directly from stdout to memory to save writing temp file to disk
IMAGE = subprocess.run(['grim', '-o', MONITOR, '-t', 'ppm', '-'], capture_output=True, check=True).stdout
SCALE = float(next((item['scale'] for item in json if item.get('focused')), None)) # get scale of focused monitor

# Load up GUI
import sys
import os
import signal
import datetime
from PySide6.QtGui import QImage
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickImageProvider
from PySide6.QtCore import QObject, Slot, QByteArray, QBuffer, QTimer
from PySide6.QtWidgets import QApplication, QFileDialog

IMAGE = QImage.fromData(IMAGE)

class ImageProvider(QQuickImageProvider):
	def __init__(self):
		super().__init__(QQuickImageProvider.Image)
	def requestImage(self, id, size, requestedSize):
		return IMAGE

def crop(x, y, w, h):
	# undo the monitor scaling, couldn't find a way to get the unscaled cords from QML :(
	return IMAGE.copy(x*SCALE, y*SCALE, w*SCALE, h*SCALE)

def imageBytes(qImage):
	byte_array = QByteArray()
	buffer = QBuffer(byte_array)
	buffer.open(QBuffer.ReadWrite)
	qImage.save(buffer, 'PPM')
	buffer.close()
	return byte_array

class Tools(QObject):
	@Slot(float, float, float, float)
	def ocr(self, x, y, w, h):
		stdout, stderr = subprocess.Popen(
			['tesseract', '-', '-'],
			stdin  = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			text = False
		).communicate(input = imageBytes(crop(x, y, w, h)))
		TEXT = stdout.decode('utf-8')
		clipboard.setText(TEXT)
		print(f"OCR'd Text:\n{TEXT}")
	@Slot(float, float, float, float)
	def qr(self, x, y, w, h):
		stdout, stderr = subprocess.Popen(
			['zbarimg', '-'],
			stdin  = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			text = False
		).communicate(input = imageBytes(crop(x, y, w, h)))
		TEXT = stdout.decode('utf-8').replace('QR-Code:', '')
		clipboard.setText(TEXT)
		print(f"Decoded data:\n{TEXT}")
	@Slot(float, float, float, float)
	def copy(self, x, y, w, h):
		clipboard.setImage(crop(x, y, w, h))
		print('Copied to clipboard')
	@Slot(float, float, float, float)
	def save(self, x, y, w, h):
		name = os.path.expanduser('~/screenshot.{date:%Y-%m-%d_%H:%M:%S}.png'.format(date = datetime.datetime.now()))
		filename, filetype = QFileDialog.getSaveFileName(None, 'Save Image', name, 'PNG (Portal Network Graphics) (*.png);;WebP (*.webp);;PPM (Portable Pixmap Format) (*.ppm);;JPEG (*.jpg);;BMP (Bitmap) (*.bmp)')
		if filename:
			crop(x, y, w, h).save(filename)
			print(f"Saved image to {filename}")
			print(f"{_}")
	@Slot(str, float, float, float, float)
	def upload(self, host, x, y, w, h):
		# TODO Implement
		print(f"Upload image to {host}")

# Handle closing via interupt signal
def sigint_handler(*args):
	app.quit()
signal.signal(signal.SIGINT, sigint_handler)

# Setup Qt app
app = QApplication(sys.argv)
clipboard = QApplication.clipboard()

engine = QQmlApplicationEngine()
engine.quit.connect(app.quit)

IMG = ImageProvider()
engine.addImageProvider('img', IMG)

tools = Tools()
engine.rootContext().setContextProperty('tools', tools)

DIR = os.path.dirname(os.path.realpath(__file__)) # get directory script is in even if called via symlink
engine.load(os.path.join(DIR, 'ui.qml')) # load ui qml

# Create timer to break from Qt's event loop and let python process signals so we can close via Ctrl+C in terminal
timer = QTimer()
timer.timeout.connect(lambda: None)
timer.start(100)

sys.exit(app.exec())
