#!/usr/bin/env/python3
"""
Contains the functions to create all the tables required for the RFID Tag Reader

Uses Software Overview V4.1


"""

#TODO: currently printing the table output badly and prints definition: None after a true statement
""" EXTRACT
tus': 'ACTIVE', 'KeySchema': [{'KeyType': 'HASH', 'AttributeName': 'Device_ID'}, {'KeyType': 'RANGE', 'AttributeName': 'TimeStamp'}], 'ItemCount': 0, 'CreationDateTime': datetime.datetime(2015, 8, 31, 14, 4, 35, 719000, tzinfo=tzlocal())}, 'ResponseMetadata': {'HTTPStatusCode': 200, 'RequestId': '3f6d518f-5263-492b-96c8-95110a196b0f'}}
true
definition: None
definition: {'TableDescription': {'TableArn': 'arn:aws:dynamodb:ddblocal:000000000000:table/SensorDescriptions', 'AttributeDefinitions': [{'AttributeName': 'Device_ID', 'AttributeT
"""

import sys
import re
from datetime import datetime
from datetime import timedelta


import boto3
import json
from boto3.exceptions import DynamoDBOperationNotSupportedError, DynamoDBNeedsConditionError, DynamoDBNeedsKeyConditionError
from botocore.exceptions import ClientError


################################## CONSTANTS ###################################

# The maximum time to ait for the table status to change (measured in seconds)
MAX_TABLE_STATUS_CHANGE_TIME = 60

################################## FUNCTIONS ###################################

def DynamodbConnection():
    """
    Connect to the dynamo db.
    setEndpoint is used to make a local connection rather than the remote connection
    """
    #TODO: Add in validation that a conection has been made.
    db = boto3.client('dynamodb', 
        endpoint_url='http://192.168.1.119:8000',
        aws_access_key_id='anything',
        aws_secret_access_key='anything',
        region_name='eu-west-1')
    #print (db)
    return db

def PrettyPrint(obj):
    """
    Prints the supplied dictionary in a human readable form
    """
    print (json.dumps(obj, sort_keys=True, indent=4))
    return
    
def ReturnElement(lookin,lookfor):
    """
    given the dictionary and the string, look for and return the value
    return FALSE if not found
    """
    try:
        response = lookin[lookfor]
        return response
    except:
        return False

def DescribeTable(db,tbl):
    """
    Takes the given table and connection to return a decoded dictionary of all the values
    the returned dictionary is a single item called 'table' that has a dictionary of the table inside it
    """
    
    fulldesc = db.describe_table(tbl)
    #print fulldesc #Debug

    # fulldesc contains a dictionary with only 1 element called table. to return the description, 
    #  extract table description from the table dictionary
    tabledesc = fulldesc['Table']
    return tabledesc

def CheckTableStatus(db,tbl,reqd):
    """
    Checks the table regularly unitl the status returned matches what is required.
    Takes the dyname db connection (db), the table to check and the status required
        CREATING | DELETING | ACTIVE | UPDATING
    Note: Has a timeout if this is exceeded - MAX_TABLE_STATUS_CHANGE_TIME
    Returns True if matched or False if not
    """
    
    #TODO: There is a better way of doing this using waiters

    #Checks for the incoming status to be either CREATING | DELETING | ACTIVE | UPDATING
    if (re.search(reqd,"CREATING | DELETING | ACTIVE | UPDATING")):
        print ("Incorrect parameter passed to CheckTableStatus: %s" % reqd)
        sys.exit()

    # Start the timer
    starttime = datetime.now()
    tablestatus = ""
    # loop waiting for either the expected status or timer is exceeded
    while ((tablestatus != req) or 
           ((datetime.now() - starttime) > timedelta(seconds = MAX_TABLE_STATUS_CHANGE_TIME))):
        print ("Checking Status")
        tabledesc = DescribeTable(conn,"users")
        tablestatus = ReturnElement(tabledesc,"TableStatus")

    # If the tablestatus is as required, then return a positive
    if tablestatus == status:
        return True
    
    return False


