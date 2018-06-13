#!/bin/bash
###Make MacOS executables

cd "$(dirname "$0")"
pyinstaller main.py --add-data "data:data" -w -F -y --clean
