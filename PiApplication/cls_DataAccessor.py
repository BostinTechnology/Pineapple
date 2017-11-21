"""
Contains the required AWS Connection Utilities.

The credentials used for connection are entered by the user as part of the customer info in Control.py

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
                    'value': { 'S' : str(data)},
                    'units': { 'S' : units}
                    }},
                'Viewed': { 'BOOL' : False},
                },
"""
#TODO: Need to improve the APi connections to use the right responses (status') and handle the various choices properly.
    #   May need to handle busy, timeouts etc.
    #   I should not have prints on screen!!!

#TODO: db version check is only completed at startup or first connection. If the version changes whilst it is connected
    #    there is no check to resolve it.

#TODO: Need to improve the testing aspects to gain good coverage

#TODO: At present this assumes the MVData type will always be 1 - so the value is a number.

#TODO: I write stuff to file, but do I ever read it back? I should on start / load

#TODO: When writing data to file, it needs to check for the directory
#       Shoudl consider also file handling / space handling

import boto3
import sys
import os
import logging
import random
import json
import time
from datetime import datetime
import requests


import Standard_Settings as SS

SUPPORTED_DB_VERSIONS = [0.1, 1.0]           # Contains a list of the supported db versions.


class DataAccessor:
    """
    Takes the given data and writes it to the required output.
    The output location will be dependent on the chosen settings - not sure where these are stored.
    Device_ID: {'N': str(device)}, TimeStamp: {'S': str(tstamp)}, Sensor_ID': {'N': str(sensor)},
    SensorAcroynm': {'S' : str(acroynm)}, SensorDescription' : { 'S': str(desc)},

    """
    def __init__(self, customer, password, db, addr, port, device, sensor, acroynm, desc):
        self.log = logging.getLogger()
        self.log.debug("[DAcc] cls_DataAccessor initialised")

        #TODO: Change this to use queues https://docs.python.org/3.3/library/collections.html#collections.deque
        self.records = []
        self.db = db                    # Local, Remote or AWS database
        self.db_ok = False              # Used to flag that we have successfully checked the database versions match
        self.db_version = 0
        self.db_addr = addr
        self.db_port = port
        self.customer = customer
        self.password = password
        self.device = device
        self.sensor = sensor
        self.acroynm = acroynm
        self.description = desc
        #self._db_version_check()
        
        return

    def DataIn(self,data):
        """
        Receive the data, this is expected to be in the following format
        [[type, value, units, timestamp],[type, value, units, timestamp]]
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
        #print("Transmitting Data")
        if self.db_ok == False:
            # Not yet validated the database version, check again now. If still unknown, just return
            self.log.debug("[DAcc] db version is still undertermined, checking again now")
            if self._db_version_check() == False:
                self.log.info("[DAcc] Not currently connected, unable to validate database version")
                return False

        more_data = True
        record_try_count = 0
        while more_data:
            if self._connected():
                record = self._read_record_from_file()
                if len(record) > 0:
                    self.log.debug("[DAcc] Length of record:%s" % len(record))
                    status = self._send_records(record)
                    if status == True:
                        self._remove_record_file()
                        record_try_count = 0
                    else:
                        record_try_count = record_try_count + 1
                        if record_try_count > SS.RECORD_TRY_COUNT:
                            self.log.error("[DAcc] Failed to send record over %s times, record archived" % record_try_count)
                            self.log.info("[DAcc] Archived Record:%s" % record)
                            self._rename_record_file(record)
                        else:
                            time.sleep(record_try_count)        # Wait for a period before retrying
                else:
                    more_data = False
                    self.log.info("[DAcc} No more data records to read")
            else:
                # I'm not connected, so return
                more_data = False
                self.log.info("[DAcc] Not currently connected, so no records sent")
                return False
        return True


#-----------------------------------------------------------------------
#
#    P R I V A T E   F U N C T I O N S
#
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
#
# Functions for writing and reading from disk
#
#RECORDFILE_LOCATION = "DataFiles"           # Where to store the records file, program automatically added '/' at the end
#RECORDFILE_NAME = "DATA_"            # The Base name part of the file
#RECORDFILE_EXT = ".rec"             # The extension for the record files
#RECORDFILE_OLD = ".oldrec"          # The extension used when the record can't be written and is stored for future analysis
#RECORD_TRY_COUNT = 10               # How many times, when connected the Data Accessor will try and send a record
#EEPROM_READ_RETRY = 5               # How many times it will try and read data from the EEPROM

    def _write_data_to_file(self, data_to_write):
        """
        Takes the given data and creates a new file with the contents of it
        Format of the filename is based on standard settings
            RECORDFILE_NAME+tiemstamp+RECORDFILE_EXT
        Stored in sub folder
            RECORDFILE_LOCATION
        Returns true if the record is written, or false if it isn't
        Disk space management is handled by the calling program
        """
        status = False
        file_time = datetime.now().strftime("%y%m%d%H%M%S-%f")

        #TODO: If the datafile directoryu doesn't exist, an error is thrown!

        data_record_name = SS.RECORDFILE_LOCATION + '/' + SS.RECORDFILE_NAME + file_time + SS.RECORDFILE_EXT
        self.log.info("[DAcc] Writing new record to disk:%s" % data_record_name)

        #TODO: Need to handle a failure to open the file
        with open(data_record_name, mode='w') as f:
            json.dump(data_to_write, f)
            status = True
        return status

    def _get_file_to_use(self):
        """
        Read the list of files from the given directory

        """
        #TODO: Check for the directory existing first

        self.log.info("[DAcc] Getting the list of files to use and selecting one")
        self.record_to_use = ""
        status = False
        list_of_files = os.listdir(path=SS.RECORDFILE_LOCATION+'/.')
        list_of_files.sort()
        self.log.debug("[DAcc] Files to Use :%s" % list_of_files)
        for i in list_of_files:
            self.log.debug("[DAcc] File being checked for extension of %s:%s" % (SS.RECORDFILE_EXT, i))
            if i[-len(SS.RECORDFILE_EXT):] == SS.RECORDFILE_EXT:
                self.record_to_use = i
                status = True
                break
        self.log.info("[DAcc] Selected File to use:%s" % self.record_to_use)
        return status

    def _read_record_from_file(self):
        """
        Read a record out of the record file location
        Return an empty string if no record to find
        """
        record = []
        if self._get_file_to_use():
            file_name = SS.RECORDFILE_LOCATION + '/' + self.record_to_use
            self.log.debug("[DAcc] File being opened:%s" % file_name)
            with open(file_name, mode='r') as f:
                record = json.load(f)
                #BUG: The line above is reading [] and assuming it is a string and not a list!
        self.log.debug("[DAcc] Record obtained from the records file:%s" % record)
        return record


    def _remove_record_file(self):
        """
        Remove the file from the directory
        """

        if os.path.isfile(SS.RECORDFILE_LOCATION+'/' + self.record_to_use):
            os.remove(SS.RECORDFILE_LOCATION+'/' + self.record_to_use)
            self.log.info("[DAcc] Record File deleted:%s" % SS.RECORDFILE_LOCATION+'/' + self.record_to_use)
        return

    def _rename_record_file(self):
        """
        Rename the current file to the old name so it is no longer sent
        """
        if os.path.isfile(SS.RECORDFILE_LOCATION+'/' + self.record_to_use):
            os.rename(SS.RECORDFILE_LOCATION+'/' + self.record_to_use, SS.RECORDFILE_LOCATION+'/' + self.record_to_use[-3:] + SS.RECORDFILE_OLD)
            self.log.info("[DAcc] Record File renamed:%s" % SS.RECORDFILE_LOCATION+'/' + self.record_to_use[-3:] + SS.RECORDFILE_OLD)
        return


#-----------------------------------------------------------------------
#
# Functions for Data In
#

    def _validate_data(self,dataset):
        """
        Check the incoming data to check it contains valid values
        Need some link into the self.db_version
        For each part of the dataset must contain 4 items,
        mvdata['type'] = {'S' : str(item[0])}
        mvdata['value'] = {'S' : str(item[1])}
        mvdata['units'] = {'S' : str(item[2])}
        data_record['TimeStamp'] = { 'S' : str(item[3])}
        """
        valid_data_record = True
        for item in dataset:
#            if str(item[0]).isdigit() == False:
            if isinstance(item[0], (int, float)) == False:
                self.log.info("[DAcc] 1st part (type) of the dataset failed as it is not a number, dataset:%s" % dataset)
                valid_data_record = False
            else:
                if item[0] < 1 or item[0] > 4:
                    self.log.info("[DAcc] 1st part (type) of the dataset failed as it is outside valid range (1-4), dataset:%s" % dataset)

            if isinstance(item[1], (int, float)) == False:
                self.log.info("[DAcc] 2nd part (value) of the dataset failed as it not a number, dataset:%s" % dataset)
                valid_data_record = False

            if len(item[2]) < 1:
                self.log.info("[DAcc] 3rd part (units) of the dataset failed as it is too short (<1), dataset:%s" % dataset)
                valid_data_record = False

            if len(item[3]) < 19:
                self.log.info("[DAcc] 4th part (timestamp) of the dataset failed as it is too short (<23), dataset:%s" % dataset)
                valid_data_record = False

        return valid_data_record

#-----------------------------------------------------------------------
#
# Functions for Transmit Data
#
    def _is_number(self, check):
        """
        Check if the string passed into check is a number or a string
        """
        self.log.debug("[DAcc] Checking %s is a number" % check)
        try:
            float(check)
            return True
        except:
            return False

    def _db_version(self):
        """
        Request the database version to work with.
        Sets the db_version according to the version being implemented in the database
        Wil set it to -1 if it fails.
        Possible status _code responses: 200 OK, 400 Bad Request, 403 Forbidden, 501 Not Implemented
        """
        #TODO: Validate response and return fail accordingly
        self.log.warning("[DAcc] DB Version is not fully implemented, validation required")

        payload = {'id': self.customer, 'auth':self.password, 'dest':self.db}
        r = requests.get('http://'+self.db_addr+':'+self.db_port+'/retrievedbversion', data=payload)

        if r.status_code ==200:
            self.log.debug("[DACC] db version retrieved from RESTFul API:%s" % r.text)
            if self._is_number(r.text):
                self.db_version = float(r.text)
                self.log.info("[DAcc] version being used:%s" % self.db_version)
                return True
            else:
                self.log.warning("[DACC] Version Number read from the database is not a number")
                self.log.debug("[DACC] Database Version Read info:%s:%s" % (r.status_code, r.text))
                return False

        else:
            self.log.warning("[DACC] Failed to Read the database version from the RESTFul API")
            self.log.debug("[DACC] Database Version Read info:%s:%s" % (r.status_code, r.text))
            return False
        return

    def _db_version_check(self):
        """
        Check the database version matches the version this software is designed for.
        End program if different, return false if unknown
        """
        if self._connected():
            self._db_version()
            if self.db_version not in SUPPORTED_DB_VERSIONS:
                self.log.critical("[DAcc] Database version is not supported, got:%s, expected:%s"
                            % (self.db_version, SUPPORTED_DB_VERSIONS))
                print("\nCRITICAL ERROR, Database version is not supported - contact Support\n")
                sys.exit()
            else:
                self.db_ok = True
        else:
            self.log.info("[DAcc] Unable to validate db version as not connected, assuming wrong version.")
            self.db_ok = False
        return self.db_ok

    def _read_record_from_list(self):
        """
        Read a record out of the record file
        Return an empty string if no record to find
        """
        record = []
        if len(self.records) > 0:
            record = self.records[0]
        self.log.debug("[DAcc] Record obtained from the records file:%s" % record)
        return record

    def _remove_record_from_list(self,record_to_delete):
        """
        Remove record zero from the records file
        Checks the record given matches the one it is about to remove before removing it
        After removing it from the records, updates the file on disk
        """

        #TODO: Consider adding the removed record to an old list.

        compare = self.records[0]
        if len(compare) > 0:
            if compare == record_to_delete:
                self.records.pop(0)
                self.log.debug("[DAcc] Removed record zero from the list, record was:%s" % compare)
            else:
                self.log.warning("[DAcc] When trying to remove record, it didn't match expected so no record removed")
            self._update_record_file()
        else:
            self.log.debug("[DAcc] tried to remove record zero but self.records was empty")
        return

    def _connected(self):
        """
        Check if the application is connected to the RESTful interface
        Returns True or False
        Possible status _code responses: 200 OK, 400 Bad Request, 403 Forbidden, 404 - Not Found, 501 Not Implemented

        """
        #TODO: Validate response and return fail accordingly
        self.log.warning("[DAcc] Checking for connection is not fully implemented, validation required")

        payload = {'dest':self.db}
        r = requests.get('http://'+self.db_addr+':'+self.db_port+'/connected', data=payload)

        if r.status_code ==200:
            self.log.debug("[DACC] connected returned from RESTFul API:%s" % r)
            return True
        else:
            self.log.warning("[DACC] Failed to connect to the RESTFul API at:%s" % ('http://'+self.db_addr+':'+self.db_port+'/connected'))
            self.log.debug("[DACC] Connected info:%s" % r)
            return False
        return

    def _post_record(self, data_to_send):
        """
        Given the dataset, send it to the RESTFul interface and return success or failure

        """
        #TODO: Validate response and return fail accordingly
        self.log.warning("[DAcc] Posting of Records is not fully implemented, validation required:%s" % data_to_send)

        payload = {'id': self.customer, 'auth':self.password, 'dest':self.db, 'data':json.dumps(data_to_send)}
        r = requests.post('http://'+self.db_addr+':'+self.db_port+'/submitdata', data=payload)

        if r.status_code ==200:
            print('Header:%s' % r.headers)
            print('Status Code:%s' % r.status_code)
            print('Text:%s' % r.text)
        else:
            print('Failed to Read')
            print('Status Code:%s' % r.status_code)
            return False
        return True

    def _send_records(self, data_in):
        """
        Send the given record set from the record file
        return True / False based on the sending of the record
        {
                'Device_ID': {'N': str(self.device)},
                'TimeStamp': {'S': str(tstamp)},
                'Sensor_ID': {'N': str(self.sensor)},
                'SensorAcroynm': {'S' : str(self.acroynm)},
                'SensorDescription' : { 'S': str(self.description)},

                THE BELOW BIT DOES NOT HOLD TRUE WITH DOCUMENTATION
                - Need to review how to store the info.

                'MVData': { 'M' :
                    {                     # Multiple sets of values require seperate records
                    'type': { 'S' : '1'},
                    'value': { 'S' : str(data)},
                    'units': { 'S' : units}
                    }
                    },
                'Viewed': { 'BOOL' : False},
                },

        if data_in contains multiple datasets, send each record independently
        The format of the data sent could be different for different data versions
        """
        response = True
        if self.db_version in [0.1, 1.0]:
            for item in data_in:
                data_record = {}
                data_record['Device_ID'] = { 'N' : str(self.device)}
                data_record['Sensor_ID'] = { 'N' : str(self.sensor)}
                data_record['TimeStamp'] = { 'S' : str(item[3])}
                data_record['SensorAcroynm'] = { 'S' : str(self.acroynm)}
                data_record['SensorDescription'] = { 'S' : str(self.description)}
                mvdata = {}
                mvdata['type'] = {'S' : str(item[0])}
                mvdata['value'] = {'S' : str(item[1])}
                mvdata['units'] = {'S' : str(item[2])}
                data_record['MVData'] = { 'M' : mvdata}
                data_record['Viewed'] = { 'BOOL' : False}

                self.log.debug("[DAcc] Data Record to be sent:%s" % data_record)

                response = response & self._post_record(data_record)
        else:
            response = False
            self.log.info("[DAcc] In _send_records, db check failed, no data sent")

        return response

#-----------------------------------------------------------------------
#
#    T E S T   F U N C T I O N S
#
#-----------------------------------------------------------------------


def GenerateTimestamp():
    now = str(datetime.now())
    print("[DAcc] Generated a timestamp %s" % now[:23])
    return now[:23]

def GenerateTestData():
    """
    Generate a dataset to represent the simulated input
    [type, number, units]
    """
    types = [1,2,3,4]
    units = ['lux', 'Deg C', 'Deg F', '%', 'tag']
    dataset = [[]]
    dataset[0].append(types[random.randint(0,len(types)-1)])
    dataset[0].append(random.randint(0,100))
    dataset[0].append(units[random.randint(0,len(units)-1)])
    dataset[0].append(GenerateTimestamp())
    print("Data Being Returned:%s" % dataset)

    return dataset

def SetupLogging():
    """
    Setup the logging defaults
    Using the logger function to span multiple files.
    """
    print("Current logging level is \n\n   DEBUG!!!!\n\n")

    # Create a logger with the name of the function
    logging.config.dictConfig(dict_LoggingSetup.log_cfg)
    log = logging.getLogger()

    #BUG: This is loading the wrong values into the log file
    log.info("File Logging Started, current level is %s" % log.getEffectiveLevel)
    log.info("Screen Logging Started, current level is %s" % log.getEffectiveLevel)

    return

def main():
    print("Sending Data In")
    # Need to add comms handler and calib data to test with
    # customer, password, db, addr, port, device, sensor, acroynm, desc
    dacc = DataAccessor(customer='m@mlb.com', password='password', db=SS.DB_LOCAL, addr=SS.DB_LOCAL_ADDR, port=SS.DB_LOCAL_PORT,
                        device=1, sensor=2, acroynm="Lght1", desc="Light Sensor 1")
    for i in range(0,10):
        dacc.DataIn(GenerateTestData())
    print("\nTransmitting Data\n")
    dacc.TransmitData()

if __name__ == '__main__':
    import logging
    import logging.config
    import dict_LoggingSetup
    SetupLogging()

    main()
    #TODO: when run seperately this needs to transmit data
