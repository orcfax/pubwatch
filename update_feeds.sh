#! /usr/bin/bash

echo "updating feeds list"
wget https://raw.githubusercontent.com/orcfax/cer-feeds/main/feeds/cer-feeds.json -O cer-feeds.json
echo "done"
