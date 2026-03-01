#!/bin/sh
#
# DON'T EDIT THIS!
#
# CodeCrafters uses this file to test your code. Don't make any changes here!
#
# DON'T EDIT THIS!
pipenv run python3 -c '' >/dev/null 2>&1
SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR"
pwd
find
exec pipenv run python3 -m app.main "$@"
