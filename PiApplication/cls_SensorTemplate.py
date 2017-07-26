"""

This is a template class, it is created to develop the template for the
sensors to actually be based on

When using the class as the template, the following actions are required.
- Modify all log statements to be the correct sensor
- Define the default configuration
- Set the Default Configuration
- Set the Sensor Address and other defaults
- Define and setup the specific configuration
    - write _set_specific_configuration
    - modify _build_calib_data
    - modify _decode_calib_data
- Write sensor specific functions
- Modify the following functions
    - _setup_sensor
    - _start
    - _read_value
        - modify the MVDATA variables to match the data being returned
    - _stop
- Write the requried test functions


Variables in the calibration dictionary
Standard
========
low_power_mode         - For when operating in reduced power consumption mode (True = Low Power Mode)
read_frequency         - The time between reading of values, converted to seconds

XXXX Specific
=============

"""

import logging
import time
from datetime import datetime

# This is the default configuration to be used
DEFAULT_CONFIG = [[0x00, 0x00, 0x00, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                  [0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]]

SENSOR_ADDR = 0x44
# The time between a write and subsequent read
WAITTIME = 0.5
MVDATA_TYPE = [1]
MVDATA_UNITS = ['lx']

class iCog():
    
    def __init__(self, comms_handler, calib):
        """
        Initialise the iCog and calibration data setup
        """
        self.log = logging.getLogger()
        self.log.debug("[XXXX] cls_icog initialised")
        self.log.debug("[XXXX] Data being used to build calibration dictionary:%s" % calib)

        self.comms = comms_handler
        self.calibration_data = {}          # Reset the calibration data dictionary
        if self._decode_calib_data(calib) == False:
            # Failed to decode the configuration, prompt the user and use the defaults
            response = self._load_defaults()
            self.log.error("[XXXX] Failed to decode calibration data, using default values. Consider resetting it")
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
        If a value is not available, a default should be returned
        """
        if self.calibration_data['low_power_mode'] == True:
            # Only start if NOT in low power mode
            status = self._start()
            
        value = self._read_value()
        timestamp = self._timestamp()
        
        if self.calibration_data['low_power_mode'] == True:
            # Only start if NOT in low power mode
            status = self._stop()
        
        mvdata = [[MVDATA_TYPE[0], value, MVDATA_UNITS[0], timestamp]]
        
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
        self.log.info("[XXXX] Setting Standard Configuration Parameters")
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
        self.log.debug("[XXXX] Low Power Mode choice:%s" % choice)
        
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
        self.log.debug("[XXXX] Read Frequency choice:%s" % choice)
        
        return
        
    def _set_specific_config(self):
        """
        Set the config specific to the XXXX
        list the specific config parameters here and their valid values
        """
        self.log.info("[XXXX] User setting specific configuration")
        print("Setting XXXX Specific Configuration Parameters\n")
        
        # Example included below - change to what is required
        print("Light Mode")
        print("IR - Infrared Mode  -  ALS - Ambient Light Sensing Mode")
        choice = ""
        while choice == "":
            choice = input("DO you want the sensor to work in IR or ALS mode? (i/a)?")
            if choice.upper() == "A":
                self.calibration_data['light_mode'] = 1
            elif choice.upper() =="I":
                self.calibration_data['light_mode'] = 0
            else:
                print("Please choose I or A")
                choice = ""
        self.log.debug("[XXXX] IR / ALS mode choice:%s" % choice)

        self.log.debug("[XXXX] New Configuration Parameters:%s" % self.calibration_data)
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
        #example below
        data[1][0] = self.calibration_data['light_mode'] & 0b00000001
        data[1][1] = (self.calibration_data['full_scale_range'] & 0b00000011) + ((self.calibration_data['adc_resolution'] & 0b00000011) << 2)
        data[1][2] = (self.calibration_data['baro_pressure_offset'] & 0xff0000) >> 16
        data[1][3] = (self.calibration_data['baro_pressure_offset'] & 0x00ff00) >> 8
        data[1][4] = (self.calibration_data['baro_pressure_offset'] & 0x0000ff)
        
        self.log.debug("[XXXX] Data bytes to be written:%s" % data)
        return data
        
    def _decode_calib_data(self, data):
        """
        Given the Calibration data, convert it into the useful dictionary of information
        The calibration data passed in is a list of 6 lists of 16 bytes of data
        """
        if len(data[0]) < 4 or len(data[1]) < 2:
            self.log.info("[XXXX] dataset is too short, using defaults. Dataset received:%s" % data)
            self.log.error("[XXXX] Failed to decode calibration data, using default values. Consider resetting it")
            data = DEFAULT_CONFIG
        
        # Standard Data values
        self.calibration_data['low_power_mode'] = (data[0][0] & 0b00000001) > 0
        self.calibration_data['read_frequency'] = ((data[0][1] << 16) + (data [0][2] << 8) + data[0][3]) / 10   #divide by 10 as in tenths
        # Unique Data values
        # example below
        # Configure Sensor Specific data
        self.calibration_data['altimeter_mode'] = data[1][0]
        self.calibration_data['baro_pressure_offset'] = ((data[1][2] << 16) + (data [1][3] << 8) + data[1][4])
       
        return True
    
    def _load_defaults(self):
        """
        Using the DEFAULT_CONFIG, load a new configuration data set        
        """
        if self._decode_calib_data(DEFAULT_CONFIG) == False:
            # Failed to decode the default configuration, need to abort
            self.log.critical("[XXXX] Unable to load Default Configuration")
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
        
        # Example Here
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
    
#-----------------------------------------------------------------------
#
#    S t a r t / S t o p / R e a d   F u n c t i o n s
#
#    Used to perform the basic sensor functions.
#-----------------------------------------------------------------------
    
    def _setup_sensor(self):
        """
        Do all that is required to setup the sensor before starting
        Return either False - unsuccessful, or True if successful
        """
        
        if 'modify here' == False:
            return False
        
        return True
    
    def _start(self):
        """
        Start the sensor working, returning False if unsuccessful, or True if successful.
        Stablise the values being read
        """
        if 'modify here' == False:
            return False
 
        return True

    def _read_value(self):
        """
        Modify this function to return the value read from the sensor
        If no value is available, return zero or a default value
        """
        return [value]

    def _stop(self):
        """
        Set the operation mode bits (5-7) of Command Register 1 to zero
        """

        return
    
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




