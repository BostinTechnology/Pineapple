#! /bin/sh

# Shelll script to run pineapple data display application on bootup

# Start the database
cd /home/pi/Projects/pineapple/bin

sleep 5

./run_datadisplay.sh &
