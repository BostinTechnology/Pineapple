# Pineapple

Installing the server
=====================

After cloning the repository, cd into the Pinapple directory and issue the following commands:-

  npm install


This will initialise and install the required npm modules.

The DynamoDB local installation also has to be completed.

cd dynamoDB
./Release

This will download and build the required DynamoDB modules.  An instance of dynamoDB can then be 
found at 
http://localhost:8000/

The dynamoDB shell can be access via 
http://localhost:8000/shell/



To Run
======

node .		(don't miss the dot!)

Restful interface can then be found at localhost:8080
