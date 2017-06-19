#!/usr/bin/env python3
"""
Need to add info in here.

This class extractgs and holds the information about the iCog that has been extracted from the 
datafile or the EEPROM associated with the sensor

On intialisation, the EEPROM class should
- read the values from the iCog EEPROM
- load the datafile and set additional acronymn data

"""

#TODO: Modify the code to take the comms handler being passed in and to use it to 
#       read data from the device.



import random
import smbus

#Bus types
I2C = "I2C"
SPI = "SPI"
SERIAL = "Serial"

ID_IOT_CHIP_ADDR = 0x50

class ID_IoT():
    """
    This class needs to hold everything extracted from the ID-IoT EEPROM associated to the iCog
    
    self.datafile contains the information read from the external file.
    """

    def __init__(self):
        #TODO: Read the EEPROM and process the data - could this be set globals function?
        #       Check for a tuple first - if UUID matches, use the data
        #       Create a iCOG class holding the sensor data
        #       turple the data for future use
        """
        Initialises the values and checkes if they have been previously saved as a tuple
        
        Requires the i2c bus reference to be passed into it.
        On intialisation, the EEPROM class should
        - read the values from the iCog EEPROM
        - load the datafile and set additional acronymn data
        """
        #TODO: Not yet implemented
        #readfrequency is the time between reading of values

        self.comms = comms_handler
        status = self._read_sensor_data_from_eeprom()
        if status:
            status = self._set_acroymn_data()
        
        #BUG - This should be set higher, but is changed for testing
        self.readfrequency = 3
        log.debug("iCOG initialised, read frequency set to %s" % self.readfrequency)
        
        log.info("[EEPROM] Initialisation of the EEPROM has been completed with status: %s" % status)
        self.comms_status = status
        return
    
    def ReturnCommsStatus(self):
        return self.comms_status
    
    def ReturnUUID(self):
        return self.uuid
    
    def ReturnBusType(self):
        return self.bustype
    
    def ReturnBusNumber(self):
        return self.busnumber
        
    def ReturnSensorAddress(self):
        return self.sensoraddress
        
    def ReturnSensor(self):
        return self.sensor
    
    def ReturnManufacturer(self):
        return self.manufacturer
    
    def ReturnReadFrequency(self):
        return self.readfrequency

#-----------------------------------------------------------------------
#
#    P R I V A T E   F U N C T I O N S
#
#-----------------------------------------------------------------------


    def _read_sensor_data_from_eeprom(self):
        """
        Interface with the EEPROM and get the sensor details
        Sets
            uuid, bustype, busnumber, sensoraddress, sensor, manufacturer, status
        returns status if the read was successful.
        """
        
        print("Not yet implemented - the read of the EEPROM")
        logging.warning("Not yet implemented the read of the EEPROM")
        # Use self.comms to work with the comms handler.
        
        sensor_id = random.randint(0,2)
        print("Sensor ID randomly selected %f" % sensor_id)
        log.info("Sensor ID randomly selected %f" % sensor_id)
        
        if sensor_id == 0:
            self.bustype = I2C
            self.busnumber = 1
            self.sensoraddress = "Ox50"
            self.uuid= 0x12345678
            self.sensor = 12
            self.manufacturer = 1
            status = True
        elif sensor_id == 1:
            self.bustype = I2C
            self.busnumber = 1
            self.sensoraddress = "Ox51"
            self.uuid= 0x00000001
            self.sensor = 12
            self.manufacturer = 1
            status = True
        elif sensor_id == 2:
            self.bustype = I2C
            self.busnumber = 1
            self.sensoraddress = "Ox52"
            self.uuid= 0x00000002
            self.sensor = 12
            self.manufacturer = 1
            status = True
        else:
            self.bustype = ""
            self.busnumber = 0
            self.sensoraddress = ""
            self.uuid= 0
            self.sensor = 0
            self.manufacturer = 0
            self.status= False
            #TODO: Implement something here
            log.critical("Unable to Read EEPROM, program halted")
            #print ("unable to read EEPROM") removed as now log statement
            sys.exit()
        
        return status
        
    def _set_acroymn_data(self):
        """
        This must be run after GetSensorDataFromEEPROM
        Sets the additional information about the sensor, based on the data file
        Loads the datafile into a 
            - Sensor Acroynm (self.sensoracroynm)
            - Sensor Description (seslf.sensordescription)
            - Read Frequency (self.readfrequency)
        
        #TODO: This should only be run if the customer hasn't set values first.
        #TODO: Reading fo the datafile should only be done once and not for each sensor
        """
        #TODO: Validate the error checking around this
        self.datafile = []
        log.info("Reading the datafile for sensor information")
        try:
            log.debug("DataFile in location:%s" % DATAFILE_LOCATION + '/' + DATAFILE_NAME)
            data = open(DATAFILE_LOCATION + '/' + DATAFILE_NAME, mode='rt')
            lines = data.readlines()
            data.close()
            log.debug("datafile loaded %s" % lines)
        except:
            log.critical("Failed to Open datafile, please contact support", exc_info=True)
            sys.exit()

        log.info("Decoding the datafile, line by line")
        for f in lines:
            # Read a line of data in and strip any unwanted \n type characters
            dataline = f.strip()
            # split the data by a comma into a list.
            row_data = dataline.split(",")
            self.datafile.append(row_data)
            log.debug("Row of extracted data %s" % row_data)
            
        #Now loop through the data string and extract the acroynm and description
        log.info("Loop through datafile and set sensor information")
        # Uses the self.sensor & self.manufacturer
        for element in self.datafile:
            if element[3] == self.sensor and element[4] == self.manufacturer:
                log.debug("Match found for Sensor and Description")
                self.sensoracroynm = element[0]
                self.sensordescription = element[1]
                
            else:
                log.warning("No match found for Sensor and Description, using defaults")
                self.sensoracroynm = "UNK"
                self.sensordescription = "Sensor Description Unknown, contact support"
                
        log.debug("Sensor: %s and Manufacturer:%s match found, loading acroynm:%s and desc:%s" 
            %(self.sensor, self.manufacturer, self.sensoracroynm, self.sensordescription))        
        
        return


### The routines below haven't been converted yet!!

    def GetEEPROMData(uuid, bustype, busnumber, sensoraddress, page):
        """
        The real routine reads a page of data from the EEPROM
        This just returns some values as a dictionary
        
        Will return 16 bytes of data
        """
        
        print("To Be Implemented")
        status = True
        return status
        
    def SetEEPROMData(uuid, bustype, busnumber, sensoraddress, page, data):
        """
        The real routine writes a page of data from the EEPROM
        This just returns some values as a dictionary
        
        Will return a status only
        """
        
        print("To Be Implemented")
        status = True
        return status
        
    def VerifyChecksum():
        """
        The real routine reads and checks the values of data against the checksum
        Will return True / False
        
        This routine always passes!
        """
        
        return True

    def SetChecksum():
        """
        The real routine calculates a new checksum and writes it to the checksum field
        Will return True if the calculation and write are successful / False if not
        
        This routine always passes!
        """
        
        return True


def selftest():
	
	return 0

if __name__ == '__main__':
	
    # setup logging
    
    import cls_comms
    
    
    selftest()

