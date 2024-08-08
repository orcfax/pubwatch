#! /usr/bin/bash

cd /home/orcfax/pubwatch/
source validator.env

venv/bin/python pubwatch.py --feeds cer-feeds.json --local
