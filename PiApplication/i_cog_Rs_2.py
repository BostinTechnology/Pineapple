"""

This is a template class, it is created to develop the template for the
sensors to actually be based on

When using the class as the template, the following actions are required.
- Write sensor specific functions
    - self test - not sure how I can use this, maybe as part of reset calibration?

- Write the requried test functions


Variables in the calibration dictionary
Standard
========
low_power_mode         - For when operating in reduced power consumption mode (True = Low Power Mode)
read_frequency         - The time between reading of values, converted to seconds

Rs2 Specific
=============
full_scale_range        - Set the maximum to be eiher 2g, 4g or 8g
single_mode             - Run in single (when set to True) or average mode.
average_quantity        - How many readings to take to get an average
zero_g_x_offset         - The offset value to be stored to realign the sensor after mounting
zero_g_y_offset         - ditto
zero_g_z_offset         - ditto
"""

#BUG: I have no confidence that the 2's compliment routines work correctly

#BUG: There are a number of bits in the offset routines that are uncertain and may not work for other
#       values, e.g. averaging numbers as hex when they are 2's c numbers.
#       Consider changing this to use converted numbers instead, but that requires the writing routine
#       to convert the offsets back to 2's c.


import logging
import time
from datetime import datetime
from datetime import timedelta
import sys

