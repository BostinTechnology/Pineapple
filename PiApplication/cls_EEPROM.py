#!/usr/bin/env python3
"""
Need to add info in here.

This class extractgs and holds the information about the iCog that has been extracted from the 
datafile or the EEPROM associated with the sensor

On intialisation, the EEPROM class should
- read the values from the iCog EEPROM
- load the datafile and set additional acronymn data

"""

import random
import sys
import logging

import Standard_Settings as SS

ID_IOT_CHIP_ADDR = 0x50

# Support EEPROM Map versions
EEPROM_MAP_VERSION_0_2 = [0x00, 0x02]

# EEPROM Mapping, the list below are registery locations
EEPROM_ADDR_MAP_VERSION = 0x00
EEPROM_ADDR_CHECKSUM = 0x0e
EEPROM_ADDR_DEVICE_CONNECT = 0x10
EEPROM_ADDR_UUID = 0xfc
EEPROM_UUID_LEN = 4
EEPROM_ADDR_ICOG_CONFIG = 0x20      #The start address for the icog configuration data


class ID_IoT():
    """
    This class needs to hold everything extracted from the ID-IoT EEPROM associated to the iCog
    
    self.datafile contains the information read from the external file.
    """

    def __init__(self, comms_handler, read_chip=True):
        """
        Initialises the values and checkes if they have been previously saved as a tuple
        
        Requires the i2c bus reference to be passed into it.
        On intialisation, the EEPROM class should
        - read the values from the iCog EEPROM
        - load the datafile and set additional data
        """
        self.log = logging.getLogger()

        self._clear_data()
        self.comms = comms_handler
        if read_chip:
            # Default is to read the chip, but option exists not to.
            status = self._read_sensor_data_from_eeprom()
        else:
            status = False
            print("Reading of chip disabled")

        self.log.info("[EEPROM] Initialisation of the EEPROM has been completed")
        self.eeprom_status = status
        return
    
    def ReturnEEPROMStatus(self):
        return self.eeprom_status
    
    def ReturnUUID(self):
        return self.uuid
    
    def ReturnBusType(self):
        """
        Returns the bus type from Standard_Settings
        SS.I2C, SS.SPI, SS.SERIAL
        """
        return self.bustype

    def ReturnMapVersion(self):
        return self.map_version
        
    def ReturnSensorAddress(self):
        return self.sensoraddress

    def ReturnSPIBus(self):
        return self.spi_bus
        
    def ReturnSPI_CELine(self):
        return self.spi_celine
        
    def ReturnGPIOPin(self):
        return self.gpio_pin
        
    def ReturnSerialCTSRTS(self):
        return self.serial_rtc_cts
        
    def ReturnSensorType(self):
        return self.sensor_type
        
    def ReturnMinimumRevision (self):
        return self.minimum_revision
        
    def ReturnInputOutput1(self):
        return self.io_1
        
    def ReturnInputOutput2(self):
        return self.io_2
        
    def ReturnCalibrationData(self):
        return self.calibration_data

    def ReturnSensorCommsFile(self):
        """
        Returns the name of the icog file to be used
        """
        return self.sensor_comms_file
        
    def ReturnSensorPartNumber(self):
        return self.sensor_part_number
        
    def ReturnSensorType(self):
        return self.sensor_type
        
    def ReturnSensorManufacturer(self):
        return self.sensor_manufacturer
    
    def SetMapVersion(self, version):
        """
        Set the map version in the ID-IoT form the given list of 2 values
        Uses EEPROM_ADDR_MAP_VERSION as the starting address
        Used as part of the ID_IoT setup only.
        """
        reply = False
        if len(version) < 1:
            # Dataset is empty
            self.log.warning("[EEPROM] Dataset passed into SetMapVersion for processing is empty")
        else:
            reply = self.comms.write_data_bytes(ID_IOT_CHIP_ADDR, EEPROM_ADDR_MAP_VERSION, version)
        self.log.debug("[EEPROM] Set Map Version response status (1=True):%s" % reply)
        return reply
    
    def SetDeviceConnectivityData(self, dataset):
        """
        Taking the dataset, program it into the ID-IoT, given a list of 16 bytes
        Uses EEPROM_ADDR_DEVICE_CONNECT as the starting address
        Returns True or False
        Used as part of the ID_IoT setup only.
        """
        self.log.info("[EEPROM] Set Device Connectivity with dataset:%s" % dataset)
        reply = False
        if len(dataset) < 1:
            # Dataset is empty
            self.log.warning("[EEPROM] Dataset passed into SetDeviceConnectivityData for processing is empty")
        else:
            reply = self.comms.write_data_bytes(ID_IOT_CHIP_ADDR, EEPROM_ADDR_DEVICE_CONNECT, dataset)
        self.log.debug("[EEPROM] Set Device Connectivity response status (1=True):%s" % reply)
        return reply

    def ResetCalibrationData(self, dataset):
        """
        Given the dataset which contains all the values to be written to the ID_IoT starting at EEPROM_ADDR_ICOG_CONFIG
        Assumes the dataset given fits into the space
        
        """
        self.log.info("[EEPROM] Reset Calibration Data with data:%s" % dataset)
        start_address = EEPROM_ADDR_ICOG_CONFIG
        for block in dataset:
            self.log.debug("[EEPROM] Start Address:%s data block:%s" % (start_address, block))
            self.comms.write_data_bytes(ID_IOT_CHIP_ADDR, start_address, block)
            start_address = start_address + len(block)
        return

