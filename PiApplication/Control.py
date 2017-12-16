#!/usr/bin/env python3
"""
Bostin Technology  (see www.BostinTechnology.com)

For use with the CognIoT Sensors and uses the Android Application to read values

Command Line Options
    - Start Capturing Readings (default action)     -s --start
    - Display Calibration                           -c --displaycal
    - Set Calibration                               -e --setcal
    - Display Customer Parameters                   -o --displayinfo
    - Set Customer Parameters                       -a --setinfo
    - Reset                                         -t --reset

Customer Info (cust_info)
['username'] - The name used to log into the system
['password'] - the associated password
['device'] - The Unique number for the device - generated from the iCog EEPROM UUID
['sensor'] - The customers sensor number
['acroynm'] - The customers acroyn for the sensor
['description'] = the full description for the sensor
['database'] - the destination for the data, local, remote or AWS
['db_addr'] - address of the database APi
['db_port'] - the port of the database APi
"""
#BUG: Whilst setting calibration
"""
Light Mode
IR - Infrared Mode  -  ALS - Ambient Light Sensing Mode
DO you want the sensor to work in IR or ALS mode? (i/a)?a
Full Scale Range
0 = 1,000LUX, 1 = 4000LUX, 2=16,000LUX, 3=64,000LUX
Which Full Scale value is required? (0,1,2,3)?3
ADC Resolution
0 = 16bit ADC, 1 = 12bit ADC, 2 = 8bit ADC, 3=4bit ADC
Which ADC Resolution value is required? (0,1,2,3)?0
Traceback (most recent call last):
  File "./Control.py", line 696, in <module>
    main()
  File "./Control.py", line 671, in main
    SetCal()
  File "./Control.py", line 421, in SetCal
    calib = icog.SetCalibration()
  File "/home/pi/Projects/pineapple/PiApplication/i_cog_Ls_1.py", line 119, in SetCalibration
    calib = self._build_calib_data()
  File "/home/pi/Projects/pineapple/PiApplication/i_cog_Ls_1.py", line 283, in _build_calib_data
    data[0][1] = ((self.calibration_data['read_frequency']* 10) & 0xff0000) >> 16
TypeError: unsupported operand type(s) for &: 'float' and 'int'
"""

#TODO: Review the use of warning, critical and exception. On an error, it is dumping all the exception
     #   data to screen, only wany critical user messages there.

#TODO: Consider having a calibration flag to indicate that calibration data has been set. When I first use a sensor
     #   it is not configured and can have literally any settings.

#TODO: After pressing CTRL-C, it goes into the keyboard interrupt but then fails to log anything outside of the
     #   interrupt routine so i have no idea if it has turned the sensor off even though the loogin works at other times.

#TODO: Make running the program easier, a single command would be great.

#TODO: I need to go through all the code and check for failure points and protect against them

#TODO: Go through and check for where I just return True that it is correct.
     #   Need to validate the failure routes of the code.

#TODO: In the icog routines there are sys.exits which I think should probably return to the main program instead as a fail

#TODO: When it started after being disconnected, the data was not sent to DBRemote.

#BUG: The sensor value is to be based on tehe UUID of the iCog, not user entered.

from datetime import datetime
from datetime import timedelta

import time
import argparse
import sys
import logging
import logging.config
import importlib
import inspect
import os
import os.path
import json

from cls_DataAccessor import DataAccessor
import cls_EEPROM
import Standard_Settings as SS
from cls_comms import i2c_comms
from cls_comms import SPi_comms
from cls_comms import Serial_comms
import dict_LoggingSetup

# Note: The required iCog is imported in the code once it has been determined


# The following global variables are used.
gbl_log = ""


#BUG: With no calibration data set, I have a read frequency of zero.
#       Do I need to add a flag in the Id_IoT to indicate that calibration data is set?
#       If not set, I could then program defaults.

def GetSerialNumber():
    """
    Get the System Serial number to be used as the Device ID
    returns the Serial Number or '0000000000000000'
    """
    gbl_log.debug("[CTRL] Opening proc/cpuinfo for CPU serial Number")
    cpuserial = '0000000000000000'
    with open('/proc/cpuinfo') as f:
        for line in f:
            if line[0:6] == "Serial":
                cpuserial = line[10:26]
    gbl_log.info("[CTRL] CPU Serial Number : %s" % cpuserial)
    return int(cpuserial, 16)

