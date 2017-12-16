"""

This is a template class, it is created to develop the template for the
sensors to actually be based on

When using the class as the template, the following actions are required.
- Write the requried test functions

TODO: Software reset to be added


Variables in the calibration dictionary
Standard
========
low_power_mode         - For when operating in reduced power consumption mode (True = Low Power Mode)
read_frequency         - The time between reading of values, converted to seconds

Ps3 Specific
=============
baro_pressure_offset    - The Barometric Pressure Offset for altitude readings
altimeter_mode          - When set to True, sensor to be in Altimeter mode, else barometer mode

"""

#BUG: /bin/sh: 1: cannot create /sys/module/i2c_bcm2708/parameters/combined: Directory nonexistent
#       After setting all the calibration values

import logging
import time
from datetime import datetime
import sys

# This is the default configuration to be used
DEFAULT_CONFIG = [[0x00, 0x00, 0x00, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                  [0x00, 0x01, 0x8b, 0xce, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]]

SENSOR_ADDR = 0x60
# The time between a write and subsequent read
WAITTIME = 0.5
MVDATA_TYPE = [1,1,1,1]
MVDATA_UNITS = []       # Not used as each function returns the units used as they vary depending on mode

class iCog():

    def __init__(self, comms_handler, calib):
        """
        Initialise the iCog and calibration data setup
        """
        self.log = logging.getLogger()
        self.log.debug("[Ps3] cls_icog initialised")
        self.log.debug("[Ps3] Data being used to build calibration dictionary:%s" % calib)

        self.comms = comms_handler
        self.calibration_data = {}          # Reset the calibration data dictionary
        if self._decode_calib_data(calib) == False:
            # Failed to decode the configuration, prompt the user and use the defaults
            response = self._load_defaults()
            self.log.error("[Ps3] Failed to decode calibration data, using default values. Consider resetting it")
        if self._setup_sensor() == False:
            self.log.critical("[Ps3] Failed to setup sensor for use")
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
        If a value is not available, a default should be returned
        """
        if self.calibration_data['low_power_mode'] == True:
            # Only start if NOT in low power mode
            status = self._start()

        temp = self._read_temperature()
        press = self._read_pressure()
        tempd = self._read_temperature_delta()
        pressd = self._read_pressure_delta()
        #value = self._read_value()     Not used as values returned includes units
        timestamp = self._timestamp()

        if self.calibration_data['low_power_mode'] == True:
            # Only start if NOT in low power mode
            status = self._stop()

        mvdata = [[MVDATA_TYPE[0], temp[0], temp[1], timestamp],[MVDATA_TYPE[0], press[0], press[1], timestamp],
                [MVDATA_TYPE[0], tempd[0], tempd[1], timestamp],[MVDATA_TYPE[0], pressd[0], pressd[1], timestamp]]

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

        #self._software_reset()     to be added and tested.

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

    def _is_number(self, check):
        """
        Check if the string passed into check is a number or a string
        """
        self.log.debug("[Ls1] Checking %s is a number" % check)
        try:
            float(check)
            return True
        except:
            return False

    def _set_standard_config(self):
        """
        Set the standard parameters for the configuration
        low_power_mode          - For when operating in reduced power consumption mode (True = Low Power Mode)
        read_frequency          - The time between reading of values, converted to seconds
        """
        print("Setting Standard Configuration Parameters")
        self.log.info("[Ps3] Setting Standard Configuration Parameters")
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
        self.log.debug("[Ps3] Low Power Mode choice:%s" % choice)

        choice = 0
        while choice == 0:
            choice = input("Please enter the Read Frequency (min 0.1s, max 16416000 (19days))")
            if self._is_number(choice):
                choice = float(choice)
                if choice >= 0.1 and choice <= 16416000:
                    self.calibration_data['read_frequency'] = choice
                else:
                    choice = 0
            else:
                choice = 0
        self.log.debug("[Ps3] Read Frequency choice:%s" % choice)

        return

    def _set_specific_config(self):
        """
        Set the config specific to the Ps3
        list the specific config parameters here and their valid values
        """
        self.log.info("[Ps3] User setting specific configuration")
        print("Setting Ps3 Specific Configuration Parameters\n")

        # Example included below - change to what is required
        print("Reading Mode")
        print("Barometric mode (reading absolute pressure) or Altitude mode (reading height compensated pressure")
        choice = ""
        while choice == "":
            choice = input("Do you want the sensor to work in Alitude mode? (y/n)?")
            if choice.upper() == "Y":
                self.calibration_data['altimeter_mode'] = True
            elif choice.upper() =="N":
                self.calibration_data['altimeter_mode'] = False
            else:
                print("Please choose Y or N")
                choice = ""
        self.log.debug("[Ps3] Pressure Barometic / Altitude mode choice:%s" % choice)

        print("Barometric Offset")
        print("In Altitude mode, there is an offset in Pascals (Pa) to set the current sensor altitude.")
        print("Press Enter to accept the default")
        choice = 0
        while choice == 0:
            choice = input("Please enter the Pressure offset (min 1Pa, max 1677216Pa, default is 101,326Pa)")
            if choice.isdigit():
                choice = int(choice)
                if choice >= 1 and choice <= 16416000:
                    self.calibration_data['baro_pressure_offset'] = choice
                else:
                    choice = 0
            elif choice =="":
                self.calibration_data['baro_pressure_offset'] = 101326


            else:
                choice = 0
        self.log.debug("[Ps3] Pressure Offset choice (Empty sets default):%s" % choice)

        self.log.debug("[Ps3] New Configuration Parameters:%s" % self.calibration_data)
        return

    def _build_calib_data(self):
        """
        Take the self.calibration_data and convert it to bytes to be written
        """
        #Initially set the dataset to be the default and changed the required bytes
        data = DEFAULT_CONFIG

        # Configure Standard data
        data[0][0] = self.calibration_data['low_power_mode'] & 0b00000001
        data[0][1] = (int(self.calibration_data['read_frequency']* 10) & 0xff0000) >> 16
        data[0][2] = (int(self.calibration_data['read_frequency']* 10) & 0x00ff00) >> 8
        data[0][3] = int(self.calibration_data['read_frequency']* 10) & 0x0000ff

        # Configure Sensor Specific data
        #example below
        data[1][0] = self.calibration_data['altimeter_mode'] & 0b00000001
        data[1][1] = (self.calibration_data['baro_pressure_offset'] & 0xff0000) >> 16
        data[1][2] = (self.calibration_data['baro_pressure_offset'] & 0x00ff00) >> 8
        data[1][3] = (self.calibration_data['baro_pressure_offset'] & 0x0000ff)


        self.log.debug("[Ps3] Data bytes to be written:%s" % data)
        return data

    def _decode_calib_data(self, data):
        """
        Given the Calibration data, convert it into the useful dictionary of information
        The calibration data passed in is a list of 6 lists of 16 bytes of data
        """
        if len(data[0]) < 4 or len(data[1]) < 4:
            self.log.info("[Ps3] dataset is too short, using defaults. Dataset received:%s" % data)
            self.log.error("[Ps3] Failed to decode calibration data, using default values. Consider resetting it")
            data = DEFAULT_CONFIG

        # Standard Data values
        self.calibration_data['low_power_mode'] = (data[0][0] & 0b00000001) > 0
        self.calibration_data['read_frequency'] = ((data[0][1] << 16) + (data [0][2] << 8) + data[0][3]) / 10   #divide by 10 as in tenths
        # Unique Data values

        self.calibration_data['altimeter_mode'] = data[1][0]
        self.calibration_data['baro_pressure_offset'] = ((data[1][1] << 16) + (data [1][2] << 8) + data[1][3])

        self.log.debug("[Ls1] Calibration data:%s" % self.calibration_data)

        #TODO: Need to add some calibration validation rather than just returning True
        return True

    def _load_defaults(self):
        """
        Using the DEFAULT_CONFIG, load a new configuration data set
        """
        if self._decode_calib_data(DEFAULT_CONFIG) == False:
            # Failed to decode the default configuration, need to abort
            self.log.critical("[Ps3] Unable to load Default Configuration")
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

    def _turn_on_sensor(self):
        """
        Set bit 0 of the CTRL Register 0x26 to 1 to make the sensor active
        """
        status = False
        reg_addr = 0x26
        mask = 0b00000001
        mode = 0b00000001
        byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
        self.log.info ("[Ps3] Control Register Before turning on Sensor (0x26):0x%x" % byte)
        if (byte & mask) != mode:
            #Modify the register to set bit0 = 1
            towrite = (byte & ~mask) | mode
            self.log.debug("[Ps3] Byte to write to turn on Sensor 0x%x" % towrite)
            self.comms.write_data_byte(SENSOR_ADDR, reg_addr, towrite)
            time.sleep(WAITTIME)
            byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
            self.log.info ("[Ps3] Control Register After turning on sensor(0x26):0x%x" % byte)
            if (byte & mask) == mode:
                self.log.debug("[Ps3] Sensor Turned ON")
                status = True
            else:
                self.log.debug("[Ps3] Sensor Failed to turn ON")
                status = False
        else:
            self.log.debug("[Ps3] Sensor already Turned ON")
            status = True
        return status

    def _turn_off_sensor(self):
        """
        Set bit 0 of the CTRL Register 0x26 to 0 to put the sensor in standby
        """
        reg_addr = 0x26
        mask = 0b00000001
        mode = 0b00000000
        byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
        self.log.info ("[Ps3] Control Register Before turning off (0x26):%x" % byte)
        if (byte & mask) != mode:
            # Modify the register to set bit0 = 0
            towrite = (byte & ~mask) | mode
            self.log.debug("[Ps3] Byte to write to turn off %s" % towrite)
            self.comms.write_data_byte(SENSOR_ADDR, reg_addr, towrite)
            time.sleep(WAITTIME)
            byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
            self.log.info ("[Ps3] Control Register After turning off (0x26):%x" % byte)
            if (byte & mask) == mode:
                self.log.debug("[Ps3] Sensor Turned OFF")
                status = True
            else:
                self.log.debug("[Ps3] Sensor Failed to turn OFF")
                status = False
        else:
            self.log.debug("[Ps3] Sensor already Turned OFF")
            status = True
        return status

    def _set_normal_output_mode(self):
        """
        Set the output mode in the CTRL_REG1 Register 0x26 to Normal (bit6=0)
        """
        reg_addr = 0x26
        mask = 0b01000000
        mode = 0b00000000
        byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
        self.log.info ("[Ps3] Set Output Mode (CTRL_REG1) before setting (%x): %x" % (reg_addr,byte))
        self.log.debug("[Ps3] Requested Output Mode of operation %x" % mode)
        if (byte & mask) != mode:
            # Modify the register to set bit 6 to the mode
            towrite = (byte & ~mask) | mode
            self.log.debug("[Ps3] Byte to write to turn on the requested Output Mode: %x" % towrite)
            self.comms.write_data_byte(SENSOR_ADDR, reg_addr, towrite)
            time.sleep(WAITTIME)
            byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
            self.log.info ("[Ps3] Set Output Mode (CTRL_REG1) Register After turning on the required mode: %x" % byte)
            if (byte & mask) == mode:
                self.log.info("[Ps3] Sensor Turned in to requested Output Mode: %x" % mode)
            else:
                self.log.info("[Ps3] Sensor Not in the requested Output Mode: %x" % mode)
        else:
            self.log.debug("[Ps3] Set Output Mode is already set in the required mode")
        return

    def _set_altimeter_mode(self):
        #Set the output mode in the CTRL_REG1 Register 0x26
        # mode can be either ALTIMETER = 0b10000000 or BAROMETER = 0b00000000
        if self.calibration_data['altimeter_mode'] == True:
            mode = 0b10000000
        else:
            mode = 0b00000000
        reg_addr = 0x26
        mask = 0b10000000
        byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
        self.log.info ("[Ps3] Set Altimeter - Barometer Mode (CTRL_REG1) before setting (%x): %x" % (reg_addr,byte))
        self.log.debug("[Ps3] Requested Output Mode of operation %x" % mode)
        if (byte & mask) != mode:
            # Modify the register to set bit 0 to the mode
            towrite = (byte & ~mask) | mode
            self.log.debug("[Ps3] Byte to write to turn on the requested Altimeter - Barometer Mode: %x" % towrite)
            self.comms.write_data_byte(SENSOR_ADDR, reg_addr, towrite)
            time.sleep(WAITTIME)
            byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
            self.log.info ("[Ps3] Set Altimeter - Barometer Mode (CTRL_REG1) Register After turning on the required mode: %x" % byte)
            if (byte & mask) == mode:
                self.log.info("[Ps3] Sensor Turned in to requested Altimeter - Barometer Mode: %x" % mode)
            else:
                self.log.info("[Ps3] Sensor Not in the requested Altimeter - Barometer Mode: %x" % mode)
        else:
            self.log.debug("[Ps3] Set Altimeter - Barometer Mode is already set in the required mode")
        return

    def _set_barometric_input(self):
        """
        This is used to calibrate the sensor for the difference between current altitude and sea level.
        input is the equivalent Sea level presure, in 2 Pa units
        Default value is 1 standard atmosphere (atm) is defined as 101.325 kPa
        """
        sealevel = self.calibration_data['baro_pressure_offset']

        #TODO: Convert the numbers below to variables
        if sealevel < 1 or sealevel > 110000:
            #value may not be valid
            sealevel = 101325
            self.log.debug("[Ps3] Sealevel value is invalid, using default of:%s" % sealevel)
        data_addr = [0x14, 0x15]
        # The value stored in the register is in 2 Pa units, so divide given value by 2 and remove fraction
        sealevelvalue = int(sealevel / 2)
        self.log.info("[Ps3] Requested Sea Level Value and equivalent data to write: %f / %f" % (sealevel, sealevelvalue))
        # Read out current reading first
        data_h = self.comms.read_data_byte(SENSOR_ADDR,data_addr[0])
        data_l = self.comms.read_data_byte(SENSOR_ADDR,data_addr[1])
        self.log.debug("[Ps3] Barometric Input Equivalent Sea Level current values (%x/%x):%x /%x" % (data_addr[0], data_addr[1], data_h, data_l))
        current_offset = (data_h << 8) + data_l
        self.log.info("[Ps3] Current Sea Level offset %f and requried Sea Level Offset %f" % (current_offset, sealevelvalue))
        if current_offset != sealevelvalue:
            # The value required is different to the value currently set
            towrite_h = (sealevelvalue >> 8)
            towrite_l = (sealevelvalue & 0b0000000011111111)
            # towrite_l may be 2 bytes, need to check during testing
            self.log.debug("[Ps3] New Sea Levels (high & low bytes) to Write in registers (%x, %x): %x / %x)" % (towrite_h, towrite_l, data_addr[0], data_addr[1]))
            self.comms.write_data_byte(SENSOR_ADDR, data_addr[0], towrite_h)
            time.sleep(WAITTIME)
            self.comms.write_data_byte(SENSOR_ADDR, data_addr[1], towrite_l)
            time.sleep(WAITTIME)
            byte_h = self.comms.read_data_byte(SENSOR_ADDR,data_addr[0])
            byte_l = self.comms.read_data_byte(SENSOR_ADDR,data_addr[1])
            self.log.info ("[Ps3] Set Barometric Input Equivalent Sea Level after writing the required value: %x /  %x" % (byte_h, byte_l))
            byte = (byte_h << 8) + byte_l
            if byte == sealevelvalue:
                self.log.debug("[Ps3] Barometric Input Equivalent Sea Level set to the requested value: %x" % byte)
            else:
                self.log.debug("[Ps3] Barometric Input Equivalent Sea Level NOT set to the requested value: %x" % byte)
        else:
            self.log.debug("[Ps3] Barometric Input Equivalent Sea Level is already set to the requested value")
        return

    def _read_temperature(self):
        """
        Read the data out from the Temperature Registers OUT_T_MSB and OUT_T_LSB data registers
        Register 0x04 - msb, 0x05 bits 7 - 4 - lsb
        Number is stored as Q8.4, not Q12.4 as stated in the datasheet
        """
        data_addr = [0x04, 0x05]
        data_h = self.comms.read_data_byte(SENSOR_ADDR,data_addr[0])
        data_l = self.comms.read_data_byte(SENSOR_ADDR,data_addr[1])
        self.log.debug("[Ps3] OUT_T Data Register values (0x%x/0x%x):%x /%x" % (data_addr[0], data_addr[1], data_h, data_l))
        # value is 8 its from data_h and uppper 4 bits from data_l, but for now just merge them together
        data_out = (data_h << 8) + data_l
        # output is a signed number.
        data_out = self._signed_number_16(data_out)
        # Because I merged the numbers together earlier, I now need to divide by 256 to get the right number
        data_out = data_out / 256
        self.log.info("[Ps3] OUT_T Registers combined %x" % data_out)
        return [data_out, "DegC"]

    def _read_pressure(self):
        """
        Read and return the pressure value read from the OUT_P_MSB, OUT_P_CSB and OUT_P_LSB registers
        Registers are 0x01, 0x02, 0x03
        Value read is dependent on the mode of operation
        """
        data_addr = [0x01, 0x02, 0x03]
        # units is used to return the units of the value
        units = ""
        data_h = self.comms.read_data_byte(SENSOR_ADDR,data_addr[0])
        data_c = self.comms.read_data_byte(SENSOR_ADDR,data_addr[1])
        data_l = self.comms.read_data_byte(SENSOR_ADDR,data_addr[2])
        self.log.debug("[Ps3] OUT_P Data Register values (%x/%x/%x):%x / %x / %x" % (data_addr[0], data_addr[1], data_addr[1], data_h, data_c, data_l))
        # The value in the register is dependent on the mode of operation, Altitude or barometer.
        if self.calibration_data['altimeter_mode'] == True:
            # In this mode, the data is a 20 bit signed Q16.4 format number
            # Therefore current value needs signing and dividing by 65536
            data_out = (data_h << 24) + (data_c << 16) + (data_l << 8)
            self.log.debug("[Ps3] 32 bit number retrieved from the sensor: %x" % data_out)
            data_out = self._signed_number_32(data_out)
            self.log.debug("[Ps3] Altimeter Pressure Converted using Signed Number %f" % data_out)
            data_out = data_out / 65536
            self.log.info("[Ps3] Altimeter Pressure Value being returned %f" % data_out)
            units = "M"
        else:
            # In this mode the data is in signed Q18.2
            # Therefore current value needs signing and dividing by 64
            data_out = (data_h << 16) + (data_c << 8) + data_l
            self.log.debug("[Ps3] 24 bit number retrieved from the sensor: %x" % data_out)
            # pressure is unsigned
            #data_out = SignedNumber(data_out)
            #self.log.debug("Barometer Pressure Converted using Signed Number %f" % data_out)
            data_out = data_out / 64
            self.log.info("[Ps3] Barometer Pressure Value being returned %f" % data_out)
            units = "Pa"
        return [data_out, units]

    def _read_temperature_delta(self):
        """
        Read the data out from the Temperature Delta Registers OUT_T_DELTA_MSB and OUT_T_DELTA_LSB data registers
        Register 0x0A - msb, 0x0B bits 7 - 4 - lsb
        Number is stored as Q8.4, not Q12.4 as stated in the datasheet as degress C

        Not sure if this is stored as a 2'c compliment, assumes so at the moment
        """
        data_addr = [0x0A, 0x0B]
        data_h = self.comms.read_data_byte(SENSOR_ADDR,data_addr[0])
        data_l = self.comms.read_data_byte(SENSOR_ADDR,data_addr[1])
        self.log.debug("[Ps3] OUT_T Delta Data Register values (%x/%x):%x /%x" % (data_addr[0], data_addr[1], data_h, data_l))
        # value is 8 its from data_h and uppper 4 bits from data_l, but for now just merge them together
        data_out = (data_h << 8) + data_l
        # output is a 2's compliment number.
        data_out = self._twos_compliment(data_out)
        # Because I merged the numbers together earlier, I now need to divide by 256 to get the right number
        data_out = data_out / 256
        self.log.info("[Ps3] OUT_T Delta Registers combined %x" % data_out)
        return [data_out, "DegC"]

    def _read_pressure_delta(self):
        """
        Read and return the pressure delta value read from the OUT_P_DELTA_MSB, OUT_P_DELTA_CSB and OUT_P_DELTA_LSB registers
        Registers are 0x07, 0x08, 0x09
        Value read is dependent on the mode of operation
        """
        data_addr = [0x07, 0x08, 0x09]
        # units is used to return the units of the value
        units = ""
        data_h = self.comms.read_data_byte(SENSOR_ADDR,data_addr[0])
        data_c = self.comms.read_data_byte(SENSOR_ADDR,data_addr[1])
        data_l = self.comms.read_data_byte(SENSOR_ADDR,data_addr[2])
        self.log.debug("[Ps3] OUT_P_DELTA Data Register values (%x/%x/%x):%x / %x / %x" % (data_addr[0], data_addr[1], data_addr[2], data_h, data_c, data_l))
        data_out = (data_h << 16) + (data_c << 8) + data_l
        self.log.debug("[Ps3] 24 bit number retrieved from the sensor: %x" % data_out)
        # The value in the register is dependent on the mode of operation, Altitude or barometer or raw.
        if self.calibration_data['altimeter_mode'] == True:
            # In this mode, the data is a 20 bit 2's compliment number, with 4 decimal places
            # Therefore current value needs 2'c compliment and dividing by 256 as the lowest 8 bits are fractions
            data_out = self._twos_compliment_20(data_out)
            self.log.debug("[Ps3] Altimeter Pressure Delta Converted using 2's Compliment Number %f" % data_out)
            data_out = data_out / 256
            self.log.info("[Ps3] Altimeter Pressure Delta Value being returned %f" % data_out)
            units = "M"
        else:
            # In this mode the data is a 2'c compliment number with 2 bits being fraction
            # Therefore current value needs 2's compliment and dividing by 64
            data_out = self._twos_compliment_20(data_out)
            self.log.debug("[Ps3] Barometer Pressure Delta Converted using 2's compliment Number %f" % data_out)
            data_out = data_out / 64
            self.log.info("[Ps3] Barometer Pressure Delta Value being returned %f" % data_out)
            units = "Pa"
        return [data_out, units]


    def _software_reset(self):
        """
        Perform a Software Reset using CTRL_Register 0x26
        After the software reset, it automatically clears the bit so no need to check / merge
        """
        reg_addr = 0x26
        value = 0b00000100
        byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
        self.log.info ("[Ps3] Control Register 1 before enabling Software Reset (%x):%x" % (reg_addr,byte))
        # Modify the register to set bit 2 to 0b1
        towrite = byte | value
        self.log.info("[Ps3] ABout to perform Software Reset with byte:%x" % towrite)
        self.comms.write_data_byte(SENSOR_ADDR, reg_addr, towrite)
        time.sleep(0.5)
        in_st = 1
        while in_st:
            # Wait while the Software Reset runs
            byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
            self.log.debug ("[Ps3] Control Register 1 After enabling Software Reset:%x" % byte)
            in_st = (byte & value) >> 2
            if in_st == 0b1:
                self.log.debug ("[Ps3] Sensor In Software Reset")
        self.log.info ("[Ps3] Software Reset Completed")
        return

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
        if self.comms.repeated_start() == False:
            return False

        # TODO: Ensure sensor is turned off
        # TODO: Fail if any of these fail
        self._set_normal_output_mode()
        self._set_altimeter_mode()
        self._set_barometric_input()

        return True

    def _start(self):
        """
        Start the sensor working, returning False if unsuccessful, or True if successful.
        Stablise the values being read
        """
        #TODO: remove the extra layer and put this functionality in StartReadings
        if self._turn_on_sensor() == False:
            return False

        return True

    # method below is not ussed as the data is passed straight back to ReadValue due to units being included.
    #def _read_value(self):
    #    """
    #    Modify this function to return the value read from the sensor
    #    If no value is available, return zero or a default value
    #    """
    #    # functions below return a value and units
    #    self._read_temperature()
    #    self._read_pressure()
    #    self._read_temperature_delta()
    #    self._read_pressure_delta()
    #    return [value]

    def _stop(self):
        """
        Set the operation mode to standby
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
        self.log.debug("[Ps3] Generated timestamp %s" % now[:23])
        return str(now[:23])

    def _twos_compliment(self,value):
        """
        Convert the given 16bit hex value to decimal using 2's compliment
        """
        return -(value & 0b1000000000000000) | (value & 0b0111111111111111)

    def _twos_compliment_20(self,value):
        # Convert the given 20bit hex value to decimal using 2's compliment
        return -(value & 0b10000000000000000000) | (value & 0b01111111111111111111)

    def _signed_number_16(self,value):
        # Takes the given number and return a signed version of it
        # Assumes the number is 16 bit
        sign = (value & 0b1000000000000000) >> 15
        value = value & 0b0111111111111111
        if sign == 0b1:
            # Sign bit is set, so number is negative
            value = value * -1
        return value

    def _signed_number_32(self,value):
        # Takes the given number and return a signed version of it
        # Assumes the number is 24 bit
        sign = (value & 0b10000000000000000000000000000000) >> 31
        value = value & 0b01111111111111111111111111111111
        if sign == 0b1:
            # Sign bit is set, so number is negative
            value = value * -1
        return value

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




