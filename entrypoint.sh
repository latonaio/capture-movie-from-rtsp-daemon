#!/bin/sh

python3 -u main.py
curl -s -X POST localhost:10001/quitquitquit
