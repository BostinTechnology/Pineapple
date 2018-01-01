#! /bin/sh

# Shelll script to run pineapple Pi Application on bootup

cd /home/pi/Projects/pineapple/PiApplication

sudo ./Control.py --start &

exit 0

