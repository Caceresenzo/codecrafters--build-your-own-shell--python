#!/bin/sh
#
# DON'T EDIT THIS!
#
# CodeCrafters uses this file to test your code. Don't make any changes here!
#
# DON'T EDIT THIS!
pipenv install >/dev/null 2>&1
exec pipenv run --quiet python3 -m app.main "$@"
