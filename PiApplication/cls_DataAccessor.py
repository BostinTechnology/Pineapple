"""
Contains the required AWS Connection Utilities

#TODO: If there is no db connection, will capture the data in local file ready for transmit
    This will require some space management so that we don't overfill the card.
    If it was really clever, it would create a separate thread to handle writing of the data

This needs to be converted to a class and handle many additional functions like
- no network connection
- connecting to the restful interface

Process
- Data In
- Write to file

Process 2
- Data to send?
- Connected? (if not end)
- Read record(s)
- Send record(s)
- Successful? (if not end)
- Set sent flag
- More data (if so repeat read records onwards)
- Wait a period
- return to start

For initial version, connect write to file and data in file and if no ore data, end

When writing Sensor Values, TableName='SensorValues',
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

"""
###
### All this needs to be changed to suit the requirements of a class
###

import boto3
import sys
import logging

import Standard_Settings as SS


class DataAccessor:
    """
    Takes the given data and writes it to the required output.
    The output location will be dependent on the chosen settings - not sure where these are stored.
    """
    def __init__(self, device, sensor, acroynm, desc):
        self.log = logging.getLogger()
        self.log.debug("[DAcc] cls_DataAccessor initialised")
        self.device = device
        self.sensor = sensor
        self.acroynm = acroynm
        self.description = desc
        self._db_version()
        self._open_record_file()
        return
    
    def DataIn(self,data):
        """
        Receive the data, this is expected to be in the following format
        [type, value, units]
        Process
        - Data In
        - Write to file
        There is no response
        """
        if self._validate_data(data):
            self._write_data_to_file(data)
        else:
            self.log.warning("[DAcc] received data was invalid:%s" % data)
        
        return
    
    def TransmitData(self):
        """
        This routine checks for data in the file and sends it
        Ideally this is called as part of a seperate thread
        Process 2
        - Connected? (if not end)
        - Read record
        - If data, Send record
        - Successful? (if not end)
        - Set sent flag
        - More data (if so repeat read records onwards)
        - Return to start
        """
        more_data = True
        while more_data:
            if self._connected():
                record = self._read_record()
                if len(record) > 0:
                    status = self._send_record(record)
                    if status:
                        self._set_status_flag(record)
            else:
                more_data = False
                    
        
#-----------------------------------------------------------------------
#
#    P R I V A T E   F U N C T I O N S
#
#-----------------------------------------------------------------------

    def _db_version(self):
        """
        Request the database version to work with
        """
        print("db version check is not yet implemented")
        self.log.warning("[DAcc] db version check is not yet implemented")
        self.db_version = 0.1
        return
    
    def _validate_data(self):
        """
        Check the incoming data to check it contains valid values
        Need some link into the self.db_version
        """
        print("Data Validation is not yet implemented")
        self.log.warning("[DAcc] Data Validation is not yet implemented")
        return True
    
    def _check_disk_space(self):
        """
        Validate there is enough disk space to write to file
        
        """
        print("Check for disk space for the data file is not yet implemented")
        self.log.warning("[DAcc] Check for disk space for the data file is not yet implemented")
        return True
    
    def _open_record_file(self):
        """
        The name of the datafile will be standard across the range.
        Returns True if the file is open, False if not. 
        """
        print("Opening of the record file is not yet implemented")
        self.log.warning("[DAcc] Opening of the record file is not yet implemented")
        if self._check_disk_space():
            self.log.info("[DAcc] Reading the record file for sensor information")
            try:
                self.log.debug("[DAcc] Record File in location:%s" % SS.RECORDFILE_LOCATION + '/' + SS.RECORDFILE_NAME)
                self.record_file = open(SS.RECORDFILE_LOCATION + '/' + SS.RECORDFILE_NAME, mode='rt')
                ##lines = self.record_file.readlines()
                ##self._record_file.close()
                self.log.debug("[DAcc] record file loaded %s" % lines)
            except:
                self.log.critical("[DAcc] Failed to open record file, please contact support", exc_info=True)
                self.log.exception("[DAcc] _sopen_record_file Exception Information")
                sys.exit()

        return True
    
    def _write_data_to_file(self,data_to_write):
        """
        Given the data, write it to the file. If it fails, try some alternative measures
        The file will already be open for writing
        """
        print("Writing data to file is not yet implemented")
        self.log.warning("[DAcc] Writing data to file is not yet implemented")
        return True

    def _connected(self):
        """
        Check if the application is connected to the RESTful interface
        Returns True or False
        """
        print("CHecking for connection is not yet implemented")
        self.log.warning("[DAcc] Checking for connection is not yet implemented")
        
        return True
    
    def _read_record(self):
        """
        Read a record out of the record file
        return an empty string if no record to find
        """
        print("Reading of Records is not yet implemented")
        self.log.warning("[DAcc] Reading of Records is not yet implemented")
        record = ""
        return record
        
    def _send_record(self, record_to_send):
        """
        Send the given record from the record file
        return True / False based on the sending of the record
        """
        print("Sending of Records is not yet implemented")
        self.log.warning("[DAcc] Sending of Records is not yet implemented")
        record = ""
        return True
    
    def _set_status_flag(self, record_to_flag):
        """
        Set the status flag after a successful sending of a record out of the record file
        return nothing
        """
        print("Reading of Records is not yet implemented")
        self.log.warning("[DAcc] Reading of Records is not yet implemented")
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