def GetSerialNumber_old():
    """
    Get the System Serial number to be used as the Device ID
    returns the Serial Number or '0000000000000000'
    """
    try:
        gbl_log.debug("[CTRL] Opening proc/cpuinfo for CPU serial Number")
        f = open('/proc/cpuinfo')
        for line in f:
            if line[0:6] == "Serial":
                cpuserial = line[10:26]
        f.close
    except:
        cpuserial = '0000000000000000'
        gbl_log.error("[CTRL] Failed to open proc / cpuinfo, set to default")

    gbl_log.info("[CTRL] CPU Serial Number : %s" % cpuserial)
    return int(cpuserial, 16)

def GenerateTimeStamp():
    """
    Generate a timestamp in the correct format
    dd-mm-yyyy hh:mm:ss.sss
    datetime returns a object so it needs to be converted to a string and then redeuced to 23 characters to meet format
    """
    now = str(datetime.now())
    gbl_log.debug("[CTRL] Generated a timestamp %s" % now[:23])
    return now[:23]

def SetupLogging():
    """
    Setup the logging defaults
    Using the logger function to span multiple files.
    """
    global gbl_log
    # Create a logger with the name of the function
    logging.config.dictConfig(dict_LoggingSetup.log_cfg)
    gbl_log = logging.getLogger()

    gbl_log.info("\n\n")
    gbl_log.info("[CTRL] Logging Started, current level is %s" % gbl_log.getEffectiveLevel())

    return

def CheckDiskSpace():
    """
    Validate there is enough disk space to write to file

    """
    st = os.statvfs(".")
    du = st.f_bavail * st.f_frsize  # number of blocks multiplied by block size
    gbl_log.debug("[CTRL] Space available %s" % du)
    if du < SS.MIN_DISK_SPACE:
        print ('Insufficient Disk Space, capture aborted')
        return False
    return True

################################################################################
#
# The following functions are the client interaction functions
#
################################################################################

def SetandGetArguments():
    """
    Define the arguments available for the program and return any arguments set.

    """

    gbl_log.info("[CTRL] Setting and Getting Parser arguments")
    parser = argparse.ArgumentParser(description="Capture and send data for CognIoT sensors")
    parser.add_argument("-s", "--start", action="store_true",
                    help="Start capturing data from the configured sensors and store them in the data files directory")
    parser.add_argument("-r", "--reset", action="store_true",
                    help="Reset to the default values")
    parser.add_argument("-t", "--transmit", action="store_true",
                    help="Start Transmitting data to the database")
    Cal_group = parser.add_mutually_exclusive_group()
    Cal_group.add_argument("-c", "--displaycal", action="store_true",
                    help="Display the Calibration Data for the sensors, e.g. Read Frequency")
    Cal_group.add_argument("-a", "--setcal", action="store_true",
                    help="Set new Calibration Data for the sensors, e.g. Read Frequency")
    Para_group = parser.add_mutually_exclusive_group()
    Para_group.add_argument("-i", "--displayinfo", action="store_true",
                    help="Display the Customer Information, e.g. Customer Name")
    Para_group.add_argument("-f", "--setinfo", action="store_true",
                    help="Set the Operational parameters, e.g. Customer Name")

    gbl_log.debug("[CTRL] Parser values captured: %s" % parser.parse_args())
    return parser.parse_args()