#-----------------------------------------------------------------------
#
#    P R I V A T E   F U N C T I O N S
#
#-----------------------------------------------------------------------


    def _clear_data(self):
        """
        Reset all the EEPROM values to default
        """
        self.eeprom_status = False
        self.comms = ''
        self.bustype = ''
        self.map_version = []
        self.sensoraddress = 0
        self.spi_bus = 0
        self.spi_celine = 0
        self.gpio_pin = 0
        self.serial_rtc_cts = 0
        self.sensor_type = []
        self.minimum_revision = []
        self.io_1 = []
        self.io_2 = []
        self.calibration_data = []
        self.sensor_comms_file = ''
        self.sensor_part_number = ''
        self.sensor_type = ''
        self.sensor_manufacturer = ''
  
        return
        
    def _read_sensor_data_from_eeprom(self):
        """
        Interface with the EEPROM and get the sensor details
        Sets
            uuid, bustype, busnumber, sensoraddress, sensor, manufacturer, status
        returns status if the read was successful.
        """
        
        self.map_version = self.comms.read_data_bytes(ID_IOT_CHIP_ADDR, EEPROM_ADDR_MAP_VERSION, 2)
        
        self.eeprom_checksum = self.comms.read_data_bytes(ID_IOT_CHIP_ADDR, EEPROM_ADDR_CHECKSUM, 2)
        
        self.log.info("[EEPROM] Map Version:%s" % self.map_version)
        self.log.info("[EEPROM] EEPROM Checksum:%s" self.eeprom_checksum)
        #TODO: Implement checksum check
        
        # Check if the map version is supported
        if self.map_version == EEPROM_MAP_VERSION_0_2:
            self._read_map_version_0_2()
        else:
            self.log.critical("[EEPROM] Map Version read from Id_IOT is not supported, value received:%s" % self.map_version)
            print("\nCRITICAL ERROR, EEPROM Map Version is not supported- contact Support\n")

            sys.exit()
        
        # Set additional info
        self._set_additional_data()
        self._set_uuid()
        return
            
    def _read_map_version_0_2(self):
        """
        Read the data from the map, version 0.2
        """
        # read device connectivity data
        row_10 = self.comms.read_data_bytes(ID_IOT_CHIP_ADDR, EEPROM_ADDR_DEVICE_CONNECT, SS.CALIB_PAGE_LENGTH)
        
        if len(row_10) < 1:
            #No data received
            self.log.critical("[EEPROM] EEPROM Map read from Id_IOT did not return any data, value received:%s" % row_10)
            print("\nCRITICAL ERROR, EEPROM Map Read Failure- contact Support\n")
            sys.exit()
                    
        # decode the device connectivity data
        # bytes 0,1,2 = device info
        if row_10[0] == 0b00000001:
            self.bustype = SS.I2C
            self.sensoraddress = row_10[1]
        elif row_10[0] == 0b00000010:
            self.bustype = SS.SPI
            self.spi_bus = row_10[2] & 0b10000000           # Bit 7 indicates the SPI bus - 0 or 1
            self.spi_celine = row_10[2] & 0b01000000        # Bit 6 indicates the CE Line
            self.gpio_pin = row_10[2] & 0b00111111          # Bit 5 - 0 indicate the GPIO pin
        elif row_10[0] == 0b00000100:
            self.bustype = SS.SERIAL
        else:
            self.bustype = ''
        # bytes 3,4 - Serial RTS and CTS info
        self.serial_rtc_cts = row_10[3:5]
        # bytes 5,6 - Sensor type
        self.sensor_type_code = row_10[5:7]
        # minimum revision 7 - 9 (a.b.c)
        self.minimum_revision = row_10[7:10]
        # input / output 1 & 2
        self.io_1 = row_10[10:12]
        self.io_2 = row_10[12:14]
        
        self.log.info("[EEPROM] Device Connectivity Data - bus type:%s" % self.bustype)
        self.log.info("[EEPROM] Device Connectivity Data - sensor address:%s" % self.sensoraddress)
        self.log.info("[EEPROM] Device Connectivity Data - SPI bus:%s" % self.spi_bus)
        self.log.info("[EEPROM] Device Connectivity Data - SPI CE Line:%s" % self.spi_celine)
        self.log.info("[EEPROM] Device Connectivity Data - GPIO Pin:%s" % self.gpio_pin)
        self.log.info("[EEPROM] Device Connectivity Data - Serial RTC CTS:%s" % self.serial_rtc_cts)
        self.log.info("[EEPROM] Device Connectivity Data - Sensor Type:%s" % self.sensor_type)
        self.log.info("[EEPROM] Device Connectivity Data - Minimum Revision:%s" % self.minimum_revision)
        self.log.info("[EEPROM] Device Connectivity Data - I/O Pin 1:%s" % self.io_1)
        self.log.info("[EEPROM] Device Connectivity Data - I/O Pin 2:%s" % self.io_2)
        
        # Read Calibration Values
        self.calibration_data = []
        for row in range(EEPROM_ADDR_ICOG_CONFIG, 0x80,0x10):
            data = self.comms.read_data_bytes(ID_IOT_CHIP_ADDR, row, SS.CALIB_PAGE_LENGTH)
            if len(data) < SS.CALIB_PAGE_LENGTH:
                #No data received
                self.log.warning("[EEPROM] EEPROM Map Calibration data read from Id_IOT did not return any data, value received:%s" % row_10)
                print("\nERROR, EEPROM Map Calibration Data Read Failure- contact Support\n")
                data = [0]*SS.CALIB_PAGE_LENGTH          # Set it to default of zero's
            self.calibration_data.append(data)
            self.log.debug("[EEPROM] Calibration Data read from Id_IoT address %s :%s" % (row,data))
        self.log.info("[EEPROM] Complete Calibration datafile retrieved:%s" % self.calibration_data)
        return
        
    def _set_additional_data(self):
        """
        Sets the additional information about the sensor, based on the data file
        Loads the datafile into a 
                self.sensor_comms_file
                self.sensor_part_number
                self.sensor_type
                self.sensor_manfacturer
        """
        self.datafile = []
        self.log.info("[EEPROM] Reading the datafile for sensor information")
        try:
            self.log.debug("[EEPROM] DataFile in location:%s" % SS.DATAFILE_LOCATION + '/' + SS.DATAFILE_NAME)
            data = open(SS.DATAFILE_LOCATION + '/' + SS.DATAFILE_NAME, mode='rt')
            lines = data.readlines()
            data.close()
            self.log.debug("[EEPROM] datafile loaded %s" % lines)
        except:
            self.log.critical("[EEPROM] Failed to Open datafile, please contact support")
            self.log.exception("[EEPROM] _set_additional_data Exception Information")
            sys.exit()

        self.log.info("[EEPROM] Decoding the datafile, line by line")
        for f in lines:
            # Read a line of data in and strip any unwanted \n type characters
            dataline = f.strip()
            # split the data by a comma into a list.
            row_data = dataline.split(",")
            self.datafile.append(row_data)
            self.log.debug("[EEPROM] Row of extracted data %s" % row_data)
            
        #Now loop through the data string and extract the acroynm and description
        self.log.info("[EEPROM] Loop through datafile and set sensor information")
        # Uses the self.sensor_type read from the Device Connectivity Data
        for element in self.datafile:
            if int(element[4],16) == self.sensor_type_code[0] and int(element[5],16) == self.sensor_type_code[1]:
                self.log.debug("[EEPROM] Match found for Sensor and Description")
                self.sensor_comms_file = element[0]
                self.sensor_part_number = element[1]
                self.sensor_type = element[2]
                self.sensor_manufacturer = element[3]

        if len(self.sensor_comms_file) < 1:
            self.log.critical("[EEPROM] No match found for Sensor and Description: %s" % self.sensor_type_code)
                
        self.log.debug("[EEPROM] Comms File:%s, Sensor: %s Part Number:%s and Manufacturer:%s match found" 
            %(self.sensor_comms_file, self.sensor_type, self.sensor_part_number, self.sensor_manufacturer))        
        
        return

    def _set_uuid(self):
        """
        Read the data from the map, version 0.2
        """
        data = []
        # read device connectivity data
        data = self.comms.read_data_bytes(ID_IOT_CHIP_ADDR, EEPROM_ADDR_UUID , EEPROM_UUID_LEN)
        
        #BUG: If data is null
        if len(data) < 1:
            #No data received
            self.log.critical("[EEPROM] EEPROM UUID read from Id_IOT did not return any data, value received:%s" % data)
            self.uuid = 0xfa17ed
        else:
            #self.uuid = data[0] << 24 + data[1] << 16 + data[2] <<8 + data[3]
            self.uuid = ''
            for i in data:
                self.uuid = self.uuid + ('{:02x}'.format(i))
        self.log.debug("[EEPROM] UUID Valued:%s" % self.uuid)

        return

 
