"""

This is a template class, it is created to develop the template for the
sensors to actually be based on

When using the class as the template, the following actions are required.
- Set the Sensor Address and other defaults
- Write sensor specific functions
- Modify the following functions
    - ReadValue to call the right read_value functions
    - _setup_sensor
    - _start
    - _read_value (change to value being read, e.g. lux)
    - _stop
- Write the requried test functions


Variables in the calibration dictionary
Standard
========
low_power_mode         - For when operating in reduced power consumption mode (True = Low Power Mode)
read_frequency         - The time between reading of values, converted to seconds

Ts1 Specific
============
avg_temp_samples        - The number of samples used to calculate the TEMPERATURE readings (3 bit numbers)
avg_humd_samples        - The number of samples used to calculate the HUMIDITY readings (3 bit numbers)

"""

import logging
import time
from datetime import datetime

# This is the default configuration to be used
DEFAULT_CONFIG = [[0x00, 0x00, 0x00, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                  [0x03, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]]

SENSOR_ADDR = 0x5f
# The time between a write and subsequent read
WAITTIME = 0.5
MVDATA_TYPE = 1         #TODO: Need to change this to cater for multiple datasets
MVDATA_UNITS = 'lx'     #TODO: Need to change this to cater for multiple datasets

class iCog():
    
    def __init__(self, comms_handler, calib):
        """
        Initialise the iCog and calibration data setup
        """
        self.log = logging.getLogger()
        self.log.debug("[Ts1] cls_icog initialised")
        self.log.debug("[Ts1] Data being used to build calibration dictionary:%s" % calib)

        self.comms = comms_handler
        self.calibration_data = {}          # Reset the calibration data dictionary
        if self._decode_calib_data(calib) == False:
            # Failed to decode the configuration, prompt the user and use the defaults
            response = self._load_defaults()
            self.log.error("[Ts1] Failed to decode calibration data, using default values. Consider resetting it")
        self._setup_sensor()
        return
    
    def StartSensor(self):
        """
        Start the sensor based on the calibration data.
        In Low Power mode, do nothing
        Return the status
        """
        if self.calibration_data['low_power_mode'] == False:
            # Only start if NOT in low power mode
            status = self._start()
        else:
            status = True
        
        return status
    
    def EndReadings(self):
        """
        Stop the sensor from running
        """
        self._stop()
        return
    
    def ReadValue(self):
        """
        Return the current value from the sensor, in the correct format
        In Low Power mode start / read and end the sensor
        This should return a list of lists, each inner list is a set of values
        """
        if self.calibration_data['low_power_mode'] == True:
            # Only start if NOT in low power mode
            status = self._start()
        
        # BUG: This needs to be modified to return multiple values
        # Once changed, update Ls1
        value = self._read_value()
        timestamp = self._timestamp()
        
        if self.calibration_data['low_power_mode'] == True:
            # Only start if NOT in low power mode
            status = self._stop()
        
        mvdata = [[MVDATA_TYPE, value, MVDATA_UNITS, timestamp]]
        
        return mvdata
    
    def SetCalibration(self):
        """
        Menu to set all possible values for the calibration data
        Update the self.calibration_data dictionary
        Return the calibration array for reprogramming into the ID_IoT chip
        ** In the calling function write that data to the ID_Iot chip
        if no data is returned, no data is written
        """
        
        self._set_standard_config()

        self._set_specific_config()

        calib = self._build_calib_data()
        return calib
    
    def ResetCalibration(self):
        """
        Reset all calibration to the defaults that are contained in this file
        Get user confirmation first!
        Return this calibration data for reprogramming into the ID_IoT chip
        ** In the calling function write that data to the ID_Iot chip
        """
        
        # Use self._load_defaults to load the default calibration
        self._load_defaults()
        
        # Send the calibration data to write back to the ID_IoT
        
        return DEFAULT_CONFIG
    
    def ReturnCalibrationData(self):
        """
        Return the currently set calibration data
        returned as a dictionary
        """
        
        return self.calibration_data
    
    def ReturnReadFrequency(self):
        """
        Return the read frequency for this iCog
        returned in seconds
        """
        
        return self.calibration_data['read_frequency']

#=======================================================================
#
#    P R I V A T E   F U N C T I O N S
#
#    Not to be Called Directly from outside call
#
#=======================================================================

#-----------------------------------------------------------------------
#
#    C o n f i g u r a t i o n   F u n c t i o n s
#
#    Used to setup / read / write calibration data
#-----------------------------------------------------------------------


    def _set_standard_config(self):
        """
        Set the standard parameters for the configuration
        low_power_mode          - For when operating in reduced power consumption mode (True = Low Power Mode)
        read_frequency          - The time between reading of values, converted to seconds
        """
        print("Setting Standard Configuration Parameters")
        self.log.info("[Ts1] Setting Standard Configuration Parameters")
        choice = ""
        while choice == "":
            choice = input("Do you want the sensor to operate in Low Power Mode (y/n)")
            if choice.upper() == "Y":
                self.calibration_data['low_power_mode'] = True
            elif choice.upper() =="N":
                self.calibration_data['low_power_mode'] = False
            else:
                print("Please choose Y or N")
                choice = ""
        self.log.debug("[Ts1] Low Power Mode choice:%s" % choice)
        
        choice = 0
        while choice == 0:
            choice = input("Please enter the Read Frequency (min 0.1s, max 16416000 (19days))")
            if choice.isdigit():
                choice = int(choice)
                if choice >= 0.1 and choice <= 16416000:
                    self.calibration_data['read_frequency'] = choice
                else:
                    choice = 0
            else:
                choice = 0
        self.log.debug("[Ts1] Read Frequency choice:%s" % choice)
        
        return
        
    def _set_specific_config(self):
        """
        Set the config specific to the Ts1
        list the specific config parameters here and their valid values
        """
        self.log.info("[Ts1] User setting specific configuration")
        print("Setting Ts1 Specific Configuration Parameters\n")
        
        #TODO: Set the humidty and temperature resolution mode
        
        # Example included below - change to what is required
        print("Temperature Mode : Select the quantity of readings to be averaged")
        temp_readings = [2,4,8,16,32,64,128,256]
        choice = ""
        while choice == "":
            choice = input("Qty of readings:%s?" % temp_readings)
            if choice.isdigit():
                if int(choice) in temp_readings:
                    print("valid value:%s" % choice)
                    self.calibration_data['avg_temp_samples'] = int(choice)
                else:
                    print("Please choose a number from: %s" % temp_readings)
                    choice = ""
            else:
                print("Please enter a number from: %s" % temp_readings)
                choice = ""
        self.log.debug("[Ts1] Temperature Resolution mode choice:%s" % choice)

        print("Humidity Mode : Select the quantity of readings to be averaged")
        temp_readings = [4,8,16,32,64,128,256, 512]
        choice = ""
        while choice == "":
            choice = input("Qty of readings:%s?" % temp_readings)
            if choice.isdigit():
                if int(choice) in temp_readings:
                    print("valid value:%s" % choice)
                    self.calibration_data['avg_humd_samples'] = int(choice)
                else:
                    print("Please choose a number from: %s" % temp_readings)
                    choice = ""
            else:
                print("Please enter a number from: %s" % temp_readings)
                choice = ""
        self.log.debug("[Ts1] Humidity Resolution mode choice:%s" % choice)

        self.log.debug("[Ts1] New Configuration Parameters:%s" % self.calibration_data)
        return
    
    def _build_calib_data(self):
        """
        Take the self.calibration_data and convert it to bytes to be written
        """
        #Initially set the dataset to be the default and changed the required bytes
        data = DEFAULT_CONFIG
        
        # Configure Standard data
        data[0][0] = self.calibration_data['low_power_mode'] & 0b00000001
        data[0][1] = ((self.calibration_data['read_frequency']* 10) & 0xff0000) >> 16
        data[0][2] = ((self.calibration_data['read_frequency']* 10) & 0x00ff00) >> 8
        data[0][3] = (self.calibration_data['read_frequency']* 10) & 0x0000ff

        # Configure Sensor Specific data
        data[1][0] = self.calibration_data['avg_temp_samples'] & 0b00000111
        data[1][1] = self.calibration_data['avg_humd_samples'] & 0b00000111
        
        
        self.log.debug("[Ts1] Data bytes to be written:%s" % data)
        return data
        
    def _decode_calib_data(self, data):
        """
        Given the Calibration data, convert it into the useful dictionary of information
        The calibration data passed in is a list of 6 lists of 16 bytes of data
        """
        if len(data[0]) < 4 or len(data[1]) < 2:
            self.log.info("[Ts1] dataset is too short, using defaults. Dataset received:%s" % data)
            self.log.error("[Ts1] Failed to decode calibration data, using default values. Consider resetting it")
            data = DEFAULT_CONFIG
        
        # Standard Data values
        self.calibration_data['low_power_mode'] = (data[0][0] & 0b00000001) > 0
        self.calibration_data['read_frequency'] = ((data[0][1] << 16) + (data [0][2] << 8) + data[0][3]) / 10   #divide by 10 as in tenths
        # Unique Data values
        self.calibration_data['avg_temp_samples'] = data[1][0] & 0b00000111
        self.calibration_data['avg_humd_samples'] = data[1][1] & 0b00000111
        
        return True
    
    def _load_defaults(self):
        """
        Using the DEFAULT_CONFIG, load a new configuration data set        
        """
        if self._decode_calib_data(DEFAULT_CONFIG) == False:
            # Failed to decode the default configuration, need to abort
            self.log.critical("[Ts1] Unable to load Default Configuration")
            print("\nCRITICAL ERROR, Unable to Load Default Configuration- contact Support\n")

            #BUG: This is a poor solution, should return to the main menu with a better way out than this
            sys.exit()
        return True


#-----------------------------------------------------------------------
#
#    S e n s o r   S e t u p   F u n c t i o n s
#
#    Specific functions required for the sensor
#-----------------------------------------------------------------------

    def _xxx(self):
        """
        do something
        """
        
        #example here
        """
        Read the 2 8 bit registers that contain the ADC value
        """
        data_addr = [0x02, 0x03]
        data_l = self.comms.read_data_byte(SENSOR_ADDR,data_addr[0])
        data_h = self.comms.read_data_byte(SENSOR_ADDR,data_addr[1])
        self.log.info ("[Ls1] Data Register values (0x03/0x02):%x /%x" % (data_h, data_l))
        data_out = (data_h << 8) + data_l
        self.log.debug("[Ls1] Data Register combined %x" % data_out)
        return data_out
    
    def _turn_on_sensor(self):
        """
        Set bit 7 of the CTRL Register 0x20 to 1 and bits 1 & 0 to 0b 00
        """
        status = False
        reg_addr = 0x20
        mask = 0b10000011
        mode = 0b10000001
        byte = self.comms.read_byte_data(SENSOR_ADDR,reg_addr)
        self.log.info ("[Ts1] Control Register Before turning on Sensor (0x20):0x%x" % byte)
        if (byte & mask) != mode:
            #Modify the register to set bit7 = 1 and bits1,0 to 01
            towrite = (byte & ~mask) | mode
            self.log.debug("[Ts1] Byte to write to turn on Sensor 0x%x" % towrite)
            self.comms.write_byte_data(SENSOR_ADDR, reg_addr, towrite)
            time.sleep(WAITTIME)
            byte = self.comms.read_byte_data(SENSOR_ADDR,reg_addr)
            self.log.info ("[Ts1] Control Register After turning on sensor(0x20):0x%x" % byte)
            if (byte & mask) == mode:
                self.log.debug("[Ts1] Sensor Turned ON")
                status = True
            else:
                self.log.debug("[Ts1] Sensor Failed to turn ON")
                status = False
        else:
            self.log.debug("[Ts1] Sensor already Turned ON")
            status = True
        return status

    def _turn_off_sensor(self):
        """
        Set bit 7 of the CTRL Register 0x20 to 0 and bits 1 & 0 to 0b00
        """
        reg_addr = 0x20
        mask = 0b10000011
        mode = 0b00000000
        byte = self.comms.read_byte_data(SENSOR_ADDR,reg_addr)
        self.log.info ("[Ts1] Control Register Before turning off (0x20):%x" % byte)
        if (byte & mask) != mode:
            # Modify the register to set bit7 = 0 and bits1,0 to 00
            towrite = (byte & ~mask) | mode
            self.log.debug("[Ts1] Byte to write to turn off %s" % towrite)
            self.comms.write_byte_data(SENSOR_ADDR, reg_addr, towrite)
            time.sleep(WAITTIME)
            byte = self.comms.read_byte_data(SENSOR_ADDR,reg_addr)
            self.log.info ("[Ts1] Control Register After turning off (0x20):%x" % byte)
            if (byte & mask) == mode:
                self.log.debug("[Ts1] Sensor Turned OFF")
                status = True
            else:
                self.log.debug("[Ts1] Sensor Failed to turn OFF")
                status = False
        else:
            self.log.debug("[Ts1] Sensor already Turned OFF")
            status = True
        return status

    
#-----------------------------------------------------------------------
#
#    S t a r t / S t o p / R e a d   F u n c t i o n s
#
#    Used to perform the basic sensor functions.
#-----------------------------------------------------------------------
    
    def _setup_sensor(self):
        """
        Do all that is required to setup the sensor before starting
        Need to write the average resolution readings to the sensor
        Need to read and store the 4 calibration values for both temp and humidity
            once read, only re-read after reset
        Return either False - unsuccessful, or True if successful
        """
        
        if 'modify here' == False:
            return False
        
        return True
    
    def _start(self):
        """
        Start the sensor working, returning False if unsuccessful, or True if successful.
        Stablise the values being read
        Wait until reading available first.
        Set the active / power down mode
        """
        if self._turn_on_sensor == False:
            return False
 
        return True

    def _read_value(self):
        """
        Modify this function to return the value read from the sensor
        If no value is available, return zero or a default value
        Read both the temperature and humidity values
        Wait until data is available before reading it
        - add a timeout to this function
        """
        return value

    def _stop(self):
        """
        Stop the sensor from working
        """
        if self._turn_off_sensor == False:
            return False
 
        return True
    
#-----------------------------------------------------------------------
#
#    M i s c e l l a n e o u s    F u n c t i o n s
#
#-----------------------------------------------------------------------

    def _timestamp(self):
        """
        Generate a timestamp of the correct format
        """
        now = str(datetime.now())
        self.log.debug("[Ls1] Generated timestamp %s" % now[:23])
        return str(now[:23])


#-----------------------------------------------------------------------
#
#    T E S T   M O D U L E S
#
#-----------------------------------------------------------------------



def main():
    print("start")
    icog = iCog()
    return

if __name__ == '__main__':
    main()




