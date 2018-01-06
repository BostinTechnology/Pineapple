#! /bin/sh

# Shelll script to run pineapple data display application on bootup

# Start the database
cd /home/pi/Projects/pineapple/DisplayTool

sleep 5

./DataDisplay.py &
