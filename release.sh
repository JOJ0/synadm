#!/bin/bash
python3 -m pip install --upgrade build
python3 -m pip install --user --upgrade twine
python3 -m build
python3 -m twine upload --repository testpypi dist/*
echo "All good? Upload to real pypi:"
echo python3 -m twine upload testpypi dist/*

