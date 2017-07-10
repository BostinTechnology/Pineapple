"""

This is a template class, it is created to develop the template for the
sensors to actually be based on



Standard variables in the calibration dictionary
low_power_mode         - For when operating in reduced power consumption mode (True = Low Power Mode)
read_frequency         - The time between reading of values, converted to seconds

"""

import logging

# This is the default configuration to be used
DEFAULT_CONFIG = [[0x20],[0x30],[0x40], [0x50], [0x60], [0x70]]

class iCog():
    
    def __init__(self, calib):
        """
        Initialise the iCog and calibration data setup
        """
        print("Into iCog")
        self.log = logging.getLogger()
        self.log.debug("[Ls1] cls_icog initialised")
        
        self.eeprom_calib_data = calib
        self.calibration_data = {}          # Reset the calibration data dictionary
        
        return
    
    def StartSensor(self):
        """
        Start the sensor based on the calibration data.
        In Low Power mode, do nothing
        """
        
        self._start()
        
        return stuff
    
    def EndReadings(self):
        """
        Stop the sensor from running
        """
        
        return
    
    def ReadValue(self):
        """
        Return the current value from the sensor
        In Low Power mode start / read and end the sensor
        """
        
        return a value
    
    def SetCalibration(self):
        """
        Menu to set all possible values for the calibration data
        Update the self.calibration_data dictionary
        Return the calibration array for reprogramming into the ID_IoT chip
        ** In the calling function write that data to the ID_Iot chip
        """
        
        return calib
    
    def ResetCalibration(self):
        """
        Reset all calibration to the defaults that are contained in this file
        Get user confirmation first!
        Return this calibration data for reprogramming into the ID_IoT chip
        ** In the calling function write that data to the ID_Iot chip
        """

        # Use self._load_defaults to load the default calibration
        
        # use something to create the calibration data to write back.
        
        return calib
    
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
        
        return waittime

#-----------------------------------------------------------------------
#
#    P R I V A T E   F U N C T I O N S
#
#-----------------------------------------------------------------------

    def _decode_calib_data(self):
        """
        Given the Calibration data, convert it into the useful dictionary of information
        """

    def _start(self):
        """
        Start the sensor working
        Stablise the values being read
        """


def main():
    print("start")
    icog = iCog()
    return

if __name__ == '__main__':
    main()




