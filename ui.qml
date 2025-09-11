import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15

ApplicationWindow {
	title: 'Quickgrab'
	visible: true
	visibility: 'FullScreen'
	width: screenshot.width
	height: screenshot.height
	Connections {
		target: tools
		function onResult_signal(result) {
			resultsText.text = result
			results.open()
		}
		function onSelection_signal(x, y, w, h) {
			selection.x = x
			selection.y = y
			selection.width = w
			selection.height = h
		}
		function onMissing_signal(command) {
			switch(command) {
				case 'tesseract':
					ocrButton.enabled = false
					ocrButton.ToolTip.text = "Tesseract doesn't appear to be installed so OCR function is unavailable."
					break;
				case 'zbarimg':
					decodeButton.enabled = false
					decodeButton.ToolTip.text = "ZBar doesn't appear to be installed so QR/Barcode decoding is unavailable."
					break;
			}
		}
	}
	Popup {
		id: results
		visible: false
		x: (parent.width - width) / 2
		y: (parent.height - height) / 2
		modal: true
		popupType: Popup.Item
		closePolicy: Popup.CloseOnPressOutside | Popup.CloseOnEscape
		Shortcut {
			sequences: ['Escape', 'Q']
			onActivated: { results.visible? results.close() : close() }
		}
		background: Rectangle {
			color: 'black'
			radius: 10
			border.width: 1
			border.color: 'gray'
		}
		contentItem: Column {
			spacing: 10
			Text {
				text: 'Results:'
				font.bold: true
				font.pointSize: resultsText.font.pointSize * 1.5
				width: parent.width
				horizontalAlignment: Text.AlignHCenter
				color: 'white'
			}
			Text {
				id: resultsText
				color: 'white'
			}
			Row {
				spacing: 10
				
				Button {
					text: 'Copy to clipboard'
					onClicked: {
						tools.copyResult()
						results.close()
					}
				}
				Button {
					text: 'Close'
					onClicked: results.close()
				}
			}
		}
	}
	Item {
		id: shortcuts
		Shortcut {
			sequence: 'T'
			onActivated: tools.ocr(selection.x, selection.y, selection.width, selection.height)
		}
		Shortcut {
			sequence: 'R'
			onActivated: tools.qr(selection.x, selection.y, selection.width, selection.height)
		}
		Shortcut {
			sequence: 'C'
			onActivated: tools.copy(selection.x, selection.y, selection.width, selection.height)
		}
		Shortcut {
			sequence: 'S'
			onActivated: tools.save(selection.x, selection.y, selection.width, selection.height)
		}
	}
	Image {
		id: screenshot
		source: "image://img"
		anchors.fill: parent
		fillMode: Image.PreserveAspectCrop
	}
	component Dim: Rectangle {
		x: 0
		y: 0
		color: 'black'
		opacity: 0.5
		visible: selection.visible
	}
	Dim {
		id: dimLeft
		width: selection.x
		height: screenshot.height
	}
	Dim {
		id: dimRight
		x: selection.x + selection.width
		width: screenshot.width
		height: screenshot.height
	}
	Dim {
		id: dimTop
		x: selection.x
		width: selection.width
		height: selection.y
	}
	Dim {
		id: dimBottom
		x: selection.x
		y: selection.y + selection.height
		width:  selection.width
		height: screenshot.height
	}
	Rectangle {
		id: selection
		x: 0
		y: 0
		width: 0
		height: 0
		color: 'transparent'
		visible: false
		border.color: 'white'
		border.width: 1
	}
	MouseArea {
		anchors.fill: parent
		width: screenshot.width
		height: screenshot.height
		cursorShape: Qt.CrossCursor
		focus: true
		property var dragging: false
		propagateComposedEvents: true
		property var lastPressPoint: Qt.point(0,0)
		onPressed: (mouse) => {
			lastPressPoint.x = mouse.x
			lastPressPoint.y = mouse.y
			selection.visible = true
		}
		onPositionChanged: (mouse) => {
			selection.x = Math.min(lastPressPoint.x , mouse.x)
			selection.y = Math.min(lastPressPoint.y , mouse.y)
			selection.width = Math.abs(lastPressPoint.x - mouse.x)
			selection.height =  Math.abs(lastPressPoint.y - mouse.y)
		}
		onReleased: (mouse) => {
			if(lastPressPoint.x === mouse.x && lastPressPoint.y === mouse.y) tools.pickWindow(mouse.x, mouse.y)
		}
	}
	Rectangle {
		id: toolbar
		height: 50
		x: {
			let pos = selection.x
			if(toolbar.sideways) {
				pos += selection.width + 10
				if(pos < screenshot.width - childrenRect.width) return pos // check right
				else {
					pos = selection.x - 10 - childrenRect.width
					if(pos > 0) return pos // check left
				}
				//toolbar.y = selection.y + (selection.height - childrenRect.height) / 2
				return selection.x + (selection.width - childrenRect.width) / 2
			}
			else if(pos + childrenRect.width > screenshot.width) return screenshot.width - childrenRect.width
			else return pos
		}
		y: {
			let pos = selection.height + selection.y + 10
			toolbar.sideways = false
			if(pos + toolbar.height > screenshot.height) { // check bottom
				pos = selection.y - toolbar.height - 10
				if(pos >= 0) return pos // check top
				else {
					//if() return selection.y + (selection.height - childrenRect.height) / 2
					toolbar.sideways = true
					return selection.y
				}
			}
			else return pos
		}
		color: 'transparent'
		visible: selection.visible
		property var sideways: false
		GridLayout {
			id: toolbarGrid
			flow: toolbar.sideways? GridLayout.TopToBottom : GridLayout.LeftToRight
			uniformCellHeights: toolbar.sideways? false : true
			uniformCellWidths: toolbar.sideways? true : false
			rowSpacing: 10
			columnSpacing: 10
			component ToolButton: Button {
				icon.width: 32
				icon.height: 32
				ToolTip.visible: hovered
				ToolTip.delay: 1000
				Layout.fillWidth: true
			}
			ToolButton {
				id: ocrButton
				text: 'OCR'
				icon.name: 'edit-select-text'
				onClicked: tools.ocr(selection.x, selection.y, selection.width, selection.height)
				ToolTip.text: 'Read text in selection via Optical Character Recognition\nShortcut: T'
			}
			ToolButton {
				id: decodeButton
				text: 'Decode'
				icon.name: 'view-barcode-qr'
				onClicked: tools.qr(selection.x, selection.y, selection.width, selection.height)
				ToolTip.text: 'Decode QR code or other 2D barcode\nShortcut: R'
			}
			ToolButton {
				id: copyButton
				text: 'Copy'
				icon.name: 'edit-copy'
				onClicked: tools.copy(selection.x, selection.y, selection.width, selection.height)
				ToolTip.text: 'Copy selection to clipboard\nShortcut: C'
			}
			ToolButton {
				id: saveAsButton
				text: 'Save As...'
				icon.name: 'document-save'
				onClicked: tools.save(selection.x, selection.y, selection.width, selection.height)
				ToolTip.text: 'Save selection to image file\nShortcut: S'
			}
			ToolButton {
				id: uploadButton
				text: 'Upload...'
				icon.name: 'upload-media'
				checked: uploadMenu.visible
				onClicked: uploadMenu.popup()
				ToolTip.text: 'Upload selection to online host'
				Menu {
					id: uploadMenu
					y: uploadButton.y + uploadButton.height
					x: uploadButton.x
					MenuItem {
						text: 'Imgur'
						onTriggered: tools.upload('imgur', selection.x, selection.y, selection.width, selection.height)
					}
					MenuItem {
						text: 'Google Image Search'
						onTriggered: tools.upload('google image search', selection.x, selection.y, selection.width, selection.height)
					}
				}
			}
			ToolButton {
				id: closeButton
				text: 'Close'
				icon.name: 'application-exit'
				onClicked: close()
				ToolTip.text: 'Quit and go back to desktop\nShortcut: Q or Escape'
			}
		}
	}
}
