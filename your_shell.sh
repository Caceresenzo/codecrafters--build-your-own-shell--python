#!/bin/sh
#
# DON'T EDIT THIS!
#
# CodeCrafters uses this file to test your code. Don't make any changes here!
#
# DON'T EDIT THIS!
set -ex

SCRIPT_DIR="$(dirname "$0")"
export PYTHONPATH="$SCRIPT_DIR"

exec pipenv \
    --quiet \
    run \
    python3 -m app.main "$@"
