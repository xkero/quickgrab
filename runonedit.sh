#!/bin/bash

WATCHLIST=()

for arg in "$@"; do
	if [[ "$arg" != "--" ]]; then
		if [[ ! -f "$arg" ]]; then
			echo "File '$arg' doesn't exist."
			exit 1
		fi
		WATCHLIST+=("$arg")
		shift
	else break
	fi
done

shift
EXEC="$@"

if [[ -z "$WATCHLIST" || -z "$EXEC" ]]; then
	echo "Usage: $0 <files to watch> -- <command to run and kill/rerun on edits>"
	exit 1
fi

start() {
	echo "Running: $EXEC"
	$EXEC &
	PID=$!
	echo "Process ID: $PID"
}

stop() {
	if [ -n "$PID" ]; then
		echo "Stopping process $PID..."
		kill "$PID"
		wait "$PID" 2>/dev/null
	fi
}

# Initial start
start

# Watch for changes and restart
echo "Watching ${WATCHLIST[*]}"
while inotifywait -e close_write ${WATCHLIST[*]}; do
	echo "Files modified."
	stop
	start
done