def SetupSensor():
    """
    This function performs the following
    - Connect to the ID_IoT chip and retive all the infromation
    - load the correct icog file
    - Transfer the configuration information into the loaded icog
    - set the global variable icog to the required icog
    returns the instance of the icog and the eeprom
    """

    # Load the data from the EEPROM on the ID-Iot chip
    i2c_connection = i2c_comms()
    eeprom = cls_EEPROM.ID_IoT(i2c_connection)

    # Load the correct sensor file
    icog_file = eeprom.ReturnSensorCommsFile()
    gbl_log.info("[CTRL] Loading the iCog Comms file:%s" % icog_file)

    try:
        # This doesn't initialise the iCog, just loads it
        imported_icog = importlib.import_module(icog_file)
    except:
        gbl_log.critical("[CTRL] Importing of the iCog file:%s failed, contact support" % icog_file)
        gbl_log.exception("[CTRL] Start Routine Exception Data")
        sys.exit()
    gbl_log.info("[CTRL] Loading of the iCog file:%s succeeded (%s)" % (icog_file,imported_icog))

    # Open the right bus connection to work with the icog connected
    reqd_bus = eeprom.ReturnBusType()
    if reqd_bus == SS.SPI:
        icog_connection = SPi_comms()
    elif reqd_bus == SS.SERIAL:
        icog_connection = Serial_Comms()
    elif reqd_bus == SS.I2C:
        icog_connection = i2c_connection
    else:
        gbl_log.critical("[CTRL] Required Connection bus:%s is not supported, contact Support" % reqd_bus)
        sys.exit()
    gbl_log.info("[CTRL] Required Connection bus:%s loaded" % icog_connection)

    # Retrieve Calibration Data and pass it to the iCog
    calib_data = eeprom.ReturnCalibrationData()

    gbl_log.debug("[CTRL] calibration data being passed into iCog:%s" % calib_data)
    # Initialise the iCog
    icog = imported_icog.iCog(icog_connection, calib_data)
    gbl_log.debug("[CTRL] Initialised icog:%s" % icog)

    return (icog, eeprom)

def Start(cust_info):
    """
    Perform the reading of and sending data to the AWS database
    This is the default action if no arguments are passed to the system.

    Order of the routine


    3. Open data accessor link
    4. in loop
        read value
        post
    """

    (icog, eeprom) = SetupSensor()

    # Sit in a loop reading the values back and writing them to the data connection
    # values available from the i_cog
    #   StartSensor, EndReadings, ReadValue, ReturnReadFrequency
    # put it all in a try loop to use CTRL-C to cancel
    print("Reading Values from sensor\n")
    print("CTRL-C to cancel")

    DataAcc = DataAccessor(cust_info['username'], cust_info['password'],
                    cust_info['database'], cust_info['db_addr'], cust_info['db_port'],
                    cust_info["device"], cust_info["sensor"], cust_info["acroynm"], cust_info["description"])
    read_freq = icog.ReturnReadFrequency()

    gbl_log.debug("[CTRL] Read Frequency:%s" % read_freq)
    try:
        icog.StartSensor()
        while True:
            # Start the timer
            endtime = datetime.now() + timedelta(seconds=read_freq)
            print("\r\r\r\r\r\r\rReading", end="")

            #Read the value
            reading = icog.ReadValue()

            gbl_log.info("[CTRL] Value Read back from the sensor:%s" % reading)

            DataAcc.DataIn(reading)


            # Wait for timeout
            waiting = False
            while endtime > datetime.now():
                if waiting == False:
                    print("\r\r\r\r\r\r\rWaiting(last reading:%s)" % reading, end="")
                    gbl_log.debug("[CTRL] Waiting for timeout to complete")
                    waiting=True
                # Use time.sleep to wait without processor burn at 25%
                sleep = datetime.now() - endtime
                if sleep.total_seconds() > 2:
                    time.sleep(sleep.total_seconds() - 0.1)
                else:
                    time.sleep(0.1)

    except KeyboardInterrupt:
        # CTRL - C entered
        print(" CTRL-C entered")
        gbl_log.debug("[CTRL] User Interrupt occurred (Ctrl-C)")
        icog.EndReadings()
        gbl_log.info("[CTRL] End of Processing")

        #TODO: Need to add in some functionality here to stop the sensor.
    except:
        #Error occurrred
        gbl_log.critical("[CTRL] Error occurred whilst looping to read values")
        print("\nCRITICAL ERROR during rading of sensor values- contact Support\n")
        gbl_log.exception("[CTRL] Start reading loop Exception Data")

    #TODO: Do I add a finally clause here to close off the comms, regardless of the failure?

    return

