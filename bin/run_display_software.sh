#! /bin/sh

# Shelll script to run pineapple display applicaiton on bootup

# Start the database
cd /home/pi/Projects/pineapple/setup_dynDB

./run_DynDB_diskdb.sh &

sleep 5

# Start the RestFul APi
cd /home/pi/Projects/pineapple/

node . &

# Start the pineapple application
cd /home/pi/Projects/pineapple/setup_dynDB

sudo ./Control.py --transmit &


exit 0