class TestCommsHandler():
    """
    Used to test the cls_EEPROM
    """
    
    def __init__(self):
        self.data =[0x00, 0x02, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
                    0x10, 0x11, 0x12, 0x13, 0x14, 0x02, 0x01, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f,
                    0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x2c, 0x2d, 0x2e, 0x2f,
                    0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x3b, 0x3c, 0x3d, 0x3e, 0x3f,
                    0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4a, 0x4b, 0x4c, 0x4d, 0x4e, 0x4f,
                    0x50, 0x51, 0x52, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x5a, 0x5b, 0x5c, 0x5d, 0x5e, 0x5f,
                    0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6a, 0x6b, 0x6c, 0x6d, 0x6e, 0x6f,
                    0x70, 0x71, 0x72, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x79, 0x7a, 0x7b, 0x7c, 0x7d, 0x7e, 0x7f,
                    0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89, 0x8a, 0x8b, 0x8c, 0x8d, 0x8e, 0x8f,
                    0x90, 0x91, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9a, 0x9b, 0x9c, 0x9d, 0x9e, 0x9f,
                    0xa0, 0xa1, 0xa2, 0xa3, 0xa4, 0xa5, 0xa6, 0xa7, 0xa8, 0xa9, 0xaa, 0xab, 0xac, 0xad, 0xae, 0xaf,
                    0xb0, 0xb1, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xb9, 0xba, 0xbb, 0xbc, 0xbd, 0xbe, 0xbf,
                    0xc0, 0xc1, 0xc2, 0xc3, 0xc4, 0xc5, 0xc6, 0xc7, 0xc8, 0xc9, 0xca, 0xcb, 0xcc, 0xcd, 0xce, 0xcf,
                    0xd0, 0xd1, 0xd2, 0xd3, 0xd4, 0xd5, 0xd6, 0xd7, 0xd8, 0xd9, 0xda, 0xdb, 0xdc, 0xdd, 0xde, 0xdf,
                    0xe0, 0xe1, 0xe2, 0xe3, 0xe4, 0xe5, 0xe6, 0xe7, 0xe8, 0xe9, 0xea, 0xeb, 0xec, 0xed, 0xee, 0xef,
                    0xf0, 0xf1, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6, 0xf7, 0xf8, 0xf9, 0xfa, 0xfb, 0xfc, 0xfd, 0xfe, 0xff
                    ]
        self.log = logging.getLogger()
        return
    
    def read_data_bytes(self, sens_addr, start_byte, no_bytes):
        """
        
        """
        if start_byte > 0xff:
            self.log.debug("[TEST] Data byte requested (%s) out of range, returning nothing" % start_byte)
            response = []
        else:
            response = self.data[start_byte:start_byte+no_bytes]
        self.log.debug("[TEST] Data returned;%s" % response)
        return response

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

def selftest():
    
    testcomms = TestCommsHandler()
    eeprom = ID_IoT(testcomms)
    return 0

if __name__ == '__main__':
    
    # setup logging
    
    import logging
    import logging.config
    import dict_LoggingSetup
    SetupLogging()
    # use a default class for comms and therefore allow it to be dummy data.
    #import cls_comms
    
    
    selftest()

