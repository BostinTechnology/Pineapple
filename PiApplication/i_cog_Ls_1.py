#!/usr/bin/env python3
"""

Variables in the calibration_data dictionary
Standard
========
low_power_mode          - For when operating in reduced power consumption mode (True = Low Power Mode)
read_frequency          - The time between reading of values, converted to seconds

Ls1 Specific
============
light_mode              - 0 = IR mode, 1 = Ambient Light Sensing (0 = IR mode, 1 = ALS mode)
full_scale_range        - 0 = 1,000LUX, 1 = 4000LUX, 2=16,000LUX, 3=64,000LUX
adc_resolution          - 0 = 16bit ADC, 1 = 12bit ADC, 2 = 8bit ADC, 3=4bit ADC

"""

import logging
import time

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
MVDATA_TYPE = 1
MVDATA_UNITS = 'lx'

class iCog():
    
    def __init__(self, comms_handler, calib):
        """
        Initialise the iCog and calibration data setup
        """
        self.log = logging.getLogger()
        self.log.debug("[Ls1] cls_icog initialised")
        self.log.debug("[Ls1] Data being used to build calibration dictionary:%s" % calib)

        self.comms = comms_handler
        self.calibration_data = {}          # Reset the calibration data dictionary
        if self._decode_calib_data(calib) == False:
            # Failed to decode the configuration, prompt the user and use the defaults
            response = self._load_defaults()
            log.error("[Ls1] Failed to decode calibration data, using default values. Consider resetting it")
            #TODO: Write calibration data back to the ID_IoT
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
        """
        if self.calibration_data['low_power_mode'] == True:
            # Only start if NOT in low power mode
            status = self._start()
            
        value = self._read_lux()
    #BUG: Returns a number, not in the correct json format
        
        if self.calibration_data['low_power_mode'] == True:
            # Only start if NOT in low power mode
            status = self._stop()
        
        mvdata = [MVDATA_TYPE, value, MVDATA_UNITS]
        
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

#-----------------------------------------------------------------------
#
#    P R I V A T E   F U N C T I O N S
#
#-----------------------------------------------------------------------

    def _set_standard_config(self):
        """
        Set the standard parameters for the configuration
        low_power_mode          - For when operating in reduced power consumption mode (True = Low Power Mode)
        read_frequency          - The time between reading of values, converted to seconds
        """
        print("Setting Standard Configuration Parameters")
        self.log.info("[Ls1] Setting Standard Configuration Parameters")
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
        self.log.debug("[Ls1] Low Power Mode choice:%s" % choice)
        
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
        self.log.debug("[Ls1] Read Frequency choice:%s" % choice)
        
        return
        
    def _set_specific_config(self):
        """
        Set the config specific to the Ls1
        light_mode              - 0 = IR mode, 1 = Ambient Light Sensing (0 = IR mode, 1 = ALS mode)
        full_scale_range        - 0 = 1,000LUX, 1 = 4000LUX, 2=16,000LUX, 3=64,000LUX
        adc_resolution          - 0 = 16bit ADC, 1 = 12bit ADC, 2 = 8bit ADC, 3=4bit ADC
        """
        self.log.info("[Ls1] User setting specific configuration")
        print("Setting Ls1 Specific Configuration Parameters\n")
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
        self.log.debug("[Ls1] IR / ALS mode choice:%s" % choice)

        print("Full Scale Range")
        print("0 = 1,000LUX, 1 = 4000LUX, 2=16,000LUX, 3=64,000LUX")
        choice = ""
        while choice == "":
            choice = input("Which Full Scale value is required? (0,1,2,3)?")
            if choice.isdigit():
                choice = int(choice)
                if choice >= 0 and choice <=3:
                    self.calibration_data['full_scale_range'] = choice
                else:
                    print("Please choose either 0, 1, 2 or 3")
                    choice = ""
            else:
                print("Please choose either 0, 1, 2 or 3")
                choice = ""
        self.log.debug("[Ls1] Full Scale Range choice:%s" % choice)

        print("ADC Resolution")
        print("0 = 16bit ADC, 1 = 12bit ADC, 2 = 8bit ADC, 3=4bit ADC")
        choice = ""
        while choice == "":
            choice = input("Which ADC Resolution value is required? (0,1,2,3)?")
            if choice.isdigit():
                choice = int(choice)
                if choice >= 0 and choice <=3:
                    self.calibration_data['adc_resolution'] = choice
                else:
                    print("Please choose either 0, 1, 2 or 3")
                    choice = ""
            else:
                print("Please choose either 0, 1, 2 or 3")
                choice = ""
        self.log.debug("[Ls1] ADC Resolution choice:%s" % choice)

        self.log.debug("[Ls1] New Configuration Parameters:%s" % self.calibration_data)
        return
    
    def _build_calib_data(self):
        """
        Take the self.calibration_data and convert it to bytes to be written
        """
        #Initially set the dataset to be the default and changed the required bytes
        data = DEFAULT_CONFIG
        data[0][0] = self.calibration_data['low_power_mode'] & 0b00000001
        data[0][1] = ((self.calibration_data['read_frequency']* 10) & 0xff0000) >> 16
        data[0][2] = ((self.calibration_data['read_frequency']* 10) & 0x00ff00) >> 8
        data[0][3] = (self.calibration_data['read_frequency']* 10) & 0x0000ff
        
        data[1][0] = self.calibration_data['light_mode'] & 0b00000001
        data[1][1] = (self.calibration_data['full_scale_range'] & 0b00000011) + ((self.calibration_data['adc_resolution'] & 0b00000011) << 2)
        
        
        self.log.debug("[Ls1] Data bytes to be written:%s" % data)
        return data
        
    def _decode_calib_data(self, data):
        """
        Given the Calibration data, convert it into the useful dictionary of information
        The calibration data passed in is a list of 6 lists of 16 bytes of data
        """
        #TODO: Need to check the length of the incoming data, currently assuming it is the right size
        
        #TODO: Need to validate the dictionary, what happens if the value doesn't exist?
        
        # Common Data values
        self.calibration_data['low_power_mode'] = (data[0][0] & 0b00000001) > 0
        self.calibration_data['read_frequency'] = ((data[0][1] << 16) + (data [0][2] << 8) + data[0][3]) / 10   #divide by 10 as in tenths
        # Unique Data values
        self.calibration_data['light_mode'] = data[1][0] & 0b00000001         # 0 = IR mode, 1 = ALS mode
        self.calibration_data['full_scale_range'] = data[1][1] & 0b00000011   # 0 = 1,000LUX, 1 = 4000LUX, 2=16,000LUX, 3=64,000LUX
        self.calibration_data['adc_resolution'] = (data[1][1] & 0b00001100) >> 2     # 0 = 16bit ADC, 1 = 12bit ADC, 2 = 8bit ADC, 3=4bit ADC
        
        self.log.info("[Ls1] Calibration Data:%s" % self.calibration_data)
        self.log.warning("[Ls1] _decode_calib_data doesn't validate incoming data currently")

        """
        #Test Data
        self.calibration_data['low_power_mode'] = False
        self.calibration_data['read_frequency'] = 10
        # Unique Data values
        self.calibration_data['light_mode'] = 0
        self.calibration_data['full_scale_range'] = 1
        self.calibration_data['adc_resolution'] = 0
        """
        
        return True
    
    def _load_defaults(self):
        """
        Using the DEFAULT_CONFIG, load a new configuration data set        
        """
        if self._decode_calib_data(DEFAULT_CONFIG) == False:
            # Failed to decode the default configuration, need to abort
            self.log.critical("[Ls1] Unable to load Default Configuration")
            print("\nCRITICAL ERROR, Unable to Load Default Configuration- contact Support\n")
            self.log.exception("[Ls1] ResetConfig Exception Data")

            #BUG: This is a poor solution, should return to the main menu with a better way out than this
            sys.exit()
        return True

    def _setup_sensor(self):
        """
        Taking the calibration data, write it to the sensor
        """
        
        if self._sensor_range_resolution() == False:
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
        #value = 0b1100
        # The calibration bits are already set in the correct bit numbers
        value = self.calibration_data['full_scale_range'] + (self.calibration_data['adc_resolution'] << 2)
        self.log.debug("[Ls1] Required Sensor Range byte setting:%s" % value)
        status = False
        byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
        self.log.info("[Ls1] Range Resolution Register before setting measurement ranges (0x01):%x" % byte)
        if (byte & mask) != value:
            # Modify the register to set bits 3 & 2 to 0b11, bits 1 & 0 to 0b00
            towrite = (byte & ~mask) | value
            self.log.debug("[Ls1] Byte to write to set measurement ranges %x" % towrite)
            self.comms.write_data_byte(SENSOR_ADDR, reg_addr, towrite)
            time.sleep(WAITTIME)
            byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
            self.log.info ("[Ls1] Range Resolution Register After setting measurement ranges (0x01):%x" % byte)
            if (byte & mask) == value:
                self.log.debug("[Ls1] Sensor Range Resolution Registers set")
                status = True
            else:
                self.log.debug("[Ls1] Sensor Range Resolution Registers not set")
                status = False
        else:
            self.log.debug("[Ls1] Sensor Range Resolution already set")
        return status
    
    def _read_data_registers(self):
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
    
    def _start(self):
        """
        Start the sensor working
        Stablise the values being read
        """
        if self._set_light_mode() == False:
            return False
 
        return True

    def _read_lux(self):
        # Determine the scaling factor for the full scale range
        if self.calibration_data['light_mode'] == 0:
            # In IR mode,the fsr is 65535
            fullscalerange = 65535
        else:
            # In ALS mode
            if self.calibration_data['full_scale_range'] == 0:
                # Range 1
                fullscalerange = 1000
            elif self.calibration_data['full_scale_range'] == 1:
                # Range 2
                fullscalerange = 4000
            elif self.calibration_data['full_scale_range'] == 2:
                # Range 3
                fullscalerange = 16000
            elif self.calibration_data['full_scale_range'] == 3:
                # Range 4
                fullscalerange = 64000
            else:
                # unknown range
                fullscalerange = 64000
                self.log.warning("[Ls1] full scale range undetermined, set to maximum (64000)")
        self.log.info("[Ls1] Full Scale Range:%s" % fullscalerange)
        
        # Determine the ADC Resolution
        # from calibration data: 0 = 16bit ADC, 1 = 12bit ADC, 2 = 8bit ADC, 3=4bit ADC
        
        adc_resolution = 00
        if self.calibration_data['adc_resolution'] == 0:
            # 2 ^ 16
            adc_resolution = 65536
        elif self.calibration_data['adc_resolution'] == 1:
            # 2 ^ 12
            adc_resolution = 4096
        elif self.calibration_data['adc_resolution'] == 2:
            # 2 ^ 8
            adc_resolution = 256
        elif self.calibration_data['adc_resolution'] == 3:
            # 2 ^ 4
            adc_resolution = 16
        else:
            # unknown resolution
            adc_resolution = 65536
            self.log.warning("[Ls1] ADC Resolution undetermined, set to maximum (65536)")

        self.log.info("[Ls1] ADC Resolution Setting %s" % adc_resolution)
        
        lux = 0
        
        data_read = self._read_data_registers()
        lux = (fullscalerange / adc_resolution) * data_read
        self.log.info("[Ls1] Calculated LUX value based on (full scale range / adc resolution) * data read %f" % lux)
        return lux

    def _stop(self):
        """
        Set the operation mode bits (5-7) of Command Register 1 to zero
        """
        reg_addr = 0x00
        mask = 0b11100000
        shift = 5
        mode = 0b000
        byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
        self.log.info ("[Ls1] Command Register Before turning off (0x00):%x" % byte)
        if (byte & mask) != (mode << shift):
            # Modify the register to set bits 7 to 5= 0b000
            towrite = (byte & ~mask) | (mode << shift)
            self.log.debug("[Ls1] Byte to write to turn off %s" % towrite)
            self.comms.write_data_byte(SENSOR_ADDR, reg_addr, towrite)
            time.sleep(WAITTIME)
            byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
            self.log.info ("[Ls1] Command Register After turning off (0x00):%x" % byte)
            if (byte & mask) == (mode << shift):
                self.log.debug("[Ls1] Sensor turned off")
                status = False
            else:
                self.log.debug("[Ls1] Sensor failed to turn off")
                status = True
        else:
            self.log.debug("[Ls1] Sensor already Turned off")
        return

def main():
    print("start")
    # Need to add comms handler and calib data to test with
    icog = iCog()
    return

if __name__ == '__main__':
    main()

