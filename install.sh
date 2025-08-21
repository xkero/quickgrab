#!/usr/bin/env bash

set -e

if [ "$EUID" -ne 0 ]
	then echo "Please run as root!"
	exit
fi

INSTALLDIR="/usr/share/quickshot"
mkdir "$INSTALLDIR"
install -m 755 main.py ui.qml "${INSTALLDIR}/"
ln -s "${INSTALLDIR}/main.py" /usr/bin/quickshot
echo "Installed quickshot!"
