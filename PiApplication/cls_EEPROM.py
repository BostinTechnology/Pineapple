#!/usr/bin/env python3
"""
Need to add info in here.

This class extractgs and holds the information about the iCog that has been extracted from the 
datafile or the EEPROM associated with the sensor


"""

#Bus types
I2C = "I2C"
SPI = "SPI"
SERIAL = "Serial"

class EEPROM():
    """
    This class needs to hold everything extracted from the EEPROM associated to the iCog
    
    self.datafile contains the information read from the external file.
    """

    def __init__(self):
        #TODO: Read the EEPROM and process the data - could this be set globals function?
        #       Check for a tuple first - if UUID matches, use the data
        #       Create a iCOG class holding the sensor data
        #       turple the data for future use
        """
        Initialises the values and checkes if they have been previously saved as a tuple
        """
        #TODO: Not yet implemented
        #readfrequency is the time between reading of values

#BUG - This should be set higher, but is changed for testing
        self.readfrequency = 3
        log.debug("iCOG initialised, read frequency set to %s" % self.readfrequency)
        return
    
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

    def GetSensorDataFromEEPROM(self, sensor_id):
        """
        Interface with the EEPROM and get the sensor details
        Sets
            uuid, bustype, busnumber, sensoraddress, sensor, manufacturer, status
        for each sensor as a unique class object
        """
        status, reply = iCOGUtils.GetSensor(sensor_id)
        log.debug("Got sensor status and data from iCOGUtils: %s : %s" % (status, reply))
        if status:
            self.uuid = reply[0]
            self.bustype = reply[1]
            self.busnumber= reply[2]
            self.sensoraddress = reply[3]
            self.sensor = reply[4]
            self.manufacturer = reply[5]
            log.info("Loaded Sensor information")
        else:
            #TODO: Implement something here
            log.critical("Unable to Read EEPROM, program halted")
            #print ("unable to read EEPROM") removed as now log statement
            sys.exit()
        
        return 
        
    def SetAcroymnData(self):
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

    def SetupSensor(self):
        """
        Calls the hardware routine to initiate comms.
        
        uuid, bustype, busnumber, sensoraddress
        """
        log.info("Setting up hardware")
        try:
            self.setuphardware = iCOGSensorComms.SetupHardware(self.uuid, self.bustype, self.busnumber, self.sensoraddress)
            log.debug("Setup comms with the sensor: %s" % self.setuphardware)
        except:
            logging.critical("Unable to set up comms, contact support")
            sys.exit()
            
        return self.setuphardware
    



    def GetSensor(sensor_id):
        """
        The real routines reads the EERPROM and returns various values from it
        This just returns a positive response and some values as a dictionary if it is the first sensor
        else it returns False and an empty set
        
        UUID, bustype, busnumber, sensoraddress, sensor, manufacturer
        """
        
        #BUG: Logging is not working in this file.
        log = logging.getLogger(__name__)
        print("Sensor ID Requested %f" % sensor_id)
        log.info("Sensor ID")
        
        if sensor_id == 0:
            print("Sensor ID 0 chosen")
            bustype = I2C
            busnumber = 1
            sensoraddress = "Ox50"
            uuid= 0x12345678
            sensor = 12
            manufacturer = 1
            status = True
        elif sensor_id == 1:
            print("Sensor ID 1 chosen")
            bustype = I2C
            busnumber = 1
            sensoraddress = "Ox51"
            uuid= 0x00000001
            sensor = 12
            manufacturer = 1
            status = True
        elif sensor_id == 2:
            print("Sensor ID 2 chosen")
            bustype = I2C
            busnumber = 1
            sensoraddress = "Ox52"
            uuid= 0x00000002
            sensor = 12
            manufacturer = 1
            status = True
        else:
            print("Sensor ID (unknown) chosen")
            bustype = ""
            busnumber = 0
            sensoraddress = ""
            uuid= 0
            sensor = 0
            manufacturer = 0
            status= False
        
        return status, [uuid, bustype, busnumber, sensoraddress, sensor, manufacturer]

    def GetEEPROMData(uuid, bustype, busnumber, sensoraddress,page):
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

    def GetSensorCount():
        """
        the real routine determines how manyu sensors are connected somehow
        This just returns a status and fixed value
        """
        
        return True, 1


def main():
	
	return 0

if __name__ == '__main__':
	main()

