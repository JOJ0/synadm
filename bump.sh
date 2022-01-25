#!/bin/bash

#set -x
DRY="echo"
PART=$1

if [ -z $1 ]; then
    echo "Bumps version, commits and tags."
    echo "Usage: ./bump.s <major|minor|patch> [doit]"
    exit 0
fi

if [[ "$2" == "doit" ]]; then
    DRY=""
else
    echo -e "\nTHIS IS A DRY-RUN\n"
fi

if [[ "$2" == "doit" ]]; then
    bumpversion $PART --verbose
    echo "All good? Then push with:"
    echo "git push --follow-tags"
else
    bumpversion $PART --verbose --dry-run
fi
