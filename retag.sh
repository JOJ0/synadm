#!/bin/bash

if [[ -z $1 ]]; then
    echo "usage: ./retag.sh <tagname>"
    exit 1
fi
PUSH_OPTS="$2"

set -x
VERS=$1

git tag -d $VERS; git push origin --delete $VERS; git tag $VERS; git push --tags --follow-tags