# This is the default configuration to be used
DEFAULT_CONFIG = [[0x00, 0x00, 0x00, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                  [0x01, 0x0A, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]]

SENSOR_ADDR = 0x1d
# The time between a write and subsequent read
WAITTIME = 0.5
MVDATA_TYPE = [1,1,1]
MVDATA_UNITS = ['g x-axis','g y-axis','g z-axis']

#Average Quantity of readings values
AVG_QTY_MAX = 250           # The maximum permissible quantity of readings
AVG_QTY_MIN = 1             # The minimum permissable quantity of readings
AVG_QTY_DEFAULT = 10        # The default value if one is not available

# The time to wait for the data avaiable flag to be set
DATA_WAIT_TIME = 10

# The force applied to teh sensoe by gravity, 1.00 in 12bit hex
GRAVITY = 0x200

class iCog():

    def __init__(self, comms_handler, calib):
        """
        Initialise the iCog and calibration data setup
        """
        self.log = logging.getLogger()
        self.log.debug("[Rs2] cls_icog initialised")
        self.log.debug("[Rs2] Data being used to build calibration dictionary:%s" % calib)

        self.comms = comms_handler
        self.calibration_data = {}          # Reset the calibration data dictionary
        if self._decode_calib_data(calib) == False:
            # Failed to decode the configuration, prompt the user and use the defaults
            response = self._load_defaults()
            self.log.error("[Rs2] Failed to decode calibration data, using default values. Consider resetting it")
        if self._setup_sensor() == False:
            self.log.critical("[Rs2] Failed to setup sensor for use")
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

        value = self._read_value()
        timestamp = self._timestamp()

        if self.calibration_data['low_power_mode'] == True:
            # Only start if NOT in low power mode
            status = self._stop()

        mvdata = [[MVDATA_TYPE[0], value[0], MVDATA_UNITS[0], timestamp],
                    [MVDATA_TYPE[1], value[1], MVDATA_UNITS[1], timestamp],
                    [MVDATA_TYPE[2], value[2], MVDATA_UNITS[2], timestamp]
                    ]

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

        self._software_reset()
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
        self.log.info("[Rs2] Setting Standard Configuration Parameters")
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
        self.log.debug("[Rs2] Low Power Mode choice:%s" % choice)

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
        self.log.debug("[Rs2] Read Frequency choice:%s" % choice)

        return

    def _set_specific_config(self):
        """
        Set the config specific to the Rs2
        list the specific config parameters here and their valid values

        """
        self.log.info("[Rs2] User setting specific configuration")
        print("Setting Rs2 Specific Configuration Parameters\n")

        print("Reading Mode")
        print("Single Mode - 1 reading is taken or Averaged Mode - multiple readings are taken and averaged")
        choice = ""
        while choice == "":
            choice = input("Do you want the sensor to work in Single or Averaged mode? (s/a)?")
            if choice.upper() == "A":
                self.calibration_data['single_mode'] = False
            elif choice.upper() =="S":
                self.calibration_data['single_mode'] = True
            else:
                print("Please choose S or A")
                choice = ""
        self.log.debug("[Rs2] Single / Average mode choice:%s" % choice)

        print("Full Scale Deflection Mode")
        print("Values can be 2g, 4g or 8g with corresponding resolutions of 0.98mg, 1.96mg or 3.9mg")
        choice = ""
        while choice == "":
            choice = input("Enter a Full Scale Range to be used (2/4/8)?")
            if choice.upper() in ["2","4","8"]:
                self.calibration_data['full_scale_range'] = int(choice)
            else:
                print("Please choose either 2, 4 or 8")
                choice = ""
        self.log.debug("[Rs2] Full Scale Range choice:%s" % choice)

        if self.calibration_data['single_mode'] == False:
            print("Quantity of Reading to be Averaged")
            print("The number of readings to be taken for the average")
            choice = ""
            while choice == "":
                choice = input("Enter the quantity of readings to be used (1 - 250)?")
                if choice.isdigit():
                    choice = int(choice)
                    if choice < AVG_QTY_MIN or choice > AVG_QTY_MAX:
                        choice = ""
                        print("Please choosse a number in the range of 1 to 250")
                    else:
                        self.calibration_data['average_quantity'] = choice
                else:
                    print("Please choosse a number in the range of 1 to 250")
                    choice = ""
            self.log.debug("[Rs2] Average Quantity of Readings choice:%s" % choice)
        else:
            self.calibration_data['average_quantity'] = AVG_QTY_DEFAULT
            self.log.debug("[Rs2] Average Quantity of Readings set to default as operating in single mode")

        print("Zero Offset Setting")
        print("Set the x, y and z axis offsets to ensure the current readings are zero")
        choice = ""
        while choice == "":
            choice = input("Do you want to set the zero offsets? (y/n)?")
            if choice.upper() == "Y":
                print("Please ensure the sensor is in the correct location / orientation")
                ready = ""
                while ready == "":
                    ready = input("press 'y' to set offsets or 'a' to abort (y/a)?")
                    if choice.upper() == "Y":
                        print("Performing offset reset")
                        self._zero_g_readings()
                    elif choice.upper() == "A":
                        print("Current offsets will be used")
                    else:
                        print("Please choose Y or A")
                        ready = ""
                self.log.debug("[Rs2] Ready to set offsets choice:%s" % ready)
            elif choice.upper() =="N":
                print("Current offsets will be used")
            else:
                print("Please choose y or n")
                choice = ""
        self.log.debug("[Rs2] Setting x,y and z offsets choice:%s" % choice)

        self.log.debug("[Rs2] New Configuration Parameters:%s" % self.calibration_data)
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
        data[1][0] = self.calibration_data['single_mode'] & 0b00000001
        data[1][1] = self.calibration_data['average_quantity']
        data[1][2] = self.calibration_data['full_scale_range']
        data[1][3] = self.calibration_data['zero_g_x_offset']
        data[1][4] = self.calibration_data['zero_g_y_offset']
        data[1][5] = self.calibration_data['zero_g_z_offset']


        self.log.debug("[Rs2] Data bytes to be written:%s" % data)
        return data

    def _decode_calib_data(self, data):
        """
        Given the Calibration data, convert it into the useful dictionary of information
        The calibration data passed in is a list of 6 lists of 16 bytes of data
        """
        if len(data[0]) < 4 or len(data[1]) < 6:
            self.log.info("[Rs2] dataset is too short, using defaults. Dataset received:%s" % data)
            self.log.error("[Rs2] Failed to decode calibration data, using default values. Consider resetting it")
            data = DEFAULT_CONFIG

        # Standard Data values
        self.calibration_data['low_power_mode'] = (data[0][0] & 0b00000001) > 0
        self.calibration_data['read_frequency'] = ((data[0][1] << 16) + (data [0][2] << 8) + data[0][3]) / 10   #divide by 10 as in tenths
        # Unique Data values
        # example below
        # Configure Sensor Specific data
        self.calibration_data['single_mode'] = data[1][0] & 0b00000001
        self.calibration_data['average_quantity'] = data[1][1]
        self.calibration_data['full_scale_range'] = data[1][2]
        self.calibration_data['zero_g_x_offset'] = data[1][3]
        self.calibration_data['zero_g_y_offset'] = data[1][4]
        self.calibration_data['zero_g_z_offset'] = data[1][5]

        self.log.debug("[Ls1] Calibration data:%s" % self.calibration_data)

        return True

    def _load_defaults(self):
        """
        Using the DEFAULT_CONFIG, load a new configuration data set
        """
        if self._decode_calib_data(DEFAULT_CONFIG) == False:
            # Failed to decode the default configuration, need to abort
            self.log.critical("[Rs2] Unable to load Default Configuration")
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
        reg_addr = 0x2A
        mask = 0b00000001
        mode = 0b00000001
        byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
        self.log.info ("[Rs2] Control Register Before turning on Sensor (0x2A):0x%x" % byte)
        if (byte & mask) != mode:
            #Modify the register to set bit0 = 1
            towrite = (byte & ~mask) | mode
            self.log.debug("[Rs2] Byte to write to turn on Sensor 0x%x" % towrite)
            self.comms.write_data_byte(SENSOR_ADDR, reg_addr, towrite)
            time.sleep(WAITTIME)
            byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
            self.log.info ("[Rs2] Control Register After turning on sensor(0x2A):0x%x" % byte)
            if (byte & mask) == mode:
                self.log.debug("[Rs2] Sensor Turned ON")
                status = True
            else:
                self.log.debug("[Rs2] Sensor Failed to turn ON")
                status = False
        else:
            self.log.debug("[Rs2] Sensor already Turned ON")
            status = True
        return status

    def _turn_off_sensor(self):
        """
        Set bit 0 of the CTRL Register 0x26 to 0 to put the sensor in standby
        """
        reg_addr = 0x2A
        mask = 0b00000001
        mode = 0b00000000
        byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
        self.log.info ("[Rs2] Control Register Before turning off (0x2A):%x" % byte)
        if (byte & mask) != mode:
            # Modify the register to set bit0 = 0
            towrite = (byte & ~mask) | mode
            self.log.debug("[Rs2] Byte to write to turn off %s" % towrite)
            self.comms.write_data_byte(SENSOR_ADDR, reg_addr, towrite)
            time.sleep(WAITTIME)
            byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
            self.log.info ("[Rs2] Control Register After turning off (0x2A):%x" % byte)
            if (byte & mask) == mode:
                self.log.debug("[Rs2] Sensor Turned OFF")
                status = True
            else:
                self.log.debug("[Rs2] Sensor Failed to turn OFF")
                status = False
        else:
            self.log.debug("[Rs2] Sensor already Turned OFF")
            status = True
        return status

    def _data_available(self, axis='a'):
        """
        Waits until the data available flag is set
        """
        reg_addr = 0x00
        if axis.upper() not in ['X','Y','Z']:
            # Set a default to be all axis'
            axis = 'a'
        if axis.upper() == 'X':
            mask = 0b00000001
        elif axis.upper() == 'Y':
            mask = 0b00000010
        elif axis.upper() == 'Z':
            mask = 0b00000100
        else:
            mask = 0b00001000
        available = False
        #TODO: Need to modify the wait time based on the number of readings to take.
        endtime = datetime.now() + timedelta(seconds=DATA_WAIT_TIME)
        self.log.info("[Rs2] Waiting for the data available flag to be set for axis %s" % axis)
        while available == False and datetime.now() < endtime:
            byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
            available = byte & mask
        self.log.debug("[Rs2] Data Status (1=data available) set for axis %s : %s" % (axis,available))
        return available

    def _set_full_scale_mode(self, override=0):
        """
        Set the Full Scale Mode in the XYZ_DATA_CFG Register 0x0E
        mode can be either 2g (0b00), 4g (0b01) or 8g (0b10)
        override allows a specific value to be set, ignoring the calibration _data - used in setup
        """
        reg_addr = 0x0e
        mask = 0b00000011
        if override in [2,4,8]:
            if override == 2:
                mode = 0b00
            elif override == 4:
                mode = 0b01
            elif override == 8:
                mode = 0b10
        else:
            if self.calibration_data['full_scale_range'] == 2:
                mode = 0b00
            elif self.calibration_data['full_scale_range'] == 4:
                mode = 0b01
            elif self.calibration_data['full_scale_range'] == 8:
                mode = 0b10
            else:
                self.log.warning("[Rs2] Unable to determine full scale range, using 8g")
                mode = 0b10
        byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
        self.log.debug("[Rs2] XYZ_DATA_CFG Register before setting Full Scale Mode(%x):%x" % (reg_addr,byte))
        self.log.info("[Rs2] Requested Full Scale mode of operation %x" % mode)
        # check if the bits are not already set
        if (byte & mask) != mode:
            # Modify the register to set bits 1 - 0 to the mode
            towrite = (byte & ~mask) | mode
            self.log.debug("[Rs2] Byte to write to turn on the Full Scale mode %x" % towrite)
            self.comms.write_data_byte(SENSOR_ADDR, reg_addr, towrite)
            time.sleep(WAITTIME)
            byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
            self.log.info ("[Rs2] XYZ_DATA_CFG Register After turning on the Full Scale mode:%x" % byte)
            if (byte & mask) == mode:
                self.log.info("[Rs2] Sensor Turned in to Full Scale mode")
            else:
                self.log.info("[Rs2] Sensor Not in the Full Scale mode")
        else:
            self.log.info("[Rs2] Sensor already in required Full Scale mode")
        return

    def _set_power_mode(self):
        """
        The sensor can run in normal or low power mode
        For the power mode set the following bits of CTRL_REG2 register (0x2B).
                            Low         Normal      Mask
        Sleep Mode          0b11        0b00        0b00011000
        Auto Sleep Flag     0b1         0b0         0b00000100
        Active Mode         0b11        0b00        0b00000011

        Therefore:
        - Low Power Mode    0b00011111
        - Normal Mode       0b00000000
        """
        reg_addr = 0x2b
        mask = 0b00011111
        shift = 7
        if self.calibration_data['low_power_mode'] == True:
            mode = 0b00011111
        else:
            mode = 0b00000000
        byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
        self.log.info ("[Rs2] Power Mode bytes before setting power mode (%x):%x" % (reg_addr,byte))
        if (byte & mask) != mode:
            # Modify the register to set bits 4 - 0 to the required mode
            towrite = (byte & ~mask) | mode
            self.log.debug("[Rs2] Power Mode bytes to write to turn on the the required power mode %x" % towrite)
            self.comms.write_data_byte(SENSOR_ADDR, reg_addr, towrite)
            time.sleep(WAITTIME)
            byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
            self.log.info ("[Rs2] Power Mode bytes after turning on the required power mode:%x" % byte)
            if (byte & mask) == mode:
                self.log.info("[Rs2] Sensor Turned in to required power mode")
            else:
                self.log.info("[Rs2] Sensor Not in the required power mode")
        else:
            self.log.info("[Rs2] Sensor already in required power mode")
        return

    def _set_fifo_disabled(self):
        """
        The sensor can run in FIFO mode where the buffer contains upto 32 readings.
        For our initial setup, this is disabled
        """
        reg_addr = 0x09
        mask = 0b11000000
        mode = 0b00000000
        byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
        self.log.info ("[Rs2] FIFO Mode before disabling (%x):%x" % (reg_addr,byte))
        if (byte & mask) != mode:
            # Modify the register to set bits 4 - 0 to the required mode
            towrite = (byte & ~mask) | mode
            self.log.debug("[Rs2] FIFO Mode bytes to write to disable FIFO %x" % towrite)
            self.comms.write_data_byte(SENSOR_ADDR, reg_addr, towrite)
            time.sleep(WAITTIME)
            byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
            self.log.info ("[Rs2] FIFO Mode bytes after disabling FIFO:%x" % byte)
            if (byte & mask) == mode:
                self.log.info("[Rs2] FIFO mode disabled")
            else:
                self.log.info("[Rs2] FIFO mode Not idisabled")
        else:
            self.log.info("[Rs2] Sensor already in FIFO mode")
        return

    def _zero_g_readings(self):
        """
        Method reads the current offset values and then converts them to the offsets
        and to the calibration_data
        The routine assumes the sensor has already been located correctly.
        """
        self.log.info("[Rs2] Generating the zero g offset values")
        # Read current values
        self._turn_off_sensor()
        self._set_full_scale_mode(4)
        self._turn_on_sensor()
        x_avg = 0
        y_avg = 0
        z_avg = 0

        #BUG: I'm not sure this method of creating an averge of 10 will work as I am not confident that
        #       python will treat these as 2's compliment numbers

        for n in range(0,10):
            x_reading = self._read_x_axis_data_registers()
            x_avg = x_avg + x_reading
            y_reading = self._read_y_axis_data_registers()
            y_avg = y_avg + y_reading
            z_reading = self._read_z_axis_data_registers()
            z_avg = z_avg + z_reading
            print("Readings (x/y/z): %x / %x / %x" % (x_reading, y_reading, z_reading))
        self._turn_off_sensor()

        x_out = int(x_avg / 10)
        y_out = int(y_avg / 10)
        z_out = int(z_avg / 10)

        self.log.debug("[Rs2] Readings taken from the sensor (x:y:z) : %x:%x:%x" % (x_avg,y_avg,z_avg))

        # TODO: Need to work out which axis has gravity applied to it, so one of the axis' will have approximately
        # +/- 1g applied. Currently assumes it is the z axis

        self.log.debug("[Rs2] 8 bit value to be used to calculate the offset (x,y,z):%x : %x : %x" % (x_out,y_out, z_out))

        # For each axis determine if the MSB == 1. If so, the offset is 0b1000 0000 0000 (0x800) minus that value
        #   If not, it is the negative (2's compliment) of the value.
        if (x_out & 0b100000000000) > 0:
            # offset needs to be the positive equivalent
            x_offset = 0x800 - x_out
        else:
            x_offset = (~x_out) + 1

        if (y_out & 0b100000000000) > 0:
            # offset needs to be the positive equivalent
            y_offset = 0x800 - y_out
        else:
            y_offset = (~y_out) + 1
        # The z axis returns 1 g as its default position, which is 0x200, reduce it by 0x200 to find the offset

        #BUG: This won't work either as if the number is less than 0x200, it will be reduced further

        z_out = z_out - GRAVITY

        if (z_out & 0b100000000000) > 0:
            # offset needs to be the positive equivalent
            z_offset = 0x800 - z_out
        else:
            z_offset = (~z_out) + 1

        # The value stored is the value received,
        self.calibration_data['zero_g_x_offset'] = x_offset
        self.calibration_data['zero_g_y_offset'] = y_offset
        self.calibration_data['zero_g_z_offset'] = z_offset
        return

    def _set_offset_registers(self):
        """
        Routine to write the offset values from calibration_data to the sensor
        ideally, the x and y should be reading zero, the z = 1g
        """
        self.log.info("[Rs2] Setting the offset registers")
        reg_addr = [0x2f, 0x30, 0x31]
        setting = [self.calibration_data['zero_g_x_offset'],
                    self.calibration_data['zero_g_y_offset'],
                    self.calibration_data['zero_g_z_offset']]

        #TODO: Check the calibration values being used, if they are greater than 250mg, use 250mg.

        # Calibration data is storing the values to be written.
        register = ["x","y","z"]
        for i in range(0,len(reg_addr)):
            byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr[i])
            self.log.info ("[Rs2] Offset Register %s  before setting the required offset (%x):%x" % (register[i],reg_addr[i],byte))
            if byte != setting[i]:
                self.log.debug("[Rs2] Offset Register %s required to be updated with %x" % (register[i],setting[i]))
                self.comms.write_data_byte(SENSOR_ADDR, reg_addr[i], setting[i])
                time.sleep(WAITTIME)
                byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr[i])
                self.log.info ("[Rs2] Offset Register %s after setting the required offset:%x" % (register[i],byte))
                if byte  == setting[i]:
                    self.log.info("[Rs2] Offset Register %s set to the required offset" % register[i])
                else:
                    self.log.info("[Rs2] Offset Register %s NOT turned to the required offset" % register[i])
            else:
                self.log.info("[Rs2] Offset Register %s already set to the required offset" % register[i])

        #TODO: Need to add some validation here to check all is ok.
        return True
