#! /usr/bin/bash

source validator.env

venv/bin/python pubwatch.py --feeds cer-feeds.json --local
