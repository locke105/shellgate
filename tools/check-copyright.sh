#!/bin/bash

find ./* -name "*.py" | xargs python tools/file-header-check.py -v --add
