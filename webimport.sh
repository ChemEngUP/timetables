#!/usr/bin/bash

./pull.py | sed -f shorten.sed | ./extractcolumns.py --headerfile headers.txt --sort -o fulltable_web.csv