def CreatingTable(db,tbl,attrib_def,key_sch,prov_thrput,wait):
    """
    Takes the given parameters and performs tha table write and error checking
    Requires the dyname connection (db) and the table attributes already formatted
    returns the table connection
    If wait is True, the function will wait for the action to be complete and the table ACTIVE
    """
    try:
        table = db.create_table(TableName=tbl, 
                AttributeDefinitions=attrib_def, 
                KeySchema=key_sch, 
                ProvisionedThroughput=prov_thrput)
        print ("definition: %s" % table)    #DEBUG
        
        #TODO: I think it is possible for this to wait until it returns ACTTIVE
 
    #TODO: Check which of these are still valid for boto3.
    # botocore.exceptions.ClientError - ResourceInUseException
    except DynamoDBOperationNotSupportedError:
        print ("Operation Not Supported Error, dynamo db error")
        print (DynamoDBOperationNotSupportedError)
        return False
    except DynamoDBNeedsConditionError:
        print ("Need Condition Error, dynamo db error")
        print (DynamoDBNeedsConditionError)
        return False
    except DynamoDBNeedsKeyConditionError:
        print ("Needs Key Condition Error, dynamo error")
        print (DynamoDBNeedsKeyConditionError)
        return False
    except ClientError as e:
        print ("Received Error: %s" % e)
        errorcode = e.response["Error"]["Code"]
        print ("Error Code: %s" % errorcode)
        return False
    
    if (wait == True):
        if (CheckTableStatus(db, 'Clients', 'ACTIVE') == False):
            print ("Table has not ACTIVATEd within timeout, aborting creation")
            sys.exit()
    return True




################################### TABLE CREATION FUNCTIONS ###################
    

def CreateClientsTable(db):
    """ 
    Create the Clients table with the necessary Client_ID
    """
    
    attribute_definitions = [
                {
                'AttributeName':'Client_ID',
                'AttributeType':'N'
                },
                ]
    table_name='Clients'
    key_schema=[
                {
                'AttributeName':'Client_ID',
                'KeyType': 'HASH'
                },
                ]
    provisioned_throughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
                }
    
    print ("Creating %s" % table_name)
    
    clients_table = CreatingTable(db,table_name,attribute_definitions,key_schema,provisioned_throughput,False)
    print ("definition: %s" % PrettyPrint(clients_table)) #Debug print to validate creation

    print ('Created %s Table' % table_name)
    print ('********************')
    
        
    return clients_table

def CreateUsersTable(db):
    """ 
    Create the Users table with the necessary User_ID and Client_ID
    """
    
    attribute_definitions = [
                {
                'AttributeName':'UserName',
                'AttributeType':'S'
                },
                ]
    table_name='Users'
    key_schema=[
                {
                'AttributeName':'UserName',
                'KeyType': 'HASH'
                },
                ]
    provisioned_throughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
                }
    print ("Creating %s" % table_name)
    users_table = CreatingTable(db,table_name,attribute_definitions,key_schema,provisioned_throughput,False)
    print ("definition: %s" % PrettyPrint(users_table)) #Debug print to validate creation

    print ('Created %s Table' % table_name)
    print (' ********************')
        
    return users_table

def CreateClientDevicesTable(db):
    """ 
    Create the Client_Devices link table with the necessary Device_ID and Client_ID
    """
    
    attribute_definitions = [
                {
                'AttributeName':'Device_ID',
                'AttributeType':'N'
                },
                ]
    table_name='Client_Devices'
    key_schema=[
                {
                'AttributeName':'Device_ID',
                'KeyType': 'HASH'
                },
                ]
    provisioned_throughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
                }
    print ("Creating %s" % table_name)
    client_devices_table = CreatingTable(db,table_name,attribute_definitions,key_schema,provisioned_throughput,False)
    print ("definition: %s" % PrettyPrint(client_devices_table)) #Debug print to validate creation

    print ('Created %s Table' % table_name)
    print (' ********************')

    return client_devices_table