def TransmitData(cust_info):
    """
    Perform the transmitting of the data to the database

    Order of the routine


    3. Open data accessor link
    4. in loop
        read value
        post
    """

    # Sit in a loop transmitting dat to the data connection
    print("Transmitting Values to the database\n")
    print("CTRL-C to cancel")

    DataAcc = DataAccessor(cust_info['username'], cust_info['password'],
                    cust_info['database'], cust_info['db_addr'], cust_info['db_port'],
                    cust_info["device"], cust_info["sensor"], cust_info["acroynm"], cust_info["description"])

    try:
        while True:
            # Start the timer
            endtime = datetime.now() + timedelta(seconds=SS.TRANSMIT_FREQ)
            print("\r\r\r\r\r\r\rReading", end="")

            DataAcc.TransmitData()

            # Wait for timeout
            waiting = False
            while endtime > datetime.now():
                if waiting == False:
                    print("\r\r\r\r\r\r\rWaiting", end="")
                    gbl_log.debug("[CTRL] Waiting for timeout to complete")
                    waiting=True
                # Use time.sleep to wait without processor burn at 25%
                sleep = datetime.now() - endtime
                if sleep.total_seconds() > 2:
                    time.sleep(sleep.total_seconds() - 0.1)
                else:
                    time.sleep(0.1)

    except KeyboardInterrupt:
        # CTRL - C entered
        print(" CTRL-C entered")
        gbl_log.debug("[CTRL] User Interrupt occurred (Ctrl-C)")
        gbl_log.info("[CTRL] End of Processing")

    except:
        #Error occurrred
        gbl_log.critical("[CTRL] Error occurred whilst looping to read values")
        print("\nCRITICAL ERROR during rading of sensor values- contact Support\n")
        gbl_log.exception("[CTRL] Start reading loop Exception Data")

    return

def Reset():
    """
    Reset the program back to using the default values
    Clear any cached sensor data

    setup i2c comms
    provide menu to reset the Id-IoT
    using the iCog to reset the config and get the data values.
    reset all the configuration data back to original
    """
    check = input("Are you sure you want to reset back to default values (y/n)?")
    gbl_log.info("[CTRL] Reset of program back to default values response:%s" % check)
    if check.upper() == "Y":
        (icog, eeprom) = SetupSensor()
        calib = icog.ResetCalibration()
        eeprom.ResetCalibrationData(calib)
        gbl_log.debug("[CTRL] Sensor Calibration Data reset")
        print("Calibration Data reset to default values")

    filename = SS.CUSTFILE_LOCATION + '/' + SS.CUSTFILE_NAME
    if os.path.isfile(filename):
        os.remove(filename)
        gbl_log.debug("[CTRL] Customer File in location deleted:%s" % filename)
        print("Customer data removed, will need to be re-entered on next startup")

    return

def DisplayCal():
    """
    Perform the necessary actions to display the Calibration data being used

    """
    #BUG: calib_data is not set as the icog is not instantiated unless Start called
    # Need to add a check to see if Setup has alread been run and therefore doesn't need to be rerun
    # Put this check in SetupSensor()

    (icog, eeprom) = SetupSensor()
    calib_data = icog.ReturnCalibrationData()
    print("Setting                  Value")
    print("==============================")
    for item in calib_data:
        print("%s%s" %( '{0: <25}'.format(item), calib_data[item]))

    return

def SetCal():
    """
    Perform the necessary actions to set the Calibration data being used
    Call the icog SetCalibration routine which returns the calibration data
    Write the calibration data to the ID_IoT
    """
    gbl_log.info("[CTRL] Setting the Calibration")
    (icog, eeprom) = SetupSensor()
    calib = icog.SetCalibration()
    if len(calib) > 1:
        # data returned, so nothing to write
        eeprom.ResetCalibrationData(calib)

        print("Calibration Data Set")
        gbl_log.info("[CTRL] Calibration data set")
    else:
        print("No change to the calibration data")
        gbl_log.info("[CTRL] No change to the Calibration")

    return

def DisplayCustomerParameters(cust_info):
    """
    Perform the necessary actions to display the customer information being used

    """
    print("Setting                  Value")
    print("==============================")
    for item in cust_info:
        print("%s%s" %( '{0: <25}'.format(item), cust_info[item]))

    return

