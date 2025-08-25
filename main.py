#!/usr/bin/env python3

# Load just enough to take screenshot as quick as possible
import subprocess
import json

WMs = {
	'hyprland': ['hyprctl', 'monitors', 'all', '-j'],
	'sway': ['swaymsg', '-t', 'get_outputs']
}
for WM, command in WMs.items():
	try:
		JSON = json.loads(subprocess.run(command, capture_output=True, text=True, check=True).stdout)
		break
	except subprocess.CalledProcessError as e: pass

MONITOR = next((item['name'] for item in JSON if item.get('focused')), None) # get name of focused monitor
# Take screenshot with grim, set format to ppm (more memory, but faster) and read directly from stdout to memory to save writing temp file to disk
IMAGE = subprocess.run(['grim', '-o', MONITOR, '-t', 'ppm', '-'], capture_output=True, check=True).stdout
SCALE = float(next((item['scale'] for item in JSON if item.get('focused')), None)) # get scale of focused monitor

# Get window list for window picking
def searchObj(obj, searchKey, searchValue=None):
	matches = []
	if isinstance(obj, dict):
		for key, value in obj.items():
			if key == searchKey:
				if searchValue is None or value == searchValue: matches.append(obj)
			else: matches.extend(searchObj(value, searchKey, searchValue))
	elif isinstance(obj, list):
		for item in obj: matches.extend(searchObj(item, searchKey, searchValue))
	return matches

match WM:
	case 'hyprland':
		WORKSPACEID = json.loads(subprocess.run(['hyprctl', 'activeworkspace', '-j'], capture_output=True, text=True, check=True).stdout)['id']
		WINDOWS = json.loads(subprocess.run(['hyprctl', 'clients', '-j'], capture_output=True, text=True, check=True).stdout)
	case 'sway':
		j = json.loads(subprocess.run(['swaymsg', '-t', 'get_tree'], capture_output=True, text=True, check=True).stdout)
		WINDOWS = searchObj(searchObj(j, 'output', MONITOR)[0], 'pid')

# Load up GUI
import sys
import os
import signal
import datetime
from PySide6.QtGui import QImage, QSurfaceFormat
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickImageProvider
from PySide6.QtCore import Qt, QObject, Slot, Signal, QByteArray, QBuffer, QTimer
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
	result_signal = Signal(str)
	selection_signal = Signal(float, float, float, float)
	_result = ''
	@Slot()
	def copyResult(self):
		clipboard.setText(self._result)
		print('Copied to clipboard')
	@Slot(float, float, float, float)
	def ocr(self, x, y, w, h):
		stdout, stderr = subprocess.Popen(
			['tesseract', '-', '-'],
			stdin  = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			text = False
		).communicate(input = imageBytes(crop(x, y, w, h)))
		self._result = stdout.decode('utf-8')
		print(f"OCR'd Text:\n{self._result}")
		self.result_signal.emit(self._result)
	@Slot(float, float, float, float)
	def qr(self, x, y, w, h):
		stdout, stderr = subprocess.Popen(
			['zbarimg', '-'],
			stdin  = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			text = False
		).communicate(input = imageBytes(crop(x, y, w, h)))
		self._result = stdout.decode('utf-8').replace('QR-Code:', '')
		print(f"Decoded data:\n{self._result}")
		self.result_signal.emit(self._result)
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
	@Slot(str, float, float, float, float)
	def upload(self, host, x, y, w, h):
		# TODO Implement
		print(f"Upload image to {host}")
	@Slot(float, float)
	def pickWindow(self, mouseX, mouseY):
		mouseX = mouseX * SCALE
		mouseY = mouseY * SCALE
		# Hyprland and Sway both order windows in reverse stacking order, i.e. the top most window is at the end, so we reverse the order and break on first match to save wasting time searching windows underneath
		match WM:
			case 'hyprland':
				for win in reversed(WINDOWS):
					x, y, w, h = [item * SCALE for item in [*win['at'], *win['size']]]
					if x <= mouseX < x + w and y <= mouseY < y + h and win['workspace']['id'] == WORKSPACEID and not win['hidden']:
						self.selection_signal.emit(*win['at'], *win['size'])
						break
			case 'sway':
				for win in reversed(WINDOWS):
					x, y, w, h = [item * SCALE for item in [win['rect']['x'], win['rect']['y'], win['rect']['width'], win['rect']['height']]]
					if x <= mouseX < x + w and y <= mouseY < y + h and win['visible']:
						self.selection_signal.emit(win['rect']['x'], win['rect']['y'], win['rect']['width'], win['rect']['height'])
						break

# Handle closing via interupt signal
def sigint_handler(*args):
	app.quit()
signal.signal(signal.SIGINT, sigint_handler)

# Setup Qt app
app = QApplication(sys.argv)
clipboard = QApplication.clipboard()

format = QSurfaceFormat()
format.setAlphaBufferSize(8)
QSurfaceFormat.setDefaultFormat(format)

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
