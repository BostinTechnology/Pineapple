#!/usr/bin/env/python3
"""
Contains the functions to create all the tables required for the RFID Tag Reader


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

# The maximum time it for the table status to change (measured in seconds)
MAX_TABLE_STATUS_CHANGE_TIME = 60

################################## FUNCTIONS ###################################

def DynamodbConnection():
    """
    Connect to the dynamo db.
    setEndpoint is used to make a local connection rather than the remote connection
    """
    #TODO: Add in validation that a conection has been made.
    db = boto3.client('dynamodb', 
        endpoint_url='http://localhost:8000',
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
    while ((tablestatus != reqd) or 
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

def CreatedbVersionTable(db):
    """ 
    Create the db Version table
    """
    
    attribute_definitions = [
                {
                'AttributeName':'db_ver',
                'AttributeType':'N'
                },
                ]
    table_name='db_Version'
    key_schema=[
                {
                'AttributeName':'db_ver',
                'KeyType': 'HASH'
                },
                ]
    provisioned_throughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
                }
    print ("Creating %s" % table_name)
    db_version_table = CreatingTable(db,table_name,attribute_definitions,key_schema,provisioned_throughput,False)
    print ("definition: %s" % PrettyPrint(db_version_table)) #Debug print to validate creation

    print ('Created %s Table' % table_name)
    print (' ********************')

    return db_version_table



################################# DATA POPULATION #######################

def WriteSensorValues(db, data, units, tstamp, device, sensor, acroynm, desc):
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
                'Sensor_ID': {'S': str(sensor)},
                'SensorAcroynm': {'S' : str(acroynm)},
                'SensorDescription' : { 'S': str(desc)},
                'MVData': { 'M' : {
                    'type': { 'S' : '1'},
                    'value': { 'S' : str(data)},
                    'units':{ 'S' : str(units)}
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

def Write3Users(db, username, password, clientid, clientname, status, lastlogon, email, contact, creationdate,
                deviceid, acroynm, description, deviceid2, acroynm2, description2, deviceid3, acroynm3, description3):
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
                        '0' : { 'M' :
                        {
                        'DeviceID': { 'S' : str(deviceid)},
                        'DeviceAcroynm': {'S' : str(acroynm)},
                        'DeviceDescription': { 'S' : str(description)}
                        }},
                        '1' : { 'M' :
                        {
                        'DeviceID': { 'S' : str(deviceid2)},
                        'DeviceAcroynm': {'S' : str(acroynm2)},
                        'DeviceDescription': { 'S' : str(description2)}
                        }},
                        '2' : { 'M' :
                        {
                        'DeviceID': { 'S' : str(deviceid3)},
                        'DeviceAcroynm': {'S' : str(acroynm3)},
                        'DeviceDescription': { 'S' : str(description3)}
                        }}
                        }
                        },
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

def WritedbVersion(db, ver):
    """
    Update the db_Version table with the given data
    returns nothing
    """
    
    #TODO: Needs to return a success / failure

    #TODO: Future upgrade is to capture the data if offline and send it when it reconnects.
    
    print ("db version: %s," % ver)
    
    try:
        ans = db.put_item(
            TableName='db_Version',
            Item={
                'db_ver': {'N': '1'},
                'version': {'S': str(ver)}
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
dbversions = CreatedbVersionTable(conn)

#Populate some sample data
# WriteUsers(db, username, password, clientid, clientname, status, lastlogon, email, contact, 
#                   creationdate, deviceid, acroynm, description):
print("Write Users\n***********")

Write3Users(conn, "m@mlb.com", "password", 1, "BostinTech", 'ACTIVE', '2017-05-05 15:05:34', 'm@mlb.com', '07676 543322', 
                    '07-07-2017 16:05:34', 3355054600, 'RPi_3B', 'RPi on workbench', 165456298, 'RPi_Zero', 'RPi by Cosy Sensor',
                    135080095, 'RPi_Sens', 'Rpi on windowsil')
WriteUsers(conn, "l@mlb.com", "pssaword", 2, "BostinTech", 'ACTIVE', '2017-06-06 16:05:34', 'l@mlb.com', '06677 543322', 
                    '07-07-2017 16:05:34', 2480248024, 'Shed1', 'Mushroom Shed 1')
WriteUsers(conn, "c@mlb.com", "passowrd", 3, "BostinTech", 'ACTIVE', '2017-07-07 17:05:34', 'c@mlb.com', '05566 543322', 
                    '07-07-2017 16:05:34', 3690369036, 'Cons', 'conservatory')
WriteClientCount(conn, 3)
print("Write additional data\n*****************")
WritedbVersion(conn, 1.0)

print("Write Sensor Values\n*******************")
# WriteSensorValues(db, data, units, tstamp, device, sensor, acroynm, desc)
WriteSensorValues(conn, '26.4', 'Deg C', '2017-07-07 :05:05:34.001', 1234567890, 1, 'Temp1', 'Temperature Sensor 1')
WriteSensorValues(conn, '26.5', 'Deg C', '2017-07-07 02:05:34.001', 1234567890, 1, 'Temp1', 'Temperature Sensor 1')
WriteSensorValues(conn, '26.6', 'Deg C', '2017-07-07 04:05:34001', 1234567890, 1, 'Temp1', 'Temperature Sensor 1')
WriteSensorValues(conn, '23.4', 'Deg C', '2017-07-07 06:05:34001', 1234567890, 1, 'Temp1', 'Temperature Sensor 1')
WriteSensorValues(conn, '18.7', 'Deg C', '2017-07-07 08:05:34001', 1234567890, 1, 'Temp1', 'Temperature Sensor 1')
WriteSensorValues(conn, '16.5', 'Deg C', '2017-07-07 10:05:34001', 1234567890, 1, 'Temp1', 'Temperature Sensor 1')
WriteSensorValues(conn, '14.5', 'Deg C', '2017-07-07 12:05:34001', 1234567890, 1, 'Temp1', 'Temperature Sensor 1')

WriteSensorValues(conn, '5', '%', '2017-09-29 03:15:34.002', 2480248024, 1, 'Humd1', 'Relative Humidity Sensor 1')
WriteSensorValues(conn, '5', '%', '2017-09-29 04:15:34.002', 2480248024, 1, 'Humd1', 'Relative Humidity Sensor 1')
WriteSensorValues(conn, '5', '%', '2017-09-29 05:15:34.002', 2480248024, 1, 'Humd1', 'Relative Humidity Sensor 1')
WriteSensorValues(conn, '9', '%', '2017-09-29 06:15:34.002', 2480248024, 1, 'Humd1', 'Relative Humidity Sensor 1')
WriteSensorValues(conn, '23', '%', '2017-09-29 07:15:34.002', 2480248024, 1, 'Humd1', 'Relative Humidity Sensor 1')
WriteSensorValues(conn, '75', '%', '2017-09-29 08:15:34.002', 2480248024, 1, 'Humd1', 'Relative Humidity Sensor 1')
WriteSensorValues(conn, '100', '%', '2017-09-29 09:15:34.002', 2480248024, 1, 'Humd1', 'Relative Humidity Sensor 1')
WriteSensorValues(conn, '100', '%', '2017-09-29 10:15:34.002', 2480248024, 1, 'Humd1', 'Relative Humidity Sensor 1')
WriteSensorValues(conn, '100', '%', '2017-09-29 11:15:34.002', 2480248024, 1, 'Humd1', 'Relative Humidity Sensor 1')
WriteSensorValues(conn, '90', '%', '2017-09-29 12:15:34.002', 2480248024, 1, 'Humd1', 'Relative Humidity Sensor 1')
WriteSensorValues(conn, '87', '%', '2017-09-29 13:15:34.002', 2480248024, 1, 'Humd1', 'Relative Humidity Sensor 1')
WriteSensorValues(conn, '72', '%', '2017-09-29 14:15:34.002', 2480248024, 1, 'Humd1', 'Relative Humidity Sensor 1')
WriteSensorValues(conn, '50', '%', '2017-09-29 15:15:34.002', 2480248024, 1, 'Humd1', 'Relative Humidity Sensor 1')

WriteSensorValues(conn, '1020', 'mBar', '2017-10-07 02:42:49.003', 3690369036, 1, 'Press1', 'Absolute Pressure Sensor 1')
WriteSensorValues(conn, '1019', 'mBar', '2017-10-07 04:42:49.003', 3690369036, 1, 'Press1', 'Absolute Pressure Sensor 1')
WriteSensorValues(conn, '1016', 'mBar', '2017-10-07 06:42:49.003', 3690369036, 1, 'Press1', 'Absolute Pressure Sensor 1')
WriteSensorValues(conn, '1012', 'mBar', '2017-10-07 08:42:49.003', 3690369036, 1, 'Press1', 'Absolute Pressure Sensor 1')
WriteSensorValues(conn, '1008', 'mBar', '2017-10-07 10:42:49.003', 3690369036, 1, 'Press1', 'Absolute Pressure Sensor 1')
WriteSensorValues(conn, '1004', 'mBar', '2017-10-07 12:42:49.003', 3690369036, 1, 'Press1', 'Absolute Pressure Sensor 1')
WriteSensorValues(conn, '996', 'mBar', '2017-10-07 14:42:49.003', 3690369036, 1, 'Press1', 'Absolute Pressure Sensor 1')
WriteSensorValues(conn, '994', 'mBar', '2017-10-07 16:42:49.003', 3690369036, 1, 'Press1', 'Absolute Pressure Sensor 1')
WriteSensorValues(conn, '994', 'mBar', '2017-10-07 18:42:49.003', 3690369036, 1, 'Press1', 'Absolute Pressure Sensor 1')
WriteSensorValues(conn, '995', 'mBar', '2017-10-07 21:42:49.003', 3690369036, 1, 'Press1', 'Absolute Pressure Sensor 1')


print ("Completed")