def SetCustomerParameters(device):
    """
    Perform the necessary actions to allow the clinet to set the parameter data being used

    Parameters to be captured
    - Sensor Acroynm
    - Sensor Description
    - local or remote database

    Will need to use SaveCustomerInfo
    """

    (icog, eeprom) = SetupSensor()

    print("Setting Customer Information\n")
    cust_info = {}
    cust_info['device'] = device
    gbl_log.debug("[CTRL] Device Number:%s" % device)
    cust_info['sensor'] = eeprom.ReturnUUID()
    gbl_log.debug("[CTRL] Sensor UUID Number:%s" % cust_info['sensor'])

    choice = ""
    while choice == "":
        choice = input("Is the Pi operating with a (l)ocal, remote over Lo(r)a, remote over (W)ifi or (A)WS database (l, r, w or a)?")
        if choice.upper() == "L":
            cust_info['database'] = SS.DB_LOCAL
        elif  choice.upper() == "A":
            cust_info['database'] = SS.DB_AWS
        elif  choice.upper() == "R":
            cust_info['database'] = SS.DB_LORA
        elif  choice.upper() == "W":
            cust_info['database'] = SS.DB_WIFI
        else:
            print("Please enter either 'l' for local or 'a' for Amazon AWS")
            choice = ""
    gbl_log.debug("[CTRL] Database Location:%s" % choice)

    if cust_info['database'] == SS.DB_WIFI:
        # Remote database details need to be captured, either LoRa or Wifi
        choice = ""
        while choice == "":
            choice = input("Please enter the remote database address (IP addr or hostname)?")
            cust_info['db_addr'] = choice
        gbl_log.debug("[CTRL] Remote database Address:%s" % choice)

        choice = ""
        while choice == "":
            choice = input("Please enter the remote database port number (Enter for default 8080)?")
            if choice == "":
                choice = "8080"
                cust_info['db_port'] = SS.DB_REMOTE_PORT
            elif choice.isdigit():
                cust_info['db_port'] = choice
            else:
                print("PLease enter a number for the port number")
                choice = ""
        gbl_log.debug("[CTRL] Remote database Port:%s" % choice)

    elif cust_info['database'] == SS.DB_AWS:
        # If the database is AWS, set the address to AWS and default port
        cust_info['db_addr'] = SS.DB_AWS_ADDR
        cust_info['db_port'] = SS.DB_AWS_PORT

    elif cust_info['database'] == SS.DB_LOCAL:
        # If the database local, set the address to localhost and default port
        cust_info['db_addr'] = SS.DB_LOCAL_ADDR
        cust_info['db_port'] = SS.DB_LOCAL_PORT

    elif cust_info['database'] == SS.DB_LORA:
        # If the database local, set the address to localhost and default port
        cust_info['db_addr'] = SS.DB_LORA_ADDR
        cust_info['db_port'] = SS.DB_LORA_PORT

    else:
        # Set a default, just in case
        cust_info['db_addr'] = SS.DB_LOCAL_ADDR
        cust_info['db_port'] = SS.DB_LOCAL_PORT

    if cust_info['database'] != SS.DB_LORA:
        choice = ""
        while choice == "":
            choice = input("Please enter your Customer Name?")
            if len(choice) > 0:
                print("Customer Name entered:%s" % choice)
                print("NOTE: This is case sensitive")
                confirm = input ("Are you sure? (y/n)")
                if confirm.upper() == "Y":
                    cust_info['username'] = choice
                else:
                    choice = ""
        gbl_log.debug("[CTRL] Customer UserName:%s" % choice)

        choice = ""
        while choice == "":
            choice = input("Please enter your customer Password?")
            if len(choice) > 0:
                print("Customer Password entered:%s" % choice)
                print("NOTE: This is case sensitive")
                confirm = input ("Are you sure? (y/n)")
                if confirm.upper() == "Y":
                    cust_info['password'] = choice
                else:
                    choice = ""
        gbl_log.debug("[CTRL] Customer Password:%s" % choice)
    else:
        cust_info['username'] = 'DEFAULT'
        cust_info['password'] = 'default'

    choice = ""
    while choice == "":
        choice = input("Please enter your Sensor Acroynm?")
        if len(choice) > 0 and len(choice) <= SS.MAX_ACROYNM_LENGTH:
            cust_info['acroynm'] = choice
        else:
            print("Please enter a acroynm for the sensor (max 10 characters")
            choice = ""
    gbl_log.debug("[CTRL] Sensor Acroynm:%s" % choice)

    choice = ""
    while choice == "":
        choice = input("Please enter your Sensor Description?")
        if len(choice) > 0 and len(choice) <= SS.MAX_DESCRIPTION_LENGTH:
            cust_info['description'] = choice
        else:
            print("Please enter a description for the sensor (max 100 characters)")
            choice = ""
    gbl_log.debug("[CTRL] Sensor Description:%s" % choice)



    SaveCustomerInfo(cust_info)

    #TODO: Add in setting of the sensor info at this stage?
    return cust_info