def CreateSensorValuesTable(db):
    """ 
    Create the SensorValues table with the necessary Device_ID and Timestamp
    """
    
    attribute_definitions = [
                {
                'AttributeName':'Device_ID',
                'AttributeType':'N'
                },
                {
                'AttributeName':'TimeStamp',
                'AttributeType':'S'
                },
                ]
    table_name='SensorValues'
    key_schema=[
                {
                'AttributeName':'Device_ID',
                'KeyType': 'HASH'
                },
                {
                'AttributeName':'TimeStamp',
                'KeyType': 'RANGE'
                },                ]
    provisioned_throughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
                }
    print ("Creating %s" % table_name)
    sensor_values_table = CreatingTable(db,table_name,attribute_definitions,key_schema,provisioned_throughput,False)
    print ("definition: %s" % PrettyPrint(sensor_values_table)) #Debug print to validate creation

    print ('Created %s Table' % table_name)
    print (' ********************')

    return sensor_values_table

def CreateSensorDescriptionsTable(db):
    """ 
    Create the SensorDescriptions table with the necessary Device_ID and Timestamp
    """
    
    attribute_definitions = [
                {
                'AttributeName':'Device_ID',
                'AttributeType':'N'
                },
                ]
    table_name='SensorDescriptions'
    key_schema=[
                {
                'AttributeName':'Device_ID',
                'KeyType': 'HASH'
                },
                ]
    provisioned_throughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
                }
    print ("Creating %s" % table_name)
    sensor_descriptions_table = CreatingTable(db,table_name,attribute_definitions,key_schema,provisioned_throughput,False)
    print ("definition: %s" % PrettyPrint(sensor_descriptions_table)) #Debug print to validate creation

    print ('Created %s Table' % table_name)
    print (' ********************')

    return sensor_descriptions_table
    
    
def CreateClientCountTable(db):
    """ 
    Create the ClientCount table with the necessary QtyClients
    """
    
    attribute_definitions = [
                {
                'AttributeName':'CC_ID',
                'AttributeType':'N'
                },
                ]
    table_name='ClientCount'
    key_schema=[
                {
                'AttributeName':'CC_ID',
                'KeyType': 'HASH'
                },
                ]
    provisioned_throughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
                }
    print ("Creating %s" % table_name)
    client_count_table = CreatingTable(db,table_name,attribute_definitions,key_schema,provisioned_throughput,False)
    print ("definition: %s" % PrettyPrint(client_count_table)) #Debug print to validate creation

    print ('Created %s Table' % table_name)
    print (' ********************')

    return client_count_table


################################# DATA POPULATION #######################

def WriteSensorValues(db, data, tstamp, device, sensor, acroynm, desc):
    """
    Update the SensorValues table with the given data and timestamp
    Always using the same sensor
    returns nothing
    """
    
    #TODO: Needs to return a success / failure

    #TODO: Future upgrade is to capture the data if offline and send it when it reconnects.
    
    print ("device: %s, Timestamp: %s, Sensor: %s, Acroynm: %s, Desc: %s, Tag: %s" % (device, tstamp, sensor, acroynm, desc, data))
    
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
    except Exception as exception:
        print ("Unable to write data to AWS:%s " % exception)


    return
        
def WriteUsers(db, username, password, clientid, clientname, status, lastlogon, email, contact, creationdate, deviceid, acroynm, description):
        """
        Update the Users table with the given data

        returns nothing
        """
        
        #TODO: Needs to return a success / failure

        #TODO: Future upgrade is to capture the data if offline and send it when it reconnects.
        
        print ("Username: %s, Password: %s, Client_ID: %s, ClientName: %s, Status: %s, LastLogOn: %s, Email: %s, Contact: %s, CreationDate: %s" 
                    % (username, password, clientid, clientname, status, lastlogon, email, contact, creationdate)), 
        

        try:
            ans = db.put_item(
                TableName='Users',
                Item={
                    'UserName': {'S': str(username)},
                    'Password': {'S': str(password)},
                    'Client_ID': {'N': str(clientid)},
                    'ClientName': {'S' : str(clientname)},
                    'Status' : { 'S': str(status)},
                    'LastLogOn' : { 'S' : str(lastlogon)},
                    'Email' : { 'S' : str(email)},
                    'Contact' : { 'S' :str(contact)},
                    'CreationDate' : {'S' : str(creationdate)},
                    'Devices': { 'M' : {
                        'DeviceID': { 'S' : str(deviceid)},
                        'DeviceAcroynm': {'S' : str(acroynm)},
                        'DeviceDescription': { 'S' : str(description)}
                        }},
                    'Viewed': { 'BOOL' : False},
                    },
                )
            # print("Create Item Response %s" % ans) #Debug
        except Exception as exception:
            print ("Unable to write data to AWS: %s" % exception)


        return

