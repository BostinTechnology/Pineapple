#!/usr/bin/env python3
"""

Variables in the calibration_data dictionary
Standard
========
low_power_mode         - For when operating in reduced power consumption mode (True = Low Power Mode)
read_frequency         - The time between reading of values, converted to seconds

Ls1 Specific
============
light_mode              - 0 = IR mode, 1 = Ambient Light Sensing (0 = IR mode, 1 = ALS mode)

"""

import logging
import time

# This is the default configuration to be used
DEFAULT_CONFIG = [[common data],[unique data],[0x40], [0x50], [0x60], [0x70]]

SENSOR_ADDR = 0x44
# The time between a write and subsequent read
WAITTIME = 0.5

class iCog():
    
    def __init__(self, comms_handler, calib):
        """
        Initialise the iCog and calibration data setup
        """
        self.log = logging.getLogger()
        self.log.debug("[Ls1] cls_icog initialised")
        
        self.comms = comms_handler
        self.calibration_data = {}          # Reset the calibration data dictionary
        if self._decode_calib_data(calib) == False:
            # Failed to decode the configuration, prompt the user and use the defaults
            response = self.ResetConfig()
            log.error("[Ls1] Failed to decode calibration data, using default values. Consider resetting it")
        
        self._setup_sensor()
        return
    
    def StartSensor(self):
        """
        Start the sensor based on the calibration data.
        In Low Power mode, do nothing
        Return the status
        """
        if self.calibration)_data{'low_power_mode'} == False:
            # Only start if NOT in low power mode
            status = self._start()
        else:
            status = True
        
        return status
    
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
    
    def SetConfig(self):
        """
        Menu to set all possible values for the calibration data
        Update the self.calibration_data dictionary
        Return the calibration array for reprogramming into the ID_IoT chip
        ** In the calling function write that data to the ID_Iot chip
        """
        
        return calib
    
    def ResetConfig(self):
        """
        Reset all calibration to the defaults that are contained in this file
        Get user confirmation first!
        Return this calibration data for reprogramming into the ID_IoT chip
        ** In the calling function write that data to the ID_Iot chip
        """
        
        return calib
    
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

    def _decode_calib_data(self, data):
        """
        Given the Calibration data, convert it into the useful dictionary of information
        The calibration data passed in is a list of 6 lists of 16 bytes of data
        """
        #TODO: Need to check the length of the incoming data, currently assuming it is the right size
        # Common Data values
        self.calibration_data['low_power_mode'] = (data[0][0] & 0b00000001) > 0
        self.calibration_data['read_frequency'] = (data[0][1] << 16) + (data [0][2] << 8) + (data[0][3]) / 10   #divide by 10 as in tenths
        # Unique Data values
        self.calibration_data['light_mode'] = data[1][0] & 0b00000001       # 0 = IR mode, 1 = ALS mode
        
        return True / False
    
    def _setup_sensor(self):
        """
        Taking the calibration data, write it to the sensor
        """
        
        if self._sensor_range_resolution() == False:
            return False
        
        if self._set_light_mode() == False:
            return False
        
        return True
    
    def _set_light_mode(self):
        """
        Set bits 5-7 of the Command Register 0x00 to 0b101
        Sensor will be in ALS mode or IR mode
        """
        status = False
        reg_addr = 0x00
        mask = 0b11100000
        shift = 5
        if self.calibration_data['light_mode'] == 1:
            mode = 0b101
        else:
            mode = 0b110
            
        byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
        self.log.debug ("[Ls1] Command Register Before turning on light mode (0x00):%x" % byte)
        if (byte & mask) != (mode << shift):
            # Modify the register to set bits 7 to 5 = 0b101
            towrite = (byte & ~mask) | (mode << shift)
            self.log.debug("[Ls1] Byte to write to turn on ALS mode %x" % towrite)
            self.comms.write_data_byte(SENSOR_ADDR, reg_addr, towrite)
            time.sleep(WAITTIME)
            byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
            self.log.debug ("[Ls1] Command Register After turning on light mode (0x00):%x" % byte)
            if (byte & mask) == (mode << shift):
                self.log.debug("[Ls1] Sensor turned into correct light mode")
                status = True
            else:
                self.log.debug("[Ls1] Sensor failed to turn into correct light mode")
                status = False
        else:
            self.log.debug("[Ls1] Sensor already in the correct light mode")
            status = True
        return status
    
    def _sensor_range_resolution(self):
        # sets the various command register 2 bits for reading values
        reg_addr = 0x01
        mask = 0b00001111
        value = 0b1100
        
        
        HERE - this is to be converted
        
        HERE - value needs to be based on calibration data.
        HERE - Set Sensor Range, 2 values Full Scale Range and ADC Resolution
                
                
        byte = bus.read_byte_data(SENSOR_ADDR,reg_addr)
        logging.info ("Range Resolution Register before setting measurement ranges (0x01):%x" % byte)
        if (byte & mask) != value:
            # Modify the register to set bits 3 & 2 to 0b11, bits 1 & 0 to 0b00
            towrite = (byte & ~mask) | value
            logging.debug("Byte to write to set measurement ranges %x" % towrite)
            bus.write_byte_data(SENSOR_ADDR, reg_addr, towrite)
            time.sleep(WAITTIME)
            byte = bus.read_byte_data(SENSOR_ADDR,reg_addr)
            logging.info ("Range Resolution Register After setting measurement ranges (0x01):%x" % byte)
            if (byte & mask) == value:
                print("Sensor Range ResolutionRegisters sets")
            else:
                print("Sensor Range ResolutionRegisters not set")
        else:
            logging.debug("Sensor Range Resolution alreay set")
        return true / false
    
    def _start(self):
        """
        Start the sensor working
        Stablise the values being read
        """
        
        
        return True

def main():
    print("start")
    icog = iCog()
    return

if __name__ == '__main__':
    main()