def SplashScreen():
    print("***********************************************")
    print("*             Bostin Technology               *")
    print("*                                             *")
    print("*             Mobile IoT Sensor               *")
    print("*                                             *")
    print("*        for more info www.cognIoT.eu         *")
    print("***********************************************\n")
    return

def LoadCustomerInfo(dev):
    """
    Load the Customer File information and return it in a dictionary
    customer_info = {"username": customer, "password": password, "device" : UUID, "sensor" : 1, "acroynm" : "LghtSns1", "description" : "Light Sensor in the Office"}

    """
    custfile = {}
    gbl_log.info("[CTRL] Reading the customer file information")
    filename = SS.CUSTFILE_LOCATION + '/' + SS.CUSTFILE_NAME
    if os.path.isfile(filename):
        gbl_log.debug("[CTRL] Customer File in location:%s" % filename)
        with open(filename, mode='r') as cust:
            custfile = json.load(cust)

    else:
        print("No existing customer file, please Set customer info")
        gbl_log.info("[CTRL] No Customer file exisitng")

    custfile['device'] = dev        #device_id is set by the UUID of the Pi

    # Validate the customer info that has been read back.
    status = True
    for item in ['username', 'password', 'device', 'sensor', 'acroynm', 'description', 'database', 'db_addr', 'db_port']:
        if item not in custfile:
            status = False
            gbl_log.info("[CTRL] Missing item from the customer file:%s" % item)

    gbl_log.debug("[CTRL] customer data being returned:%s" % custfile)
    return status, custfile

def SaveCustomerInfo(cust_info):
    """
    Take the cust_info and write it to the file
    Disk management is handled as part of the Control module
    """

    gbl_log.debug("[CTRL] Data being written to the customer file:%s" % cust_info)
    with open(SS.CUSTFILE_LOCATION + '/' + SS.CUSTFILE_NAME, mode='w') as f:
        json.dump(cust_info, f)
        gbl_log.info("[DAcc] Customer File udpated")

    return

################################################################################
#
# The following function is main - the entry point
#
################################################################################

def main():
    """
    This routine is the main called routine and therefore determines what action to take based on the arguments given.

    """

    SplashScreen()

    SetupLogging()

    args = SetandGetArguments()

    # First print a 'splash screen'
    device_id = GetSerialNumber()
    print("\nDevice ID: %s" % device_id)        # TODO: This should probably get the info from cutomer info
    print("\nTo Exit, CTRL-c\n\n")

    #TODO: print out the values being used, especially if they are the defaults.

    #TODO: probably needs something to bomb out if there is a failure

    if CheckDiskSpace() == False:
        gbl_log.critical("[CTRL] Insufficient disk space, unable to start")
        print("\nCRITICAL ERROR Insufficient disk space, unable to start application\n")

    status, customer_info = LoadCustomerInfo(device_id)
    if status != True:
        print("Customer Infomation is missing or incomplete, please re-enter")
        customer_info = SetCustomerParameters(device_id)

    # Note: The default is Start, hence it is the else clause
    if args.start:
        Start(customer_info)
    elif args.reset:
        Reset()
    elif args.displaycal:
        DisplayCal()
    elif args.setcal:
        SetCal()
        DisplayCal()
    elif args.displayinfo:
        DisplayCustomerParameters(customer_info)
    elif args.setinfo:
        SetCustomerParameters(device_id)
    elif args.transmit:
        TransmitData(customer_info)
    else:
        Start(customer_info)



#-----------------------------------------------------------------------
#
#    T E S T   M O D U L E S
#
#-----------------------------------------------------------------------




# Only call the Start routine if the module is being called directly, else it is handled by the calling program
if __name__ == "__main__":

    main()