def WriteClientCount(db, count):
    """
    Update the ClientCount table with the given data
    returns nothing
    """
    
    #TODO: Needs to return a success / failure

    #TODO: Future upgrade is to capture the data if offline and send it when it reconnects.
    
    print ("Client Count: %s" % count)
    
    try:
        ans = db.put_item(
            TableName='ClientCount',
            Item={
                'CC_ID': {'N': '1'},
                'QtyClients': {'S': str(count)},
                },
            )
        # print("Create Item Response %s" % ans) #Debug
    except Exception as exception:
        print ("Unable to write data to AWS:%s " % exception)


    return
################################## MAIN ########################################

conn = DynamodbConnection()

"""
v 1 table setup
Clients = CreateClientsTable(conn)
Users = CreateUsersTable(conn)
ClientDevices = CreateClientDevicesTable(conn)
SensorValues = CreateSensorValuesTable(conn)
SensorDescriptions = CreateSensorDescriptionsTable(conn)
ClientCount = CreateClientCountTable(conn)
"""

#v2 table setup
Users = CreateUsersTable(conn)
ClientCount = CreateClientCountTable(conn)
SensorValues = CreateSensorValuesTable(conn)

#Populate some sample data
# WriteUsers(db, username, password, clientid, clientname, status, lastlogon, email, contact, 
#                   creationdate, deviceid, acroynm, description):
print("Write Users\n***********")

WriteUsers(conn, "m@mlb.com", "password", 1, "BostinTech", 'ACTIVE', '05-05-2017 15:05:34', 'm@mlb.com', '07676 543322', 
                    '07-07-2017 16:05:34', 1, 'GrnHse1', 'Greenhouse 1')
WriteUsers(conn, "l@mlb.com", "pssaword", 2, "BostinTech", 'ACTIVE', '06-06-2017 16:05:34', 'l@mlb.com', '06677 543322', 
                    '07-07-2017 16:05:34', 2, 'Shed1', 'Mushroom Shed 1')
WriteUsers(conn, "c@mlb.com", "passowrd", 3, "BostinTech", 'ACTIVE', '07-07-2017 17:05:34', 'c@mlb.com', '05566 543322', 
                    '07-07-2017 16:05:34', 3, 'Cons', 'conservatory')
WriteClientCount(conn, 3)
print("Write Sensor Values\n*******************")
# WriteSensorValues(db, data, tstamp, device, sensor, acroynm, desc)
WriteSensorValues(conn, '26.4 Deg C', '07-07-2017 :05:05:34.000', 1, 1, 'Temp1', 'Temperature Sensor 1')
WriteSensorValues(conn, '26.5 Deg C', '07-07-2017 02:05:34', 1, 1, 'Temp1', 'Temperature Sensor 1')
WriteSensorValues(conn, '26.6 Deg C', '07-07-2017 04:05:34', 1, 1, 'Temp1', 'Temperature Sensor 1')
WriteSensorValues(conn, '23.4 Deg C', '07-07-2017 06:05:34', 1, 1, 'Temp1', 'Temperature Sensor 1')
WriteSensorValues(conn, '18.7 Deg C', '07-07-2017 08:05:34', 1, 1, 'Temp1', 'Temperature Sensor 1')
WriteSensorValues(conn, '16.5 Deg C', '07-07-2017 10:05:34', 1, 1, 'Temp1', 'Temperature Sensor 1')
WriteSensorValues(conn, '14.5 Deg C', '07-07-2017 12:05:34', 1, 1, 'Temp1', 'Temperature Sensor 1')



print ("Completed")