#-----------------------------------------------------------------------
#
#    S e n s o r   C a l c u l a t i o n   F u n c t i o n s
#
#    Specific functions to read the g forces
#-----------------------------------------------------------------------


    def _read_x_axis_data_registers(self):
        """
        Read the data out from the X Axis data registers 0x01 - msb, 0x02 bits 7 - 4 - lsb
        """
        if self._data_available('x'):
            data_addr = [0x02, 0x01]
            data_l = self.comms.read_data_byte(SENSOR_ADDR,data_addr[0])
            data_h = self.comms.read_data_byte(SENSOR_ADDR,data_addr[1])
            self.log.debug("[Rs2] X Axis Data Register values (%x/%x):%x / %x" % (data_addr[0], data_addr[1], data_h, data_l))
            data_out = (data_h << 4) + (data_l >> 4)
            self.log.info("[Rs2] X Axis Data Register combined %x" % data_out)
        else:
            data_out = 0x7ff
        return data_out

    def _read_y_axis_data_registers(self):
        """
        Read the data out from the Y Axis data registers 0x03 - msb, 0x04 bits 7 - 4 - lsb
        """
        if self._data_available('y'):
            data_addr = [0x04, 0x03]
            data_l = self.comms.read_data_byte(SENSOR_ADDR,data_addr[0])
            data_h = self.comms.read_data_byte(SENSOR_ADDR,data_addr[1])
            self.log.debug("[Rs2] Y Axis Data Register values (%x/%x):%x / %x" % (data_addr[0], data_addr[1], data_h, data_l))
            data_out = (data_h << 4) + (data_l >> 4)
            self.log.info("[Rs2] Y Axis Data Register combined %x" % data_out)
        else:
            data_out = 0x7ff
        return data_out

    def _read_z_axis_data_registers(self):
        """
        Read the data out from the Z Axis data registers 0x05 - msb, 0x06 bits 7 - 4 - lsb
        """
        if self._data_available('z'):
            data_addr = [0x06, 0x05]
            data_l = self.comms.read_data_byte(SENSOR_ADDR,data_addr[0])
            data_h = self.comms.read_data_byte(SENSOR_ADDR,data_addr[1])
            self.log.debug("[Rs2] Z Axis Data Register values (%x/%x):%x / %x" % (data_addr[0], data_addr[1], data_h, data_l))
            data_out = (data_h << 4) + (data_l >> 4)
            self.log.info("[Rs2] Z Axis Data Register combined %x" % data_out)
        else:
            data_out = 0x7ff
        return data_out

    def _fsr_multiplier(self):
        """
        Given the value from calibration data for the full scale range, calculate the mutiplier
        The multipler is used to scale the readings from the sensor axis'
        """
        #TODO: Change these number to static variables
        if self.calibration_data['full_scale_range'] == 2:
            fsr_multiplier = 1/1024
        elif self.calibration_data['full_scale_range'] == 4:
            fsr_multiplier = 1/512
        elif self.calibration_data['full_scale_range'] == 8:
            fsr_multiplier = 1/256
        else:
            # default if calibration data incorrect.
            fsr_multiplier = 1/1024
            self.log.warning("[Rs2] Calibration data for Full Scale Range was invalid, using default of 8g")
        self.log.info("[Rs2] Full Scale Range Multiplier is:%f" % fsr_multiplier)
        return fsr_multiplier

    def _calculate_values(self):
        """
        Takes the readings and returns the x, y, z values
        Given the current Full Scale Range multipler
        """
        x = self._read_x_axis_data_registers()
        y = self._read_y_axis_data_registers()
        z = self._read_z_axis_data_registers()

        fsr = self._fsr_multiplier()
        x = self._twos_compliment12(x)
        self.log.debug("[Rs2] 2's Compliment of X axis:%f" % x)
        x = x * fsr
        y = self._twos_compliment12(y)
        self.log.debug("[Rs2] 2's Compliment of Y axis:%f" % y)
        y = y * fsr
        z = self._twos_compliment12(z)
        self.log.debug("[Rs2] 2's Compliment of Z axis:%f" % z)
        z = z * fsr
        self.log.info("[Rs2] Calculated values of the x,y,z axis: %f : %f : %f" % (x,y,z))
        return [x, y, z]

    def _calculate_avg_values(self):
        """
        Takes 10 sets of readings and returns the averaged x, y, z values
        Given the current Full Scale Range multipler
        """
        avg_x = 0
        avg_y = 0
        avg_z = 0
        fsr = self._fsr_multiplier()
        qty_read = self.calibration_data['average_quantity']
        if qty_read < AVG_QTY_MIN or qty_read > AVG_QTY_MAX:
            self.log.warning("[Rs2] Calibration Data for the number of readings is invalid, using default of 10")
            qty_read = AVG_QTY_DEFAULT

        for n in range(0,qty_read):
            x = self._read_x_axis_data_registers()
            y = self._read_y_axis_data_registers()
            z = self._read_z_axis_data_registers()
            x = self._twos_compliment12(x)
            x = x * fsr
            y = self._twos_compliment12(y)
            y = y * fsr
            z = self._twos_compliment12(z)
            z = z * fsr
            avg_x = avg_x + x
            avg_y = avg_y + y
            avg_z = avg_z + z

        avg_x = avg_x / qty_read
        avg_y = avg_y / qty_read
        avg_z = avg_z / qty_read

        return [avg_x, avg_y, avg_z]


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

        self._turn_off_sensor()

        self._set_full_scale_mode()

        self._set_fifo_disabled()

        self._set_power_mode()      # Uses calibration data to determine mode of operation

        self._set_offset_registers()

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

    def _read_value(self):
        """
        Modify this function to return the value read from the sensor
        If no value is available, return zero or a default value
        """
        if self.calibration_data['single_mode'] == True:
            value = self._calculate_values()
        else:
            value = self._calculate_avg_values()
        # Below: No need to return value as a list ([value]) as it is already a list from the calculate functions
        return value

    def _stop(self):
        """
        Set the operation mode bits (5-7) of Command Register 1 to zero
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

    def _twos_compliment12(self,value):
        """
        Convert the given 12bit hex value to decimal using 2's compliment
        """
        return -(value & 0b100000000000) | (value & 0b011111111111)

    def _create_2s_c12(self,value):
        """
        Given the value, return a binary representation in 2's c for it
        """
        twos_c = 0
        if value < 0:
            twos_c = 0b100000000000 | (value & 0b011111111111)
        else:
            twos_c = (value & 0b011111111111)
        return twos_c

    def _software_reset():
        """
        Perform a Software Reset using CTRL_Register 0x2b
        After the software reset, it automatically clears the bit so no need to check / merge
        """
        reg_addr = 0x0e
        value = 0b01000000
        byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
        self.log.info ("[Rs2] Control Register 2 before enabling Software Reset (%x):%x" % (reg_addr,byte))
        # Modify the register to set bit 6 to 0b1
        towrite = byte | value
        self.log.debug("[Rs2] Byte to write to perform Software Reset %x" % towrite)
        self.comms.write_data_byte(SENSOR_ADDR, reg_addr, towrite)
        time.sleep(0.5)
        in_st = 1
        while in_st:
            # Wait while the Software Reset runs
            byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
            self.log.info ("[Rs2] Control Register 2 After enabling Software Reset:%x" % byte)
            in_st = (byte & 0b01000000) >> 6
            if in_st == 0b1:
                print("Sensor In Software Reset")
        print ("Software Reset Completed")
        self.log.debug("[Rs2] Software Reset Completed")
        return


def SetSelfTest(onoff):
    # To activate the self-test by setting the ST bit in the CTRL_REG2 register (0x2B).
    # Enable the Self Test using CTRL_Register 0x2b
    reg_addr = 0x2b
    mask = 0b10000000
    shift = 7
    byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
    self.log.info ("[Rs2] Self Test byte before setting Self Test bit (%x):%x" % (reg_addr,byte))
    if (byte & mask) != (onoff << shift):
        # Modify the register to set bit 7 to on or off
        towrite = (byte & ~mask) | (onoff << shift)
        self.log.debug("[Rs2] Self Test Byte to write to turn on the Self Test %x" % towrite)
        self.comms.write_data_byte(SENSOR_ADDR, reg_addr, towrite)
        time.sleep(WAITTIME)
        byte = self.comms.read_data_byte(SENSOR_ADDR,reg_addr)
        self.log.info ("[Rs2] Self Test After turning on the required mode:%x" % byte)
        if (byte & mask) == (onoff << shift):
            self.log.info("[Rs2] Sensor Turned in to required Self Test mode")
        else:
            self.log.info("[Rs2] Sensor Not in the required Self Test mode")
    else:
        self.log.info("[Rs2] Sensor already in required Self Test mode")
    return

def SelfTest():
    """
    Run the self test routine and capture the results. Steps required
    Set the sensor in Standby by clearing the ACTIVE bit in CTRL_REG1 register (0x2A)
    Set the Full Scale mode to 2g
    Set the sensor into Self Test by setting the ST bit in CTRL_REG2 (0x2B)
    Set the Sensor back into ACTIVE mode by setting the ACTIVE bit in CTRL_REG1 register (0x2A)
    Measure the values from the 3 axis (take multiple samples)
    Set the sensor in Standby by clearing the ACTIVE bit in CTRL_REG1 register (0x2A)
    End the Self Test by clearing the ST bit in CTRL_REG2 (0x2B)
    Set the Sensor back into ACTIVE mode by setting the ACTIVE bit in CTRL_REG1 register (0x2A)
    Measure the values from the 3 axis (take multiple samples)

    Then simply compute the difference between the acceleration output of all axes with self-test enabled
    (ST = 1) and disabled (ST = 0) as follows:

    XST = XST_ON − XST_OFF
    YST = YST_ON − YST_OFF
    ZST = ZST_ON − ZST_OFF

    The difference is based on a full scale mode of 2g although the values are not calculated
    range   x       y       z
    2g      +90     +104    +782

    """
    # Need to get the full scale mode for later use
    fullscalerange = ReadFullScaleMode()
    SetFullScaleMode(TWOG)

    SetSystemMode(STANDBY)
    SetSelfTest(False)
    SetSystemMode(ACTIVE)
    print ("Capturing Values")
    out_selftest = CalculateAvgValues(fullscalerange)
    print ("Set into STANDBY mode")
    SetSystemMode(STANDBY)
    print ("Enable Self Test mode")
    SetSelfTest(True)
    print ("Set into ACTIVE mode")
    SetSystemMode(ACTIVE)
    print ("Capturing Values")
    in_selftest = CalculateAvgValues(fullscalerange)
    print ("Set into STANDBY mode")
    SetSystemMode(STANDBY)
    print ("DISable Self Test mode")
    SetSelfTest(False)

    print("\nValues Before / During Self Test (Non Calibrated Values)")
    print(" Y |             :%f / %f" % (out_selftest[1],in_selftest[1]))
    print("   |")
    print("   |   Z         :%f / %f" % (out_selftest[2],in_selftest[2]))
    print("   |  / ")
    print("   | /")
    print("   |_________ X  :%f / %f" % (out_selftest[0],in_selftest[0]))
    print("\n")

    # Check for Self Test Pass
    # X increase of 90, y increase of 104, z increase of 782 (these are non calibrated!)

    #BUG: I have changed the calculateavgvalues to make them calibrated!!
    if (in_selftest[0] - out_selftest[0]) > (90 * 0.75):
        print("X - PASS")
    else:
        print("X - FAIL")
    if (in_selftest[1] - out_selftest[1]) > (104 * 0.75):
        print("Y - PASS")
    else:
        print("Y - FAIL")
    if (in_selftest[2] - out_selftest[2]) > (782 * 0.75):
        print("Z - PASS")
    else:
        print("Z - FAIL")

    return




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




