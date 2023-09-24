#!/usr/bin/env bash

# Run tests
action=$1

if [[ $action != "build" && $action != "install" ]]; then
	echo 'Missing required argument: "build" or "install"'
	exit 1
fi

DIR="$(dirname "$0")"
cd $DIR
for file in $DIR/comments_*.8xpsrc; do
	tibasic_compile.py $action "$file" /tmp/script_testing_tempfile.8xp IGNORE
done
