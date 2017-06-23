"""
Contains the required AWS Connection Utilities

#TODO: If there is no db connection, will capture the data in local file ready for transmit
    This will require some space management so that we don't overfill the card.
    If it was really clever, it would create a separate thread to handle writing of the data

BUG - Logging is not working

This needs to be converted to a class and handle many additional functions like
- no network connection
- connecting to the restful interface
"""
###
### All this needs to be changed to suit the requirements of a class
###

import boto3
import sys
import logging

import Standard_Settings


class DataAccessor:
    """
    Takes the given data and writes it to the required output.
    The output location will be dependent on the chosen settings - not sure where these are stored.
    """
    def __init__(self):
        
        return
        

    def DynamodbConnection(self):
        """
        Connect to the dynamo db.
        set Endpoint is used to make a local connection rather than the remote connection
        returns T
        """
        log = logging.getLogger(__name__)
        #TODO: Add in validation that a conection has been made.
        log.info("Setting Up db connection")
        try:
            db = boto3.client('dynamodb', 
                aws_access_key_id='AKIAI7HW3Y2EPZ5GPBTQ',
                aws_secret_access_key='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',
                region_name = 'eu-west-1')
    #            endpoint_url='http://dynamodb.eu-west-1.amazonaws.com',

        except:
            print ("Unable to connected to database, please check internet connection")
            sys.exit()


        return db

        
    def WriteValues(self, db, data, tstamp, device, sensor, acroynm, desc):
        """
        Update the SensorValues table with the given data and timestamp
        Always using the same sensor
        returns nothing
        """
        
        #TODO: Needs to return a success / failure

        #TODO: Future upgrade is to capture the data if offline and send it when it reconnects.
        
        print ("device: %s, Timestamp: %s, Sensor: %s, Acroynm: %s, Desc: %s, Tag: %s" % (device, tstamp, sensor, acroynm, desc, data))
        
        return
        try:
            ans = db.put_item(
                TableName='SensorValues',
                Item={
                    'Device_ID': {'N': str(device)},
                    'TimeStamp': {'S': str(tstamp)},
                    'Sensor_ID': {'N': str(sensor)},
                    'SensorAcroynm': {'S' : str(acroynm)},
                    'SensorDescription' : { 'S': str(desc)},
                    'MVData': { 'M' : {
                        'type': { 'S' : '1'},
                        'value': { 'S' : str(data)}
                        }},
                    'Viewed': { 'BOOL' : False},
                    },
                )
            # print("Create Item Response %s" % ans) #Debug
        except:
            print ("Unable to write data to AWS")


        return
