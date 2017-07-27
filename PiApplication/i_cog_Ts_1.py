"""

This is a template class, it is created to develop the template for the
sensors to actually be based on

When using the class as the template, the following actions are required.


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
#BUG: The Wait time for data to be available needs to be based on the various settings
#       at the moment it is set to 10 seconds that appears to work.
#BUG: when passing data to the data accessor, it is rejecting the values, even though they are floating point numbers

#TODO:- Write the requried test functions
#TODO: Implement something that also resets the sensor - there is a command for it

import logging
import time
from datetime import datetime
from datetime import timedelta
import sys

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
# The time to wait for the Humidity / Temperature data avaiable flag to be set
HUMID_DA_WAIT_TIME = 10#0.5
TEMP_DA_WAIT_TIME = 10#0.5
# The default value to be used if there is no reading available
DEFAULT_TEMP = -273
DEFAULT_HUMID = -1

# The items listed below MUST match the data structure returned from the _read_value function
MVDATA_TYPE = [1,1]
MVDATA_UNITS = ['DegC','rH']

# Conversion from numeric to binary for the sample quantity
# NOTE: The zero key is added as the default and to cater for when there is no calibration data set.
AVGT = {0:16, 2:0, 4:1, 8:2, 16:3, 32:4, 64:5, 128:6, 256:7}
AVGH = {0:32, 4:0, 8:1, 16:2, 32:3, 64:4, 128:5, 256:7, 512:8}

class iCog():
    
    def __init__(self, comms_handler, calib):
        """
        Initialise the iCog and calibration data setup
        """
        self.log = logging.getLogger()
        self.log.debug("[Ts1] cls_icog initialised")
        self.log.debug("[Ts1] Data being used to build calibration dictionary:%s" % calib)
        self.t_out = 0              # Temperature reading from the sensor
        self.h_out = 0              # Humidity reading from the sensor
        
        self.t0_degc = 0            #Calibration Data
        self.t1_degc = 0            #   -- "" --
        self.t0_out = 0             #   -- "" --
        self.t1_out = 0             #   -- "" --
        self.h0_rh = 0             #   -- "" --
        self.h1_rh = 0             #   -- "" --
        self.h0_out = 0             #   -- "" --
        self.h1_out = 0             #   -- "" --
        
        self.t_degc = 0             # Calculated output value

        self.comms = comms_handler
        self.calibration_data = {}          # Reset the calibration data dictionary
        if self._decode_calib_data(calib) == False:
            # Failed to decode the configuration, prompt the user and use the defaults
            response = self._load_defaults()
            self.log.error("[Ts1] Failed to decode calibration data, using default values. Consider resetting it")
        self.log.info("[Ts1] Calibration Data\n:%s" % self.calibration_data)
        if self._setup_sensor() == False:
            self.log.critical("[Ts2] Failed to setup sensor for use")
            print("Failed to initialise the sensor correctly, please try again and if it persists, contact support")
            sys.exit()
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
        
        mvdata = [[MVDATA_TYPE[0], value[0], MVDATA_UNITS[0], timestamp],
                    [MVDATA_TYPE[1], value[1], MVDATA_UNITS[1], timestamp]]
        
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
        
        #TODO: Consider resetting the sensor at the same time - use RefreshRegisters
        
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
        
        # Get the choices for the temperature resolution mode
        choices = []
        for item in AVGT:
            choices.append(item)
        choices.sort()
        print("Temperature Mode : Select the quantity of readings to be averaged")
        #temp_readings = [2,4,8,16,32,64,128,256]
        choice = ""
        while choice == "":
            choice = input("Qty of readings:%s?" % choices)
            if choice.isdigit():
                if int(choice) in AVGT.keys():
                    print("valid value:%s" % choice)
                    self.calibration_data['avg_temp_samples'] = int(choice)
                else:
                    print("Please choose a number from: %s" % choices)
                    choice = ""
            else:
                print("Please enter a number from: %s" % choices)
                choice = ""
        self.log.debug("[Ts1] Temperature Resolution mode choice:%s" % choice)

        # Get the choices for the humidity readings
        choices = []
        for item in AVGH:
            choices.append(item)
        choices.sort()        
        print("Humidity Mode : Select the quantity of readings to be averaged")
        #temp_readings = [4,8,16,32,64,128,256, 512]
        choice = ""
        while choice == "":
            choice = input("Qty of readings:%s?" % choices)
            if choice.isdigit():
                if int(choice) in AVGH.keys():
                    print("valid value:%s" % choice)
                    self.calibration_data['avg_humd_samples'] = int(choice)
                else:
                    print("Please choose a number from: %s" % choices)
                    choice = ""
            else:
                print("Please enter a number from: %s" % choices)
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
        data[1][0] = self.calibration_data['avg_temp_samples']      #conversion is completed when writing values to the sensor
        data[1][1] = self.calibration_data['avg_humd_samples']      #conversion is completed when writing values to the sensor
        
        
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
        self.calibration_data['avg_temp_samples'] = data[1][0]      #conversion is completed when writing values to the sensor
        self.calibration_data['avg_humd_samples'] = data[1][1]      #conversion is completed when writing values to the sensor
        
        self.log.debug("[Ls1] Calibration data:%s" % self.calibration_data)

        #TODO: Need to have some validation here or just return - no need for return True
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

    def _set_temp_samples(self):
        """
        Set bit 7 of the CTRL Register 0x20 to 1 and bits 1 & 0 to 0b 00
        """
        status = False
        reg_addr = 0x10
        mask = 0b00111000
        mode = AVGT[self.calibration_data['avg_temp_samples']] << 3
        byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
        self.log.info ("[Ts1] Temperature Samples Register Before turning on Sensor:0x%x" % byte)
        if (byte & mask) != mode:
            #Modify the register to set bits 5-3 to the mode
            towrite = (byte & ~mask) | mode
            self.log.debug("[Ts1] Byte to write to set Temperature Samples Register 0x%x" % towrite)
            self.comms.write_data_byte(SENSOR_ADDR, reg_addr, towrite)
            time.sleep(WAITTIME)
            byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
            self.log.debug ("[Ts1] Temperature Samples Register after setting:0x%x" % byte)
            if (byte & mask) == mode:
                self.log.info("[Ts1] Temperature Samples Register set")
                status = True
            else:
                self.log.info("[Ts1] Temperature Samples Register Failed to set")
                status = False
        else:
            self.log.info("[Ts1] Temperature Samples Register already set")
            status = True
        return status

    def _set_humid_samples(self):
        """
        Set bit 7 of the CTRL Register 0x20 to 1 and bits 1 & 0 to 0b 00
        """
        status = False
        reg_addr = 0x10
        mask = 0b00000111
        mode = AVGH[self.calibration_data['avg_humd_samples']]
        byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
        self.log.info ("[Ts1] Humidity Samples Register Before turning on Sensor:0x%x" % byte)
        if (byte & mask) != mode:
            #Modify the register to set bits 5-3 to the mode
            towrite = (byte & ~mask) | mode
            self.log.debug("[Ts1] Byte to write to set Humidity Samples Register 0x%x" % towrite)
            self.comms.write_data_byte(SENSOR_ADDR, reg_addr, towrite)
            time.sleep(WAITTIME)
            byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
            self.log.info ("[Ts1] Humidity Samples Register after setting:0x%x" % byte)
            if (byte & mask) == mode:
                self.log.debug("[Ts1] Humidity Samples Register set")
                status = True
            else:
                self.log.debug("[Ts1] Humidity Samples Register Failed to set")
                status = False
        else:
            self.log.debug("[Ts1] Humidity Samples Register already set")
            status = True
        return status
    
    def _turn_on_sensor(self):
        """
        Set bit 7 of the CTRL Register 0x20 to 1 and bits 1 & 0 to 0b 00
        """
        status = False
        reg_addr = 0x20
        mask = 0b10000011
        mode = 0b10000001
        byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
        self.log.info ("[Ts1] Control Register Before turning on Sensor (0x20):0x%x" % byte)
        if (byte & mask) != mode:
            #Modify the register to set bit7 = 1 and bits1,0 to 01
            towrite = (byte & ~mask) | mode
            self.log.debug("[Ts1] Byte to write to turn on Sensor 0x%x" % towrite)
            self.comms.write_data_byte(SENSOR_ADDR, reg_addr, towrite)
            time.sleep(WAITTIME)
            byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
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
        byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
        self.log.info ("[Ts1] Control Register Before turning off (0x20):%x" % byte)
        if (byte & mask) != mode:
            # Modify the register to set bit7 = 0 and bits1,0 to 00
            towrite = (byte & ~mask) | mode
            self.log.debug("[Ts1] Byte to write to turn off %s" % towrite)
            self.comms.write_data_byte(SENSOR_ADDR, reg_addr, towrite)
            time.sleep(WAITTIME)
            byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
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

    ### Routines to read the various temperature calibration data out
    def _read_t0_degc(self):
        """
        Read out and decode the 1.2 bytes of temperature calibraion reading T0
        """
        #TODO: Need to have some sort of validation here
        t0_reg_addr = [0x32, 0x35]
        t0_degc_l = self.comms.read_data_byte(SENSOR_ADDR,t0_reg_addr[0])
        t0_degc_h = self.comms.read_data_byte(SENSOR_ADDR,t0_reg_addr[1])
        self.log.debug ("[Ts1] T0 Calibration Readings (0x35/0x32):%x/%x" % (t0_degc_h, t0_degc_l))
        #Merge the values into a single reading
        #extract 2 bits from T0 high
        t0_degc_h = (t0_degc_h & 0b00000011)
        self.log.debug("[Ts1] bits 0 & 1 of T0 High:%s" % bin(t0_degc_h))
        self.t0_degc = ((t0_degc_h << 8) + t0_degc_l) / 8
        self.log.info("[Ts1] T0 Value:%s" % self.t0_degc)
        return

    def _read_t1_degc(self):
        """
        Read out and decode the 1.2 bytes of temperature calibraion reading T1
        """
        #TODO: Need to have some sort of validation here
        t1_reg_addr = [0x33, 0x35]
        t1_degc_l = self.comms.read_data_byte(SENSOR_ADDR,t1_reg_addr[0])
        t1_degc_h = self.comms.read_data_byte(SENSOR_ADDR,t1_reg_addr[1])
        self.log.debug ("[Ts1] T1 Calibration Readings (0x35/0x33):%x/%x" % (t1_degc_h, t1_degc_l))
        #Merge the values into a single reading
        #extract 2 bits from T0 high
        t1_degc_h = (t1_degc_h & 0b00001100) >> 2
        self.log.debug("[Ts1] Bits 2 & 3 of T1 High:%s" % bin(t1_degc_h))
        self.t1_degc = ((t1_degc_h << 8) + t1_degc_l) / 8
        self.log.info("[Ts1] T1 Value:%s" % self.t1_degc)
        return

    def _read_t0_out(self):
        """
        Read out and decode the 2 bytes of temperature calibration readings
        """
        #TODO: Need to have some sort of validation here
        t0_out_reg_addr = [0x3c, 0x3d]
        t0_out_l = self.comms.read_data_byte(SENSOR_ADDR,t0_out_reg_addr[0])
        t0_out_h = self.comms.read_data_byte(SENSOR_ADDR,t0_out_reg_addr[1])
        self.log.debug ("[Ts1] T0 OUT Reading (0x3c/0x3d):%x/%x" % (t0_out_h, t0_out_l))
        #Merge the values into a single reading
        t0_out = (t0_out_h << 8) + t0_out_l
        self.t0_out = self._twos_compliment(t0_out)
        self.log.info ("[Ts1] T0 OUT combined (0x3c/0x3d):%s" % self.t0_out)
        return

    def _read_t1_out(self):
        """
        Read out and decode the 2 bytes of temperature calibration readings
        """
        #TODO: Need to have some sort of validation here
        t1_out_reg_addr = [0x3e, 0x3f]
        t1_out_l = self.comms.read_data_byte(SENSOR_ADDR,t1_out_reg_addr[0])
        t1_out_h = self.comms.read_data_byte(SENSOR_ADDR,t1_out_reg_addr[1])
        self.log.debug ("[Ts1] T1_OUT Reading (0x3e/0x3f):%x/%x" % (t1_out_h, t1_out_l))
        #Merge the values into a single reading
        t1_out = (t1_out_h << 8) + t1_out_l
        self.t1_out = self._twos_compliment(t1_out)
        self.log.info ("[Ts1] T1_OUT Reading combined (0x3e/0x3f):%s" % self.t1_out)
        return

    ### Routines to read out the various humidity values
    def _read_h0_rH(self):
        """
        Read out and decode the 1 byte of humidity calibraion reading H0
        """
        reg_addr = 0x30
        h0_rh = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
        self.log.debug ("[Ts1] H0 Calibration Readings (0x30):%x" % h0_rh)
        self.h0_rh = h0_rh / 2
        self.log.info("[Ts1] H0 Value:%s" % self.h0_rh)
        return

    def _read_h1_rH(self):
        """
        Read out and decode the 1 byte of humidity calibraion reading H1
        """
        reg_addr = 0x31
        h1_rh = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
        self.log.debug ("[Ts1] H1 Calibration Readings (0x30):%x" % h1_rh)
        self.h1_rh = h1_rh / 2
        self.log.info("[Ts1] H1 Value:%s" % self.h1_rh)
        return h1_rh

    def _read_h0_out(self):
        """
        Read out and decode the 2 bytes of humidity calibration readings
        """
        h0_out_reg_addr = [0x36, 0x37]
        h0_out_l = self.comms.read_data_byte(SENSOR_ADDR,h0_out_reg_addr[0])
        h0_out_h = self.comms.read_data_byte(SENSOR_ADDR,h0_out_reg_addr[1])
        self.log.debug ("[Ts1] H0 OUT Reading (0x37/0x36):%x/%x" % (h0_out_h, h0_out_l))
        #Merge the values into a single reading
        h0_out = (h0_out_h << 8) + h0_out_l
        self.h0_out = self._twos_compliment(h0_out)
        self.log.info ("[Ts1] H0 OUT combined (0x37/0x36):%s" % self.h0_out)
        return

    def _read_h1_out(self):
        """
        Read out and decode the 2 bytes of humidity calibration readings
        """
        h0_out_reg_addr = [0x3a, 0x3b]
        h1_out_l = self.comms.read_data_byte(SENSOR_ADDR,h0_out_reg_addr[0])
        h1_out_h = self.comms.read_data_byte(SENSOR_ADDR,h0_out_reg_addr[1])
        self.log.debug ("[Ts1] H1 OUT Reading (0x3B/0x3A):%x/%x" % (h1_out_h, h1_out_l))
        #Merge the values into a single reading
        h1_out = (h1_out_h << 8) + h1_out_l
        self.h1_out = self._twos_compliment(h1_out)
        self.log.info ("[Ts1] H1 OUT combined (0x3B/0x3A):%s" % self.h1_out)
        return

    ### Routines to read the sensor values
    def _read_t_out(self):
        """
        Read out and decode the 2 bytes of temperature readings
        """
        #TODO: Need to have some sort of validation here
        t_out_addr = [0x2a, 0x2b]
        t_out_l = self.comms.read_data_byte(SENSOR_ADDR,t_out_addr[0])
        t_out_h = self.comms.read_data_byte(SENSOR_ADDR,t_out_addr[1])
        self.log.debug ("[Ts1] T_OUT Reading (0x2b/0x2a):%x/%x" % (t_out_h, t_out_l))
        #Merge the values into a single reading
        t_out = (t_out_h << 8) + t_out_l
        self.t_out = self._twos_compliment(t_out)
        self.log.info ("[Ts1] T_OUT Reading combined (0x2b/0x2a):%s" % self.t_out)
        return self.t_out

    def _read_h_out(self):
        """
        Read out and decode the 2 bytes of temperature readings
        """
        #TODO: Need to have some sort of validation here that the reading is within an acceptable range
        h_out_reg_addr = [0x28, 0x29]
        h_out_l = self.comms.read_data_byte(SENSOR_ADDR,h_out_reg_addr[0])
        h_out_h = self.comms.read_data_byte(SENSOR_ADDR,h_out_reg_addr[1])
        self.log.debug ("[Ts1] H_OUT Reading (0x28/0x29):%x/%x" % (h_out_h, h_out_l))
        #Merge the values into a single reading
        h_out = (h_out_h << 8) + h_out_l
        self.h_out = self._twos_compliment(h_out)
        self.log.info ("[Ts1] H_OUT Reading combined (0x28/0x29):%s" % self.h_out)
        return self.h_out

    ### Routines to check if there are reading available
    def _humidity_data_available(self):
        """
        Waits until the Humidity data available flag is set
        """
        reg_addr = 0x27
        mask = 0b00000010
        humid = False
        endtime = datetime.now() + timedelta(seconds=HUMID_DA_WAIT_TIME)
        self.log.info("[Ts1] Waiting for the Humidity data available flag (bit1, 0x27) to be set")
        while humid == False and datetime.now() < endtime:
            byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
            humid = (byte & mask) >> 1
        self.log.debug("[Ts1] Humidity Data Status (1=data available) %s" % humid)
        return humid

    def _temperature_data_available(self):
        """
        Waits until the Temperature data available flag is set
        """
        reg_addr = 0x27
        mask = 0b00000001
        temp = False
        #TODO: Need to modify the wait time based on the number of readings to take.
        endtime = datetime.now() + timedelta(seconds=TEMP_DA_WAIT_TIME)
        self.log.info("[Ts1] Waiting for the Temperature data available flag (bit1, 0x27) to be set")
        while temp == False and datetime.now() < endtime:
            byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
            temp = byte & mask
        self.log.debug("[Ts1] Temperature Data Status (1=data available) %s" % temp)
        return temp
    
    def _enable_one_shot_old(self):
        """
        Set the one shot bit to start a new conversion set of data
        """
        reg_addr = 0x21
        mask = 0b00000001
        mode = 0b00000001
        byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
        self.log.info ("[Ts1] One Shot Enable before activating (0x21):%x" % byte)
        if (byte & mask) != mode:
            # Modify the register to set bit0 = 1
            towrite = (byte & ~mask) | mode
            self.log.debug("[Ts1] Byte to write to enable One Shot %s" % towrite)
            self.comms.write_data_byte(SENSOR_ADDR, reg_addr, towrite)
            time.sleep(WAITTIME)
            byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
            self.log.info ("[Ts1] One Shot Enable after activating (0x21):%x" % byte)
            if (byte & mask) == mode:
                self.log.debug("[Ts1] One Shot Enableb")
                status = True
            else:
                self.log.debug("[Ts1] One Shot Enable Failed to enable")
                status = False
        else:
            self.log.debug("[Ts1] One Shot Enable already activated")
            status = True
        return status
        
    def _enable_one_shot(self):
        """
        Set the one shot bit to start a new conversion set of data
        """
        reg_addr = 0x21
        mask = 0b00000001
        mode = 0b00000001
        byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
        self.log.info ("[Ts1] One Shot Enable before activating (0x21):%x" % byte)
        towrite = (byte & ~mask) | mode
        self.log.debug("[Ts1] Byte to write to enable One Shot %x" % towrite)
        self.comms.write_data_byte(SENSOR_ADDR, reg_addr, towrite)
        byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
        self.log.info ("[Ts1] One Shot Enable after activating (0x21):%x" % byte)
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
        Writes the average resolution readings to the sensor (set_?????_samples)

        Need to read and store the 4 calibration values for both temp and humidity
            once read, only re-read after reset
        Return either False - unsuccessful, or True if successful
        """
        # TODO: Do I need to set the sensor off first?
        if self._set_humid_samples() == False:
            return False

        if self._set_temp_samples() == False:
            return False
        
        self._read_h0_out()
        self._read_h0_rH()
        self._read_h1_out()
        self._read_h1_rH()
        
        self._read_t0_degc()
        self._read_t0_out()
        self._read_t1_degc()
        self._read_t1_out()
        
        return True
    
    def _start(self):
        """
        Start the sensor working, returning False if unsuccessful, or True if successful.
        Stablise the values being read
        Wait until reading available first.
        Set the active / power down mode
        """
        #TODO: remove the extra layer and put this functionality in StartReadings

        if self._turn_on_sensor() == False:
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
        #TODO: check there is a temperature value available
        # Calculate the temperature
        #TODO: Need to check the values are set before using them, else get them again
        #    self.t0_degc, self.t1_degc, self.t0_out, self.t1_out
        
        if self._enable_one_shot() == False:
            return [0,0]

        if self._temperature_data_available():
            t_out = self._read_t_out()
            self.log.debug("[Ts1] Temperature Reading from Sensor (T OUT):%s" % t_out)
            self.t_degc = (self.t0_degc + (t_out - self.t0_out) * (self.t1_degc - self.t0_degc) / (self.t1_out - self.t0_out))
            self.log.info("[Ts1] Calculated Temperature: %s" % self.t_degc)
        else:
            self.log.info("[Ts1] Temperature Reading not available, using default")
            self.t_degc = DEFAULT_TEMP
            
        #TODO: Need to check these values are valid before using them, else get them again
        #   self.h0_rh, self.h1_rh, self.h0_out, self.h1_out
        if self._humidity_data_available():
            h_out = self._read_h_out()
            self.log.debug("[Ts1] Humidity Reading from Sensor (H OUT):%s" % h_out)
            self.h_rh = (self.h0_rh + (h_out - self.h0_out) * (self.h1_rh - self.h0_rh) / (self.h1_out - self.h0_out))
            self.log.info("[Ts1] Calculated Relative Humidity: %s" % self.h_rh)
        else:
            self.log.info("[Ts1] Humidity Reading not available, using default")
            self.h_rh = DEFAULT_HUMID
            
        return [self.t_degc, self.h_rh]

    def _stop(self):
        """
        Stop the sensor from working
        """
        #TODO: Remove the extra step and put the turn off sensor functionality here and move this bit to EndReadings
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

    def _twos_compliment(self,value):
        """
        Convert the given 16bit hex value to decimal using 2's compliment
        """
        return -(value & 0b1000000000000000) | (value & 0b0111111111111111)



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




